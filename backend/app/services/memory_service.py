"""Сервис работы с памятью (Redis + ChromaDB)"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis
import chromadb
from chromadb.config import Settings as ChromaSettings
import json

from app.models.base import Memory, MemoryType
from app.core.config import settings


class MemoryService:
    """Сервис управления памятью"""
    
    def __init__(self):
        # Redis для кэша и сессий
        self.redis = redis.from_url(settings.REDIS_URL)
        
        # ChromaDB для векторного поиска
        self.chroma_client = chromadb.Client(
            ChromaSettings(
                chroma_server_host=settings.CHROMA_HOST,
                chroma_server_http_port=settings.CHROMA_PORT,
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False
            )
        )
        self.memories_collection = self.chroma_client.get_or_create_collection(
            name="personal_memories",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def store_memory(self, memory: Memory) -> str:
        """Сохранить воспоминание в ChromaDB и Redis"""
        
        # Сохранение в ChromaDB (для векторного поиска)
        if memory.embedding:
            self.memories_collection.add(
                ids=[memory.id],
                embeddings=[memory.embedding],
                metadatas=[{
                    "user_id": memory.user_id,
                    "type": memory.memory_type.value,
                    "importance": memory.importance,
                    "source": memory.source,
                    "created_at": memory.created_at.isoformat()
                }],
                documents=[memory.content]
            )
        
        # Сохранение в Redis
        key = f"memory:{memory.id}"
        await self.redis.setex(
            key,
            86400 * 30,  # 30 дней
            json.dumps(memory.model_dump())
        )
        
        # Добавление в индекс пользователя
        user_index_key = f"user_memories:{memory.user_id}"
        await self.redis.sadd(user_index_key, memory.id)
        
        return memory.id
    
    async def search_memories(
        self,
        user_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None
    ) -> List[Memory]:
        """Поиск воспоминаний по эмбеддингу"""
        
        where_clause = {"user_id": {"$eq": user_id}}
        if memory_type:
            where_clause["type"] = {"$eq": memory_type.value}
        
        results = self.memories_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        
        memories = []
        if results and results.get("ids"):
            for memory_id in results["ids"][0]:
                key = f"memory:{memory_id}"
                data = await self.redis.get(key)
                if data:
                    memory_dict = json.loads(data)
                    memories.append(Memory(**memory_dict))
        
        return memories
    
    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Получить воспоминание по ID"""
        key = f"memory:{memory_id}"
        data = await self.redis.get(key)
        
        if data:
            memory_dict = json.loads(data)
            return Memory(**memory_dict)
        return None
    
    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Удалить воспоминание"""
        
        # Удалить из ChromaDB
        try:
            self.memories_collection.delete(ids=[memory_id])
        except:
            pass
        
        # Удалить из Redis
        key = f"memory:{memory_id}"
        result = await self.redis.delete(key)
        
        # Удалить из индекса пользователя
        user_index_key = f"user_memories:{user_id}"
        await self.redis.srem(user_index_key, memory_id)
        
        return result > 0
    
    async def get_user_memories(self, user_id: str) -> List[Memory]:
        """Получить все воспоминания пользователя"""
        user_index_key = f"user_memories:{user_id}"
        memory_ids = await self.redis.smembers(user_index_key)
        
        memories = []
        for memory_id in memory_ids:
            memory = await self.get_memory(memory_id.decode() if isinstance(memory_id, bytes) else memory_id)
            if memory:
                memories.append(memory)
        
        return sorted(memories, key=lambda m: m.created_at, reverse=True)
    
    async def get_memory_stats(self, user_id: str) -> dict:
        """Статистика памяти пользователя"""
        memories = await self.get_user_memories(user_id)
        
        stats = {
            "total_memories": len(memories),
            "by_type": {},
            "total_importance": 0.0,
            "oldest_memory": None,
            "newest_memory": None
        }
        
        for memory_type in MemoryType:
            count = sum(1 for m in memories if m.memory_type == memory_type)
            if count > 0:
                stats["by_type"][memory_type.value] = count
        
        if memories:
            stats["total_importance"] = sum(m.importance for m in memories)
            stats["oldest_memory"] = memories[-1].created_at.isoformat()
            stats["newest_memory"] = memories[0].created_at.isoformat()
        
        return stats

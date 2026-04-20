import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
import openai

from app.models.base import Memory, MemoryType
from app.core.config import settings


class MemoryAgent:
    """Агент управления памятью с векторным поиском и графом знаний"""
    
    def __init__(self):
        self.client = chromadb.Client(
            ChromaSettings(
                chroma_server_host=settings.CHROMA_HOST,
                chroma_server_http_port=settings.CHROMA_PORT,
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="personal_memories",
            metadata={"hnsw:space": "cosine"}
        )
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Эпизодический буфер (кратковременная память)
        self.episodic_buffer: Dict[str, List[Memory]] = {}
        self.max_buffer_size = settings.MAX_EPISODIC_BUFFER
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Получение эмбеддинга через OpenAI"""
        response = await self.openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def _calculate_importance(self, content: str, source: str = "chat") -> float:
        """Оценка важности контента (0-1)"""
        # Простая эвристика, можно улучшить через LLM
        importance = 0.5
        
        # Личные факты важнее
        personal_indicators = [
            "я ", "мне ", "мой ", "моя ", "мои ",
            "люблю", "ненавижу", "хочу", "нужно", "важно",
            "работаю", "живу", "учусь", "семья", "дети"
        ]
        content_lower = content.lower()
        matches = sum(1 for indicator in personal_indicators if indicator in content_lower)
        importance += min(matches * 0.1, 0.3)
        
        # Документы важнее случайных фраз
        if source == "document":
            importance += 0.2
        
        # Длинные осмысленные сообщения важнее
        if len(content) > 100:
            importance += 0.1
        
        return min(importance, 1.0)
    
    async def store(
        self,
        content: str,
        user_id: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: Optional[float] = None,
        source: str = "chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Сохранение воспоминания"""
        
        # Оценка важности если не указана
        if importance is None:
            importance = self._calculate_importance(content, source)
        
        # Создание эмбеддинга
        embedding = await self._get_embedding(content)
        
        # Создание объекта памяти
        memory = Memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            embedding=embedding,
            source=source,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        # Сохранение в ChromaDB
        self.collection.add(
            ids=[memory.id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "memory_type": memory_type.value,
                "importance": importance,
                "source": source,
                "user_id": user_id,
                "created_at": memory.created_at.isoformat(),
                "access_count": 0
            }]
        )
        
        # Добавление в эпизодический буфер
        if user_id not in self.episodic_buffer:
            self.episodic_buffer[user_id] = []
        self.episodic_buffer[user_id].append(memory)
        
        # Ограничение буфера
        if len(self.episodic_buffer[user_id]) > self.max_buffer_size:
            self._consolidate_buffer(user_id)
        
        return memory
    
    async def recall(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """Поиск релевантных воспоминаний"""
        
        # Получение эмбеддинга запроса
        query_embedding = await self._get_embedding(query)
        
        # Фильтры
        where_filter = {"user_id": user_id}
        if memory_type:
            where_filter["memory_type"] = memory_type.value
        
        # Векторный поиск
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Берём больше для реранкинга
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Формирование результатов с реранкингом
        memories = []
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            # Пропускаем низковажные
            if metadata.get('importance', 0) < min_importance:
                continue
            
            # Расчёт финального скора
            vector_score = 1 - distance  # Косинусное расстояние → сходство
            importance_boost = metadata.get('importance', 0.5) * 0.2
            recency_boost = self._recency_score(metadata.get('created_at')) * 0.1
            
            final_score = vector_score + importance_boost + recency_boost
            
            memory = Memory(
                id=results['ids'][0][i],
                content=doc,
                memory_type=MemoryType(metadata.get('memory_type', 'episodic')),
                importance=metadata.get('importance', 0.5),
                source=metadata.get('source', 'chat'),
                user_id=user_id,
                created_at=datetime.fromisoformat(metadata.get('created_at')),
                access_count=metadata.get('access_count', 0),
                metadata=metadata
            )
            memories.append((memory, final_score))
        
        # Сортировка по скору
        memories.sort(key=lambda x: x[1], reverse=True)
        
        # Обновление статистики доступа
        for memory, _ in memories[:top_k]:
            self._update_access_stats(memory.id)
        
        return [m for m, _ in memories[:top_k]]
    
    def _recency_score(self, created_at_str: Optional[str]) -> float:
        """Оценка свежести воспоминания (0-1)"""
        if not created_at_str:
            return 0.5
        
        try:
            created = datetime.fromisoformat(created_at_str)
            days_ago = (datetime.utcnow() - created).days
            
            # Экспоненциальное затухание
            import math
            return math.exp(-days_ago / 30)  # Половина за месяц
        except:
            return 0.5
    
    def _update_access_stats(self, memory_id: str):
        """Обновление статистики доступа"""
        # Получение текущих метаданных
        result = self.collection.get(ids=[memory_id], include=["metadatas"])
        if result and result['metadatas']:
            metadata = result['metadatas'][0]
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            metadata['last_accessed'] = datetime.utcnow().isoformat()
            
            self.collection.update(
                ids=[memory_id],
                metadatas=[metadata]
            )
    
    def _consolidate_buffer(self, user_id: str):
        """Консолидация эпизодической памяти в долгосрочную"""
        buffer = self.episodic_buffer[user_id]
        if len(buffer) < 5:
            return
        
        # Находим паттерны в буфере (упрощённо)
        # В реальности здесь LLM-анализ для извлечения общих фактов
        old_memories = buffer[:-self.max_buffer_size//2]
        self.episodic_buffer[user_id] = buffer[-self.max_buffer_size//2:]
        
        # Помечаем старые как кандидаты на консолидацию
        for memory in old_memories:
            if memory.importance > settings.MEMORY_CONSOLIDATION_THRESHOLD:
                # Здесь можно создать обобщённое воспоминание
                pass
    
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Статистика памяти пользователя"""
        result = self.collection.get(
            where={"user_id": user_id},
            include=["metadatas"]
        )
        
        if not result or not result['metadatas']:
            return {
                "total_memories": 0,
                "by_type": {},
                "avg_importance": 0,
                "oldest_memory": None,
                "newest_memory": None
            }
        
        memories = result['metadatas']
        types_count = {}
        importances = []
        
        for m in memories:
            m_type = m.get('memory_type', 'unknown')
            types_count[m_type] = types_count.get(m_type, 0) + 1
            importances.append(m.get('importance', 0.5))
        
        dates = [datetime.fromisoformat(m.get('created_at')) for m in memories if m.get('created_at')]
        
        return {
            "total_memories": len(memories),
            "by_type": types_count,
            "avg_importance": sum(importances) / len(importances) if importances else 0,
            "oldest_memory": min(dates).isoformat() if dates else None,
            "newest_memory": max(dates).isoformat() if dates else None
        }
    
    async def delete(self, memory_id: str, user_id: str) -> bool:
        """Удаление воспоминания"""
        try:
            # Проверка владельца
            result = self.collection.get(ids=[memory_id], include=["metadatas"])
            if not result or not result['metadatas']:
                return False
            
            metadata = result['metadatas'][0]
            if metadata.get('user_id') != user_id:
                return False
            
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
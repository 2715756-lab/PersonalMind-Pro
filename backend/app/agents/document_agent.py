import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiofiles
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    JSONLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.models.base import DocumentChunk, MemoryType
from app.agents.memory_agent import MemoryAgent
from app.core.config import settings


class DocumentAgent:
    """Агент обработки документов с RAG"""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.csv': CSVLoader,
        '.json': JSONLoader,
        '.py': TextLoader,
        '.js': TextLoader,
        '.html': TextLoader,
        '.docx': None,  # Требует дополнительных зависимостей
    }
    
    def __init__(self, memory_agent: MemoryAgent):
        self.memory_agent = memory_agent
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.storage_path = Path(settings.LOCAL_STORAGE_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обработка загруженного файла"""
        
        # Генерация уникального ID и пути
        file_hash = hashlib.md5(file_content).hexdigest()[:12]
        ext = Path(filename).suffix.lower()
        safe_filename = f"{file_hash}_{Path(filename).stem}{ext}"
        
        user_dir = self.storage_path / user_id
        user_dir.mkdir(exist_ok=True)
        
        file_path = user_dir / safe_filename
        
        # Сохранение файла
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Определение загрузчика
        loader_class = self.SUPPORTED_EXTENSIONS.get(ext)
        if not loader_class:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
        
        # Загрузка документа
        try:
            loader = loader_class(str(file_path))
            documents = loader.load()
        except Exception as e:
            # Fallback на простой текстовый загрузчик
            documents = [Document(page_content=str(file_content), metadata={"source": filename})]
        
        # Разбиение на чанки
        chunks = self.text_splitter.split_documents(documents)
        
        # Обработка каждого чанка
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_obj = DocumentChunk(
                content=chunk.page_content,
                source_file=str(file_path),
                file_type=ext,
                chunk_index=i,
                total_chunks=len(chunks),
                metadata={
                    "original_file": filename,
                    "chunk_context": chunk.metadata,
                    **(metadata or {})
                },
                user_id=user_id
            )
            
            # Сохранение как воспоминание типа DOCUMENT
            memory = await self.memory_agent.store(
                content=chunk.page_content,
                user_id=user_id,
                memory_type=MemoryType.DOCUMENT,
                importance=0.6,  # Документы важнее обычного чата
                source="document",
                metadata={
                    "file_name": filename,
                    "chunk_index": i,
                    "file_path": str(file_path)
                }
            )
            
            chunk_obj.id = memory.id
            processed_chunks.append(chunk_obj)
        
        # Извлечение ключевых тем для сводки
        summary = await self._generate_summary(processed_chunks)
        
        # Сохранение мета-воспоминания о документе
        await self.memory_agent.store(
            content=f"Загружен документ '{filename}' ({len(chunks)} фрагментов). Сводка: {summary}",
            user_id=user_id,
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
            source="system",
            metadata={"document_summary": True, "file_name": filename}
        )
        
        return {
            "file_id": file_hash,
            "filename": filename,
            "stored_path": str(file_path),
            "chunks_processed": len(chunks),
            "total_chars": sum(len(c.content) for c in processed_chunks),
            "summary": summary,
            "status": "completed"
        }
    
    async def _generate_summary(self, chunks: List[DocumentChunk]) -> str:
        """Генерация краткой сводки документа (упрощённо)"""
        # В реальности здесь LLM для саммаризации
        first_chunks = " ".join([c.content[:200] for c in chunks[:3]])
        return f"Документ содержит {len(chunks)} разделов. Начало: {first_chunks[:100]}..."
    
    async def search_in_documents(
        self,
        query: str,
        user_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Поиск по документам пользователя"""
        memories = await self.memory_agent.recall(
            query=query,
            user_id=user_id,
            memory_type=MemoryType.DOCUMENT,
            top_k=top_k
        )
        
        return [
            {
                "content": m.content,
                "source_file": m.metadata.get("file_name", "unknown"),
                "relevance_score": 0.9,  # Можно рассчитать точнее
                "chunk_index": m.metadata.get("chunk_index", 0)
            }
            for m in memories
        ]
    
    async def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Список документов пользователя"""
        user_dir = self.storage_path / user_id
        if not user_dir.exists():
            return []
        
        files = []
        for file_path in user_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": str(file_path)
                })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    
    async def delete_document(self, file_id: str, user_id: str) -> bool:
        """Удаление документа и связанных воспоминаний"""
        # Поиск файла по ID (хеш в начале имени)
        user_dir = self.storage_path / user_id
        if not user_dir.exists():
            return False
        target_file = None
        
        for file_path in user_dir.iterdir():
            if file_path.name.startswith(file_id):
                target_file = file_path
                break
        
        if not target_file:
            return False
        
        # Удаление файла
        target_file.unlink()
        
        # Удаление связанных воспоминаний из ChromaDB
        # (требует дополнительной логики поиска по metadata)
        
        return True

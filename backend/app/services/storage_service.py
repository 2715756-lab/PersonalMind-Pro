"""Сервис хранения файлов"""

import os
from pathlib import Path
from typing import Optional
import aiofiles
import hashlib
from app.core.config import settings


class StorageService:
    """Сервис управления хранилищем файлов"""
    
    def __init__(self):
        self.base_path = Path(settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: str) -> Path:
        """Получить директорию пользователя"""
        user_dir = self.base_path / user_id
        user_dir.mkdir(exist_ok=True, parents=True)
        return user_dir
    
    def _generate_filename(self, original_filename: str, content_hash: Optional[str] = None) -> str:
        """Генерировать безопасное имя файла"""
        if content_hash is None:
            content_hash = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        
        stem = Path(original_filename).stem
        suffix = Path(original_filename).suffix.lower()
        return f"{content_hash}_{stem}{suffix}"
    
    async def save_document(
        self,
        user_id: str,
        filename: str,
        content: bytes
    ) -> dict:
        """Сохранить документ"""
        content_hash = hashlib.md5(content).hexdigest()[:12]
        safe_filename = self._generate_filename(filename, content_hash)
        
        user_dir = self._get_user_dir(user_id)
        file_path = user_dir / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return {
            "file_id": content_hash,
            "filename": safe_filename,
            "original_filename": filename,
            "path": str(file_path),
            "size_bytes": len(content),
            "user_id": user_id
        }
    
    async def read_document(self, user_id: str, filename: str) -> bytes:
        """Прочитать документ"""
        file_path = self._get_user_dir(user_id) / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл {filename} не найден")
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    async def delete_document(self, user_id: str, filename: str) -> bool:
        """Удалить документ"""
        file_path = self._get_user_dir(user_id) / filename
        
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    
    async def list_documents(self, user_id: str) -> list:
        """Список документов пользователя"""
        user_dir = self._get_user_dir(user_id)
        
        documents = []
        for file_path in user_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                documents.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": str(file_path)
                })
        
        return sorted(documents, key=lambda x: x['modified'], reverse=True)

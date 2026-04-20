"""Сервис обработки документов"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
    JSONLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import markdown
from app.models.base import DocumentChunk
from app.core.config import settings


class DocumentService:
    """Сервис обработки документов"""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.csv': CSVLoader,
        '.json': JSONLoader,
        '.py': TextLoader,
        '.js': TextLoader,
        '.html': TextLoader,
    }
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def process_file(
        self,
        file_path: str,
        filename: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """Обработать файл и создать чанки"""
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Неподдерживаемый формат: {file_ext}")
        
        # Загрузка документа
        loader_class = self.SUPPORTED_EXTENSIONS[file_ext]
        loader = loader_class(file_path)
        documents = loader.load()
        
        # Объединение и разбиение текста
        full_text = "\n\n".join([doc.page_content for doc in documents])
        text_chunks = self.text_splitter.split_text(full_text)
        
        # Создание объектов DocumentChunk
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            doc_chunk = DocumentChunk(
                content=chunk_text,
                source_file=filename,
                file_type=file_ext,
                chunk_index=idx,
                total_chunks=len(text_chunks),
                metadata=metadata or {"source": "user_upload"},
                user_id=user_id
            )
            chunks.append(doc_chunk)
        
        return chunks
    
    async def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Создать краткое описание документа"""
        # Базовое резюме - первые строки
        lines = text.split('\n')
        summary_lines = []
        char_count = 0
        
        for line in lines:
            if char_count + len(line) > max_length:
                break
            if line.strip():
                summary_lines.append(line)
                char_count += len(line)
        
        return '\n'.join(summary_lines[:10])
    
    def extract_text_from_markdown(self, markdown_text: str) -> str:
        """Извлечь текст из Markdown"""
        html = markdown.markdown(markdown_text)
        # Простое удаление HTML тегов
        import re
        text = re.sub('<[^<]+?>', '', html)
        return text

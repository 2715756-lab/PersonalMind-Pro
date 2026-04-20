"""Сервис работы с эмбеддингами и LLM"""

from typing import List, Optional
import openai
from app.core.config import settings


class EmbeddingService:
    """Сервис для генерации эмбеддингов"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
    
    async def embed_text(self, text: str) -> List[float]:
        """Получить эмбеддинг текста"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Получить эмбеддинги для списка текстов"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


class LLMService:
    """Сервис для работы с LLM"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
    
    async def generate_response(
        self,
        messages: List[dict],
        temperature: Optional[float] = None,
        max_tokens: int = 2000,
        response_format: Optional[dict] = None
    ) -> str:
        """Генерировать ответ от LLM"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )
        return response.choices[0].message.content
    
    async def extract_json(
        self,
        text: str,
        extraction_prompt: str
    ) -> dict:
        """Извлечь JSON из текста с помощью LLM"""
        messages = [
            {"role": "system", "content": extraction_prompt},
            {"role": "user", "content": text}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {}

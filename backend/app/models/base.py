from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid


class MemoryType(str, Enum):
    EPISODIC = "episodic"      # Конкретные события
    SEMANTIC = "semantic"      # Факты
    PROCEDURAL = "procedural"  # Предпочтения/навыки
    DOCUMENT = "document"      # Из документов


class Memory(BaseModel):
    """Модель воспоминания"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    memory_type: MemoryType
    importance: float = Field(ge=0.0, le=1.0, default=0.5)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "chat"  # chat, document, system
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Профиль пользователя"""
    user_id: str
    demographics: Dict[str, Any] = Field(default_factory=dict)
    interests: List[Dict[str, Any]] = Field(default_factory=list)  # [{name, weight, source}]
    communication_style: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    goals: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    commerce_profile: Dict[str, Any] = Field(default_factory=dict)  # Для будущего
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentChunk(BaseModel):
    """Чанк документа"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    source_file: str
    file_type: str
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(BaseModel):
    """Сообщение чата"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    context_used: List[str] = Field(default_factory=list)  # ID использованных воспоминаний
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResponse(BaseModel):
    """Ответ агента"""
    text: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int
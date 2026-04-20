from typing import List, Dict, Any, Optional
import openai
import time

from app.models.base import ChatMessage, AgentResponse, Memory, MemoryType
from app.agents.memory_agent import MemoryAgent
from app.agents.profile_agent import ProfileAgent
from app.core.config import settings


class ChatAgent:
    """Агент ведения диалога с контекстом"""
    
    def __init__(
        self,
        memory_agent: MemoryAgent,
        profile_agent: ProfileAgent
    ):
        self.memory_agent = memory_agent
        self.profile_agent = profile_agent
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Системный промпт
        self.system_prompt = """Ты — PersonalMind Pro, персональный ИИ-ассистент с долгосрочной памятью.
Твоя задача — помогать пользователю, используя всё, что ты знаешь о нём.

Правила:
1. Обращайся дружелюбно, но профессионально
2. Используй информацию из контекста для персонализации ответов
3. Если упоминаешь факт из памяти — делай это естественно
4. Не выдумывай факты, которых нет в контексте
5. Если не уверен — уточни у пользователя
6. Адаптируй длину ответа под стиль пользователя (известен из профиля)"""
    
    async def generate_response(
        self,
        user_input: str,
        user_id: str,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> AgentResponse:
        """Генерация ответа с полным контекстом"""
        start_time = time.time()
        
        # 1. Получение релевантных воспоминаний
        memories = await self.memory_agent.recall(
            query=user_input,
            user_id=user_id,
            top_k=5
        )
        
        # 2. Получение профиля
        profile = await self.profile_agent.get_profile(user_id)
        
        # 3. Поиск в документах
        doc_memories = []
        if any(keyword in user_input.lower() for keyword in ["документ", "файл", "написано"]):
            doc_memories = await self.memory_agent.recall(
                query=user_input,
                user_id=user_id,
                memory_type=MemoryType.DOCUMENT,
                top_k=3
            )
        
        # 4. Формирование контекста
        context_messages = self._build_context_messages(
            memories=memories + doc_memories,
            profile=profile,
            history=conversation_history or []
        )
        
        # 5. Генерация ответа
        messages = [
            {"role": "system", "content": self.system_prompt},
            *context_messages,
            {"role": "user", "content": user_input}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=2000
        )
        
        assistant_text = response.choices[0].message.content
        
        # 6. Сохранение диалога в память
        await self.memory_agent.store(
            content=user_input,
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            source="user"
        )
        
        # 7. Обновление профиля если нужно
        if any(kw in user_input.lower() for kw in ["я ", "мне ", "мой "]):
            await self.profile_agent.update_from_conversation(user_id, user_input)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AgentResponse(
            text=assistant_text,
            sources=[{"type": "memory", "content": m.content[:100]} for m in memories[:3]],
            actions=[],
            confidence=0.85,
            processing_time_ms=processing_time
        )
    
    def _build_context_messages(
        self,
        memories: List[Memory],
        profile: Any,
        history: List[ChatMessage]
    ) -> List[Dict[str, str]]:
        """Построение контекстных сообщений"""
        messages = []
        
        # Профиль
        profile_text = "О пользователе:\n"
        demo = profile.demographics if hasattr(profile, 'demographics') else {}
        if demo.get('age'):
            profile_text += f"- Возраст: {demo['age']}\n"
        if demo.get('location'):
            profile_text += f"- Город: {demo['location']}\n"
        
        if profile_text != "О пользователе:\n":
            messages.append({"role": "system", "content": profile_text})
        
        # Воспоминания
        if memories:
            mem_text = "Факты из памяти:\n"
            for m in memories[:5]:
                mem_text += f"• {m.content[:150]}\n"
            messages.append({"role": "system", "content": mem_text})
        
        # История
        for msg in (history or [])[-3:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        return messages
        context_ids = [m.id for m in context_memories]
        await self.memory_agent.store(
            content=assistant_response,
            user_id=user_id,
            memory_type="episodic",
            importance=0.4,
            source="assistant",
            metadata={"context_memories": context_ids}
        )
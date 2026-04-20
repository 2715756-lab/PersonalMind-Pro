from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import openai
import redis.asyncio as redis

from app.models.base import UserProfile
from app.core.config import settings


class ProfileAgent:
    """Агент для построения и управления профилем пользователя"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def get_profile(self, user_id: str) -> UserProfile:
        """Получить или создать профиль"""
        key = f"profile:{user_id}"
        data = await self.redis.get(key)
        
        if data:
            profile_dict = json.loads(data)
            return UserProfile(**profile_dict)
        
        # Создать новый профиль
        profile = UserProfile(user_id=user_id)
        await self._save_profile(profile)
        return profile
    
    async def _save_profile(self, profile: UserProfile) -> None:
        """Сохранить профиль"""
        profile.updated_at = datetime.utcnow()
        key = f"profile:{profile.user_id}"
        await self.redis.setex(key, 86400 * 365, json.dumps(profile.model_dump()))
    
    async def update_from_conversation(
        self,
        user_id: str,
        conversation: str,
        assistant_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """Обновить профиль на основе диалога"""
        
        profile = await self.get_profile(user_id)
        
        # Простой анализ для извлечения фактов (в реальности - LLM)
        text_lower = conversation.lower()
        updates = {"updates_count": 0}
        
        # Демография
        if "мне " in text_lower and " лет" in text_lower:
            # Простейшее извлечение возраста из паттерна "мне N лет"
            import re
            match = re.search(r'мне\s+(\d+)\s+лет', text_lower)
            if match:
                age = int(match.group(1))
                profile.demographics["age"] = age
                updates["updates_count"] += 1
        
        if any(kw in text_lower for kw in ["я живу в ", "я проживаю в ", "я из "]):
            # Простой поиск локации
            import re
            match = re.search(r'я (?:живу в|проживаю в|из)\s+([а-яА-Я]+)', text_lower)
            if match:
                location = match.group(1)
                profile.demographics["location"] = location
                updates["updates_count"] += 1
        
        # Интересы
        if "люблю" in text_lower or "мне нравится" in text_lower:
            # Простое извлечение
            if "люблю" in text_lower:
                import re
                match = re.search(r'люблю\s+([а-яА-Я\s]+)(?:\.|,|$)', conversation)
                if match:
                    interest = match.group(1).strip()
                    existing = next((i for i in profile.interests if i.get("name") == interest), None)
                    if not existing:
                        profile.interests.append({
                            "name": interest,
                            "weight": 0.7,
                            "added_at": datetime.utcnow().isoformat()
                        })
                        updates["updates_count"] += 1
        
        await self._save_profile(profile)
        return updates
    
    async def get_relevant_context(
        self,
        user_id: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить релевантный контекст профиля"""
        profile = await self.get_profile(user_id)
        
        return {
            "demographics": profile.demographics,
            "interests": profile.interests[:3],
            "preferences": profile.preferences,
            "goals": profile.goals[:2]
        }
                    updates.append(f"demographics.{key}")
        
        # Интересы
        for interest in insights.get('interests', []):
            if not any(i['name'] == interest['name'] for i in profile.interests):
                profile.interests.append({
                    "name": interest['name'],
                    "context": interest.get('context', ''),
                    "added_at": datetime.utcnow().isoformat()
                })
                updates.append(f"interest: {interest['name']}")
        
        # Предпочтения коммуникации
        if insights.get('preferences'):
            for key, value in insights['preferences'].items():
                if value:
                    profile.communication_style[key] = value
                    updates.append(f"preference: {key}")
        
        # Цели
        for goal in insights.get('goals', []):
            if not any(g['description'] == goal['description'] for g in profile.goals):
                profile.goals.append({
                    "description": goal['description'],
                    "category": goal.get('category', 'general'),
                    "added_at": datetime.utcnow().isoformat(),
                    "status": "active"
                })
                updates.append(f"goal: {goal['description']}")
        
        # Факты (дополнительные)
        for fact in insights.get('facts', []):
            # Здесь можно сохранить в специальное хранилище фактов
            pass
        
        profile.updated_at = datetime.utcnow()
        await self._save_profile(profile)
        
        return {
            "updated": len(updates) > 0,
            "fields_updated": updates,
            "profile": profile
        }
    
    async def get_relevant_context(
        self,
        user_id: str,
        query: str
    ) -> Dict[str, Any]:
        """Получение релевантного контекста профиля для запроса"""
        
        profile = await self.get_profile(user_id)
        
        # Простой keyword matching (можно улучшить через embeddings)
        query_lower = query.lower()
        relevant_interests = [
            i for i in profile.interests 
            if i['name'].lower() in query_lower or 
            any(word in i.get('context', '').lower() for word in query_lower.split())
        ]
        
        # Предпочтения общения
        style = profile.communication_style
        
        return {
            "demographics": profile.demographics,
            "relevant_interests": relevant_interests,
            "communication_preferences": style,
            "active_goals": [g for g in profile.goals if g.get('status') == 'active'][:3]
        }
    
    async def get_commerce_profile(self, user_id: str) -> Dict[str, Any]:
        """Получение коммерческого профиля (для будущего Commerce Agent)"""
        profile = await self.get_profile(user_id)
        return {
            "address": profile.commerce_profile.get('address'),
            "phone": profile.commerce_profile.get('phone'),
            "payment_methods": profile.commerce_profile.get('payment_methods', []),
            "preferred_stores": profile.commerce_profile.get('preferred_stores', []),
            "dietary_restrictions": profile.commerce_profile.get('dietary_restrictions', []),
            "budget_range": profile.commerce_profile.get('budget_range')
        }
    
    async def update_commerce_profile(self, user_id: str, updates: Dict[str, Any]):
        """Обновление коммерческого профиля"""
        profile = await self.get_profile(user_id)
        profile.commerce_profile.update(updates)
        profile.updated_at = datetime.utcnow()
        await self._save_profile(profile)
        return profile.commerce_profile
    
    async def _save_profile(self, profile: UserProfile):
        """Сохранение профиля в Redis"""
        key = f"profile:{profile.user_id}"
        await self.redis.set(
            key,
            json.dumps(profile.model_dump(), default=str),
            ex=86400 * 30  # 30 дней
        )
    
    async def enrich_from_entities(self, user_id: str, entities: List[Dict[str, Any]]):
        """Обогащение профиля извлечёнными сущностями (из документов)"""
        profile = await self.get_profile(user_id)
        
        for entity in entities:
            entity_type = entity.get('type')
            entity_value = entity.get('value')
            
            if entity_type == 'PERSON' and 'family' not in profile.relationships:
                profile.relationships.setdefault('family', []).append(entity_value)
            elif entity_type == 'ORG' and 'work' not in profile.demographics:
                profile.demographics['work'] = entity_value
            elif entity_type == 'GPE':  # Геополитическая единица
                if 'location' not in profile.demographics:
                    profile.demographics['location'] = entity_value
        
        await self._save_profile(profile)
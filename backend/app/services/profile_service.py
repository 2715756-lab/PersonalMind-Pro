"""Сервис управления профилем пользователя"""

from typing import Dict, Any, Optional
import redis.asyncio as redis
import json
from datetime import datetime

from app.models.base import UserProfile
from app.core.config import settings


class ProfileService:
    """Сервис управления профилем"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 86400 * 365  # 1 год
    
    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Получить или создать профиль"""
        key = f"profile:{user_id}"
        
        # Попытка получить из кэша
        data = await self.redis.get(key)
        
        if data:
            profile_dict = json.loads(data)
            return UserProfile(**profile_dict)
        
        # Создать новый профиль
        profile = UserProfile(user_id=user_id)
        await self._save_profile(profile)
        return profile
    
    async def _save_profile(self, profile: UserProfile) -> None:
        """Сохранить профиль в Redis"""
        profile.updated_at = datetime.utcnow()
        key = f"profile:{profile.user_id}"
        
        await self.redis.setex(
            key,
            self.default_ttl,
            json.dumps(profile.model_dump())
        )
    
    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserProfile:
        """Обновить профиль"""
        profile = await self.get_or_create_profile(user_id)
        
        # Применение обновлений
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        await self._save_profile(profile)
        return profile
    
    async def add_interest(
        self,
        user_id: str,
        name: str,
        context: str = "",
        weight: float = 0.5
    ) -> UserProfile:
        """Добавить интерес в профиль"""
        profile = await self.get_or_create_profile(user_id)
        
        # Проверить, существует ли уже
        existing = next((i for i in profile.interests if i.get("name") == name), None)
        
        if existing:
            existing["weight"] = min(1.0, existing.get("weight", 0.5) + weight * 0.1)
            existing["context"] = context or existing.get("context")
        else:
            profile.interests.append({
                "name": name,
                "weight": weight,
                "context": context,
                "added_at": datetime.utcnow().isoformat()
            })
        
        await self._save_profile(profile)
        return profile
    
    async def add_goal(
        self,
        user_id: str,
        description: str,
        category: str = "general"
    ) -> UserProfile:
        """Добавить цель"""
        profile = await self.get_or_create_profile(user_id)
        
        profile.goals.append({
            "description": description,
            "category": category,
            "added_at": datetime.utcnow().isoformat(),
            "priority": "medium"
        })
        
        await self._save_profile(profile)
        return profile
    
    async def update_demographics(
        self,
        user_id: str,
        age: Optional[int] = None,
        location: Optional[str] = None,
        occupation: Optional[str] = None
    ) -> UserProfile:
        """Обновить демографию"""
        profile = await self.get_or_create_profile(user_id)
        
        if age is not None:
            profile.demographics["age"] = age
        if location:
            profile.demographics["location"] = location
        if occupation:
            profile.demographics["occupation"] = occupation
        
        await self._save_profile(profile)
        return profile
    
    async def delete_profile(self, user_id: str) -> bool:
        """Удалить профиль"""
        key = f"profile:{user_id}"
        result = await self.redis.delete(key)
        return result > 0

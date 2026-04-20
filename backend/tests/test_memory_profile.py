import pytest

from app.agents.memory_agent import MemoryAgent
from app.agents.profile_agent import ProfileAgent


@pytest.mark.asyncio
async def test_memory_store_and_recall():
    agent = MemoryAgent()

    stored = await agent.store("Проверочное воспоминание о встрече", "user-test", importance=0.9)
    assert stored.content.startswith("Проверочное")

    recalled = await agent.recall("встрече", "user-test", top_k=3)
    assert recalled
    assert recalled[0].id == stored.id

    stats = await agent.get_stats("user-test")
    assert stats["total"] == 1
    assert "episodic" in stats["breakdown"]


@pytest.mark.asyncio
async def test_profile_updates_from_conversation():
    agent = ProfileAgent()
    result = await agent.update_from_conversation("user-test", "мне 29 лет, живу в Москве на Тверской")

    assert result["updated"]
    profile = await agent.get_profile("user-test")
    assert profile.demographics["age"] == 29
    assert "москве" in profile.demographics["location"].lower()

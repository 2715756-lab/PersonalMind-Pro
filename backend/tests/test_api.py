"""Базовые тесты для backend"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestHealthCheck:
    def test_health_check(self):
        """Тест здоровья приложения"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestChatEndpoint:
    def test_chat_successful(self):
        """Тест отправки сообщения"""
        response = client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "content": "Привет!",
                "metadata": {}
            }
        )
        assert response.status_code == 200
        assert "text" in response.json()
        assert response.json()["confidence"] > 0


class TestMemoryEndpoint:
    def test_memory_stats(self):
        """Тест получения статистики памяти"""
        response = client.get("/memory/stats", params={"user_id": "test_user"})
        assert response.status_code == 200
        data = response.json()
        assert "total_memories" in data
        assert "by_type" in data


class TestProfileEndpoint:
    def test_get_profile(self):
        """Тест получения профиля"""
        response = client.get("/profile", params={"user_id": "test_user"})
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "demographics" in data


class TestDocumentsEndpoint:
    def test_list_documents(self):
        """Тест списка документов"""
        response = client.get("/documents", params={"user_id": "test_user"})
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

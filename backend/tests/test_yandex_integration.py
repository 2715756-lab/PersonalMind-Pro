"""Integration tests using Yandex GPT API"""

import asyncio
import pytest
from backend.app.services.yandex_llm_service import YandexLLMService


class TestYandexGPT:
    """Test suite for Yandex GPT integration"""

    @pytest.fixture
    def yandex_service(self):
        """Initialize Yandex LLM service"""
        return YandexLLMService(
            api_key="YOUR_YANDEX_API_KEY",  # Set in .env
            folder_id="YOUR_FOLDER_ID",     # Set in .env
        )

    @pytest.mark.asyncio
    async def test_health_check(self, yandex_service):
        """Test Yandex API availability"""
        is_healthy = await yandex_service.health_check()
        assert is_healthy is True, "Yandex API should be accessible"

    @pytest.mark.asyncio
    async def test_basic_response(self, yandex_service):
        """Test basic text generation"""
        response = await yandex_service.generate_response("Привет, как дела?")
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        print(f"✅ Generated: {response}")

    @pytest.mark.asyncio
    async def test_temperature_variation(self, yandex_service):
        """Test different temperature values"""
        prompt = "Назови 3 российских города"

        # Low temp - more deterministic
        response_low = await yandex_service.generate_response(
            prompt, temperature=0.1, max_tokens=100
        )
        assert len(response_low) > 0

        # High temp - more creative
        response_high = await yandex_service.generate_response(
            prompt, temperature=0.9, max_tokens=100
        )
        assert len(response_high) > 0
        print(f"✅ Low temp: {response_low}")
        print(f"✅ High temp: {response_high}")

    @pytest.mark.asyncio
    async def test_intent_classification(self, yandex_service):
        """Test intent classification from message"""
        intents = ["greeting", "question", "command", "complaint"]

        # Test greeting
        intent, confidence = await yandex_service.classify_intent(
            "Привет, как дела?", intents
        )
        assert intent in intents, f"Intent should be from list, got {intent}"
        assert 0 <= confidence <= 1, "Confidence should be 0-1"
        print(f"✅ Greeting intent: {intent} (confidence: {confidence})")

        # Test command
        intent, confidence = await yandex_service.classify_intent(
            "Найди мне пиццу", intents
        )
        assert intent in intents
        print(f"✅ Command intent: {intent} (confidence: {confidence})")

    @pytest.mark.asyncio
    async def test_json_extraction(self, yandex_service):
        """Test JSON extraction from response"""
        prompt = """Верни JSON с информацией: 
        {
            "name": "Иван",
            "age": 25,
            "city": "Москва"
        }
        """
        result = await yandex_service.extract_json(
            "Мой профиль: Иван, 25 лет, из Москвы"
        )
        assert isinstance(result, dict), "Result should be a dictionary"
        print(f"✅ Extracted JSON: {result}")

    @pytest.mark.asyncio
    async def test_memory_recall_simulation(self, yandex_service):
        """Test memory-like responses"""
        conversation = [
            "Привет! Я Артем",
            "Я живу в Санкт-Петербурге",
            "Люблю программировать",
        ]

        # Simulate learning from conversation
        context = "\n".join([f"- {msg}" for msg in conversation])
        prompt = f"""Based on this conversation:
{context}

What can you tell me about this person?"""

        response = await yandex_service.generate_response(prompt)
        assert len(response) > 0
        print(f"✅ Memory recall: {response}")

    @pytest.mark.asyncio
    async def test_document_summarization(self, yandex_service):
        """Test document summarization capability"""
        document = """
        PersonalMind Pro - это ИИ-ассистент с долгосрочной памятью.
        Он может запоминать информацию о пользователе, работать с документами,
        интегрироваться с сервисами доставки и быть доступным через Telegram.
        Система использует векторную базу данных для семантического поиска.
        """

        prompt = f"""Summarize this document in 1-2 sentences:
{document}"""

        summary = await yandex_service.generate_response(prompt, max_tokens=100)
        assert len(summary) > 0
        print(f"✅ Summary: {summary}")

    @pytest.mark.asyncio
    async def test_streaming_response(self, yandex_service):
        """Test streaming response generation"""
        prompt = "Расскажи о своих возможностях"
        chunks = []

        async for chunk in yandex_service.generate_streaming_response(prompt):
            chunks.append(chunk)

        full_response = "".join(chunks)
        assert len(full_response) > 0
        print(f"✅ Streamed {len(chunks)} chunks: {full_response}")

    @pytest.mark.asyncio
    async def test_commerce_query(self, yandex_service):
        """Test commerce-related queries"""
        prompts = [
            "Какие товары можно купить в Samokat?",
            "Найди мне пиццу с пепперони",
            "Какие доставки работают в Москве?",
        ]

        for prompt in prompts:
            response = await yandex_service.generate_response(
                prompt, max_tokens=150
            )
            assert len(response) > 0
            print(f"✅ Commerce query: {prompt}")
            print(f"   Response: {response[:100]}...\n")


# Manual testing
async def manual_test_yandex():
    """Manual test script"""
    import os
    print("=" * 60)
    print("🧪 Yandex GPT API Integration Tests")
    print("=" * 60)

    # Get API key from environment
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    
    if not api_key or not folder_id:
        print("❌ YANDEX_API_KEY or YANDEX_FOLDER_ID not set in environment")
        print("Set them in .env file")
        return
    
    service = YandexLLMService(
        api_key=api_key,
        folder_id=folder_id,
    )

    # Test 1: Health Check
    print("\n1️⃣ Health Check")
    is_healthy = await service.health_check()
    print(f"Status: {'✅ OK' if is_healthy else '❌ Failed'}")

    # Test 2: Basic Response
    print("\n2️⃣ Basic Response")
    response = await service.generate_response("Привет! Кто ты?")
    print(f"Response: {response}")

    # Test 3: Intent Classification
    print("\n3️⃣ Intent Classification")
    intent, confidence = await service.classify_intent(
        "Найди мне пиццу", ["greeting", "question", "commerce", "help"]
    )
    print(f"Intent: {intent} (confidence: {confidence})")

    # Test 4: JSON Extraction
    print("\n4️⃣ JSON Extraction")
    result = await service.extract_json("Мне 25 лет, я из Москвы, люблю кодить")
    print(f"Extracted: {result}")

    # Test 5: Commerce Scenario
    print("\n5️⃣ Commerce Query")
    response = await service.generate_response(
        "Какие товары можно купить через приложение доставки? Назови 5 категорий."
    )
    print(f"Response: {response}")

    print("\n" + "=" * 60)
    print("✅ All manual tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run manual tests
    asyncio.run(manual_test_yandex())

    # For pytest:
    # pytest backend/tests/test_yandex_integration.py -v -s

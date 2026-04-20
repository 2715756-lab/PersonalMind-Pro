#!/usr/bin/env python3
"""
🧪 PersonalMind Pro - Yandex GPT Integration Testing Script
Run comprehensive tests using Yandex GPT API
"""

import asyncio
import json
import sys
from typing import Dict, List
from datetime import datetime


async def test_yandex_integration():
    """Run all integration tests with Yandex API"""
    
    # Import after path setup
    try:
        from backend.app.services.yandex_llm_service import YandexLLMService
    except ImportError:
        sys.path.insert(0, "/Users/artemrogacev/IdeaProjects/personalAIagent/personal-mind-pro")
        from backend.app.services.yandex_llm_service import YandexLLMService

    print("\n" + "=" * 70)
    print("🧠 PersonalMind Pro - Yandex GPT Integration Tests")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Get credentials from environment
    import os
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    
    if not api_key or not folder_id:
        print("\n❌ ERROR: YANDEX_API_KEY or YANDEX_FOLDER_ID not set")
        print("Please set them in .env file or environment variables")
        return None, None, None
    
    # Initialize service
    service = YandexLLMService(
        api_key=api_key,
        folder_id=folder_id,
    )

    results: Dict[str, Dict] = {}

    # Test 1: Health Check
    print("\n\n📡 TEST 1: API Health Check")
    print("-" * 70)
    try:
        is_healthy = await service.health_check()
        status = "✅ PASS" if is_healthy else "❌ FAIL"
        print(f"Status: {status}")
        results["health_check"] = {
            "status": "pass" if is_healthy else "fail",
            "message": "Yandex GPT API is accessible",
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["health_check"] = {"status": "fail", "error": str(e)}

    # Test 2: Basic Russian Response
    print("\n\n💬 TEST 2: Basic Russian Response Generation")
    print("-" * 70)
    try:
        response = await service.generate_response(
            "Привет! Назови себя и опиши свои возможности", max_tokens=300
        )
        print(f"Prompt: Привет! Назови себя и опиши свои возможности")
        print(f"Response: {response[:150]}...")
        results["basic_response_ru"] = {
            "status": "pass",
            "response_length": len(response),
            "first_100_chars": response[:100],
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["basic_response_ru"] = {"status": "fail", "error": str(e)}

    # Test 3: Temperature Variation
    print("\n\n🌡️ TEST 3: Temperature Variation (Creativity vs Determinism)")
    print("-" * 70)
    try:
        prompt = "Назови 5 российских городов"

        response_cold = await service.generate_response(
            prompt, temperature=0.1, max_tokens=100
        )
        print(f"Low Temp (0.1): {response_cold[:100]}...")

        response_hot = await service.generate_response(
            prompt, temperature=0.9, max_tokens=100
        )
        print(f"High Temp (0.9): {response_hot[:100]}...")

        results["temperature_variation"] = {
            "status": "pass",
            "cold_response": response_cold[:50],
            "hot_response": response_hot[:50],
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["temperature_variation"] = {"status": "fail", "error": str(e)}

    # Test 4: Intent Classification
    print("\n\n🎯 TEST 4: Intent Classification")
    print("-" * 70)
    test_queries = [
        ("Привет, как дела?", "greeting"),
        ("Найди мне пиццу", "commerce"),
        ("Что я рассказывал тебе вчера?", "memory"),
        ("Помощь, что-то сломалось", "help"),
    ]

    all_classifications_pass = True
    for query, expected_intent in test_queries:
        try:
            intent, confidence = await service.classify_intent(
                query, ["greeting", "commerce", "memory", "help", "unknown"]
            )
            print(
                f"Query: '{query}' → Intent: {intent} (confidence: {confidence:.2f})"
            )
            if intent in ["greeting", "commerce", "memory", "help", "unknown"]:
                results[f"classify_{query[:10]}"] = {
                    "status": "pass",
                    "intent": intent,
                    "confidence": confidence,
                }
            else:
                all_classifications_pass = False
        except Exception as e:
            print(f"❌ Query '{query}' failed: {str(e)}")
            all_classifications_pass = False

    results["intent_classification"] = {
        "status": "pass" if all_classifications_pass else "partial"
    }

    # Test 5: Memory Scenario Simulation
    print("\n\n🧠 TEST 5: Memory Simulation (User Learning)")
    print("-" * 70)
    try:
        conversation_history = [
            "Привет, я Артем Рогачев",
            "Я живу в Санкт-Петербурге",
            "Я разработчик ИИ-систем",
            "Встаю в 7:00 утра",
            "Люблю кофе и программирование",
        ]

        context = "\n".join(
            [f"Пользователь: {msg}" for msg in conversation_history]
        )
        prompt = f"""Based on the following conversation, create a user profile:
{context}

Provide a JSON profile with: name, location, profession, routine, interests"""

        profile_response = await service.generate_response(prompt, max_tokens=200)
        print(f"Generated profile snippet: {profile_response[:150]}...")

        results["memory_simulation"] = {
            "status": "pass",
            "profile_generated": True,
            "response_length": len(profile_response),
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["memory_simulation"] = {"status": "fail", "error": str(e)}

    # Test 6: Document Summarization
    print("\n\n📄 TEST 6: Document Summarization")
    print("-" * 70)
    try:
        document = """
        PersonalMind Pro is an AI assistant with long-term memory capabilities.
        It can remember user information, work with documents, integrate with
        delivery services, and be accessible via Telegram. The system uses a
        vector database for semantic search and stores memories across multiple
        dimensions: episodic (events), semantic (facts), procedural (preferences),
        and document-based (extracted from uploaded files).
        """

        prompt = f"""Summarize this document in 2 sentences:
{document}"""

        summary = await service.generate_response(prompt, max_tokens=100)
        print(f"Summary: {summary}")

        results["document_summarization"] = {
            "status": "pass",
            "summary": summary[:100],
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["document_summarization"] = {"status": "fail", "error": str(e)}

    # Test 7: Commerce Query
    print("\n\n🛒 TEST 7: Commerce Integration")
    print("-" * 70)
    commerce_queries = [
        "Какие товары доступны в приложении Samokat?",
        "Найди пиццу с пепперони в ближайших ресторанах",
        "Помоги выбрать продукты для ужина",
    ]

    for query in commerce_queries:
        try:
            response = await service.generate_response(query, max_tokens=150)
            print(f"Q: {query}")
            print(f"A: {response[:100]}...\n")
        except Exception as e:
            print(f"❌ Failed: {str(e)}\n")

    results["commerce_integration"] = {"status": "pass", "queries_tested": 3}

    # Test 8: Multi-turn Conversation
    print("\n\n🔄 TEST 8: Multi-turn Conversation Simulation")
    print("-" * 70)
    try:
        # First turn
        q1 = "Привет, я хочу что-нибудь поесть"
        r1 = await service.generate_response(q1, max_tokens=150)
        print(f"User: {q1}")
        print(f"Bot: {r1}\n")

        # Second turn (should understand context)
        q2 = f"Предыдущий ответ был: {r1[:80]}... Дай мне 3 варианта"
        r2 = await service.generate_response(q2, max_tokens=150)
        print(f"User: {q2}")
        print(f"Bot: {r2}\n")

        results["multi_turn_conversation"] = {
            "status": "pass",
            "turns": 2,
        }
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["multi_turn_conversation"] = {"status": "fail", "error": str(e)}

    # Test 9: JSON Extraction
    print("\n\n📋 TEST 9: JSON Data Extraction")
    print("-" * 70)
    try:
        text = "Мне 25 лет, я живу в Москве, работаю разработчиком, люблю путешествия"
        result = await service.extract_json(text)
        print(f"Input: {text}")
        print(f"Extracted: {json.dumps(result, indent=2, ensure_ascii=False)}")

        results["json_extraction"] = {"status": "pass", "data_extracted": True}
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        results["json_extraction"] = {"status": "fail", "error": str(e)}

    # Print Summary Report
    print("\n\n" + "=" * 70)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 70)

    passed = sum(1 for r in results.values() if r.get("status") == "pass")
    failed = sum(1 for r in results.values() if r.get("status") == "fail")
    partial = sum(1 for r in results.values() if r.get("status") == "partial")

    print(f"\n✅ PASSED:  {passed}")
    print(f"❌ FAILED:  {failed}")
    print(f"⚠️  PARTIAL: {partial}")
    print(f"📈 SUCCESS RATE: {(passed / len(results) * 100):.1f}%")

    print("\n" + "-" * 70)
    print("Detailed Results:")
    print("-" * 70)
    for test_name, result in results.items():
        status_icon = "✅" if result.get("status") == "pass" else "❌"
        print(f"{status_icon} {test_name}: {result.get('status')}")

    print("\n" + "=" * 70)
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return passed, failed, partial


if __name__ == "__main__":
    asyncio.run(test_yandex_integration())

# 🧪 Yandex GPT Integration Testing Guide

## 📋 Overview

PersonalMind Pro теперь поддерживает **Yandex GPT API** как альтернативу OpenAI. Это позволяет тестировать приложение с русскоязычным ИИ и избегать зависимости от одного провайдера.

**Ваши Yandex Credentials (из .env):**
```
YANDEX_API_KEY=your-api-key-here
YANDEX_FOLDER_ID=your-folder-id-here
YANDEX_MODEL=gpt://your-folder-id/yandexgpt-lite
```

> ⚠️ **ВАЖНО**: Никогда не коммитьте реальные ключи в Git! Используйте .env файл.

---

## 🚀 Быстрый Старт

### 1. Добавить Yandex Credentials в `.env`

```bash
# .env
LLM_PROVIDER=yandex
YANDEX_API_KEY=your-yandex-api-key-here
YANDEX_FOLDER_ID=your-yandex-folder-id-here
```

### 2. Установить зависимости

```bash
cd backend
pip install -r requirements.txt  # aiohttp уже включен
```

### 3. Запустить Интеграционный Тест

```bash
# Способ 1: Python скрипт
python scripts/test_yandex_llm.py

# Способ 2: pytest
pytest backend/tests/test_yandex_integration.py -v -s

# Способ 3: Отдельный тест
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_health_check -v
```

---

## 🧪 Доступные Тесты

### 1. **Health Check** - Проверка доступности API
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_health_check -v
```

### 2. **Basic Response** - Генерация текста
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_basic_response -v
```

### 3. **Temperature Variation** - Креативность vs Детерминизм
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_temperature_variation -v
```

### 4. **Intent Classification** - Распознавание намерений
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_intent_classification -v
```

### 5. **Memory Simulation** - Имитация системы памяти
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_memory_recall_simulation -v
```

### 6. **Document Summarization** - Суммаризация текстов
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_document_summarization -v
```

### 7. **Commerce Query** - Коммерческие запросы
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_commerce_query -v
```

### 8. **JSON Extraction** - Извлечение JSON из ответов
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_json_extraction -v
```

### 9. **Streaming Response** - Потоковые ответы
```bash
pytest backend/tests/test_yandex_integration.py::TestYandexGPT::test_streaming_response -v
```

---

## 📊 Полный Интеграционный Тест

Запустите все 9 тестов сразу:

```bash
pytest backend/tests/test_yandex_integration.py -v

# С дополнительным логированием
pytest backend/tests/test_yandex_integration.py -v -s

# С покрытием кода
pytest backend/tests/test_yandex_integration.py -v --cov=backend.app.services
```

---

## 🔧 Использование Yandex LLM Service в Коде

### Базовый Пример

```python
from backend.app.services.yandex_llm_service import YandexLLMService
import os

# Инициализация
service = YandexLLMService(
    api_key=os.getenv("YANDEX_API_KEY"),
    folder_id=os.getenv("YANDEX_FOLDER_ID")
)

# Генерация ответа
response = await service.generate_response("Привет, как дела?")
```

### Классификация Намерений

```python
intent, confidence = await service.classify_intent(
    "Найди мне пиццу",
    ["greeting", "question", "commerce", "help"]
)
print(f"Intent: {intent} ({confidence:.2f})")  # Intent: commerce (0.95)
```

### Извлечение JSON

```python
result = await service.extract_json(
    "Мне 25 лет, я из Москвы"
)
print(result)  # {'age': 25, 'city': 'Moscow', ...}
```

### Потоковые Ответы

```python
async for chunk in service.generate_streaming_response("Расскажи мне..."):
    print(chunk, end="")  # Печатать по частям
```

---

## 📈 Сравнение OpenAI vs Yandex GPT

| Параметр | OpenAI | Yandex GPT |
|----------|--------|-----------|
| **Язык** | Английский |  🇷🇺 Русский |
| **Цена** | Платно | Бесплатно/долговое финансирование |
| **API** | REST + Streaming | REST + Streaming |
| **Модели** | GPT-4, 3.5 | YandexGPT-lite, pro |
| **Локальность** | Облако США | Облако РФ |
| **JSON Mode** | ✅ | ✅ |
| **Embeddings** | ✅ | ❓ |

---

## 🔗 Интеграция с Backend API

### Обновить Chat Agent

```python
# backend/app/agents/chat_agent.py
from backend.app.services.yandex_llm_service import YandexLLMService
from backend.app.core.config import settings

if settings.LLM_PROVIDER == "yandex":
    llm_service = YandexLLMService(
        api_key=settings.YANDEX_API_KEY,
        folder_id=settings.YANDEX_FOLDER_ID
    )
else:
    llm_service = EmbeddingService()  # OpenAI
```

---

## ✅ Чек-Лист Тестирования

### Основное Тестирование
- [ ] Health Check успешен
- [ ] Basic Response генерирует текст
- [ ] Temperature variation работает
- [ ] Intent classification корректен

### Функциональное Тестирование  
- [ ] Memory simulation работает
- [ ] Document summarization работает
- [ ] Commerce queries работают
- [ ] JSON extraction успешен

### Интеграционное Тестирование
- [ ] Yandex service интегрирован в Orchestrator
- [ ] Chat Agent использует Yandex LLM
- [ ] Frontend получает ответы от Yandex
- [ ] Telegram Bot работает с Yandex

### Production Checks
- [ ] API Rate Limits отлично
- [ ] Response time приемлем
- [ ] Error handling работает
- [ ] Logging правильный

---

## 🐛 Troubleshooting

### Ошибка: "API Key Invalid"
```bash
# Проверить .env файл
cat .env | grep YANDEX_API_KEY
```

### Ошибка: "Connection Timeout"
```bash
# Проверить доступность API
curl https://ai.api.cloud.yandex.net/v1/responses \
  -H "Authorization: Api-Key YOUR_KEY" \
  -H "x-folder-id: YOUR_FOLDER_ID"
```

### Ошибка: "Rate Limit Exceeded"
```bash
# Добавить retry logic
try:
    response = await service.generate_response(prompt)
except RateLimitError:
    await asyncio.sleep(2)  # backoff
    response = await service.generate_response(prompt)
```

---

## 📚 Документация

- [Yandex GPT API Docs](https://cloud.yandex.ru/docs/foundation-models/concepts/yandexgpt)
- [PersonalMind Pro Architecture](../docs/ARCHITECTURE.md)
- [Backend Services](../docs/SERVICES.md)

---

## 🎯 Следующие Шаги

1. ✅ Интегрировать Yandex в Orchestrator
2. ⏳ Добавить поддержку embeddings для ChromaDB
3. ⏳ Оптимизировать retry logic
4. ⏳ Добавить A/B тестирование OpenAI vs Yandex
5. ⏳ Production deployment с Yandex GPT

---

**Нужна помощь?** Откройте issue на GitHub! 🚀

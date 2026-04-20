# PersonalMind Pro 🧠

Полнофункциональный персональный ИИ-ассистент с долгосрочной памятью, поддержкой документов и интеграцией с сервисами доставки.

## 🎯 Возможности

- **💬 Умный чат** - ИИ помнит всё о вас
- **🧠 Долгосрочная память** - векторная БД для семантического поиска
- **📁 Работа с документами** - загрузка и поиск в PDF, TXT, Markdown
- **👤 Профиль пользователя** - автоматическое обучение
- **🛒 Интеграция магазинов** - Samokat, Papa John's
- **🤖 Telegram Bot** - полный доступ через мессенджер
- **🎨 Красивый UI** - современный интерфейс на Next.js

## 🚀 Быстрый старт

### требования
- Docker & Docker Compose
- OpenAI API ключ

### Запуск

```bash
git clone <repo>
cd personal-mind-pro

# Скопировать и отредактировать .env
cp .env.example .env
# Добавить API ключи

# Запустить все сервисы
docker-compose up -d
```

Доступно:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 🏗️ Архитектура

**3 основных компонента:**

1. **Backend (Python/FastAPI)**
   - REST API
   - Система агентов (Memory, Chat, Profile, Document, Commerce)
   - PostgreSQL + Redis + ChromaDB

2. **Frontend (Next.js/React)**
   - 💬 Chat Interface
   - 🧠 Memory Graph
   - 📁 File Manager
   - 🛒 Commerce Panel
   - 👤 Profile Panel

3. **Telegram Bot (Python)**
   - Синхронизация с backend
   - Поиск товаров
   - Загрузка документов

## 📚 API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|---------|
| POST | `/chat` | Отправить сообщение |
| POST | `/upload` | Загрузить документ |
| GET | `/memory/stats` | Статистика памяти |
| GET | `/profile` | Профиль пользователя |
| GET | `/documents` | Список документов |
| POST | `/commerce/search` | Поиск товаров |

## 💻 Локальная разработка

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (в другом терминале)
cd frontend
npm install
npm run dev

# Telegram Bot (в третьем терминале)
cd telegram-bot
pip install -r requirements.txt
python main.py
```

## 🧪 Тестирование

```bash
pytest backend/tests/
npm test --prefix frontend/
```

## 🔐 Переменные окружения

```env
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379/0
```

## 📖 Документация

- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)

## 📄 Лицензия

MIT

## 🎉 Готово к использованию!

Проект полностью функционален и готов к деплойменту в production.

---
**Нужна помощь?** Откройте issue на GitHub! 🚀

# 🤖 Telegram Bot Setup Guide

## Важная информация

Ваш Telegram Bot Token сохранен в `.env` файле (локально, не в Git):
```
TELEGRAM_BOT_TOKEN=8645567088:AAFWnoi9R2h40p48oCOfPyfiWAVhDjIe1KM
```

## 🚀 Быстрый Старт

### 1. Установить зависимости

```bash
cd telegram-bot
python -m venv venv
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Проверить конфигурацию

```bash
# Убедиться, что .env файл в корне проекта с TELEGRAM_BOT_TOKEN
cat ../.env | grep TELEGRAM_BOT_TOKEN
```

### 3. Запустить бота

```bash
python main.py
```

Вы должны увидеть:
```
✅ Bot Token configured
✅ Backend URL: http://localhost:8001
✅ Connected to Telegram API
🤖 Bot: @PersonalMindProBot (PersonalMind Pro)
🚀 Starting polling...
```

## 📱 Тестирование в Telegram

### Найти бота

- Откройте Telegram
- Найдите бота по имени: **@PersonalMindProBot**
- Нажмите /start

### Доступные команды

| Команда | Описание |
|---------|---------|
| `/start` | Приветствие и информация |
| `/help` | Справка по командам |
| `/search <query>` | Поиск товаров |
| `/memory <text>` | Запрос памяти |
| `/docs` | Список загруженных документов |

### Примеры

```
/start                          → Приветствие
/help                           → Справка
/search пицца пепперони        → Поиск пиццы
/memory как меня зовут?         → Вспомнить имя
/docs                           → Список файлов
```

## 🔧 Структура Бота

```
telegram-bot/
├── main.py                     # Entry point
├── bot.py                      # Bot configuration (старый файл)
├── app/
│   ├── config.py              # Settings & environment
│   ├── handlers/
│   │   ├── commands.py        # /start, /help, etc
│   │   ├── messages.py        # Текстовые сообщения
│   │   ├── files.py           # Загрузка файлов
│   │   ├── callbacks.py       # Кнопки и inline-меню
│   │   ├── commerce.py        # Заказы и товары
│   │   └── __init__.py
│   ├── keyboards/
│   │   ├── main.py            # Кнопки меню
│   │   └── __init__.py
│   ├── services/
│   │   ├── api_client.py      # Backend API integration
│   │   └── __init__.py
│   └── __init__.py
├── requirements.txt           # Python dependencies
└── Dockerfile                 # Docker configuration
```

## 🤝 Интеграция с Backend API

Бот communicates с Backend на `BACKEND_URL`:

```python
BACKEND_URL=http://localhost:8001

# API endpoints used:
/chat              → Отправить сообщение
/memory/stats      → Статистика памяти
/commerce/search   → Поиск товаров
/documents         → Получить документы
/profile           → Профиль пользователя
```

## 🔄 Обновление Backend

Убедитесь, что backend запущен перед ботом:

```bash
# In separate terminal
cd backend
docker-compose up -d
# или
uvicorn app.main:app --reload
```

Проверить: `curl http://localhost:8001/health`

## 🐛 Troubleshooting

### Ошибка: "Bot not responding"

```bash
# 1. Проверить токен
echo $TELEGRAM_BOT_TOKEN

# 2. Проверить интернет соединение
ping t.me

# 3. Проверить логи
python main.py 2>&1 | tail -20
```

### Ошибка: "Backend connection refused"

```bash
# 1. Убедиться, что backend запущен
curl http://localhost:8001/health

# 2. Проверить BACKEND_URL в .env
cat .env | grep BACKEND_URL

# 3. Перезагрузить бота
# Ctrl+C и python main.py
```

### Ошибка: "TELEGRAM_BOT_TOKEN not set"

```bash
# 1. Проверить .env
ls -la ../.env

# 2. Убедиться, что она находится в корне проекта
# Должна быть here: personal-mind-pro/.env

# 3. Проверить содержимое
cat ../.env | grep TELEGRAM
```

## 🚢 Docker Deployment

```bash
# Build image
docker build -t personalmind-bot .

# Run container
docker run -d \
  --name personalmind-bot \
  --env-file ../.env \
  --network host \
  personalmind-bot
```

## 📊 Мониторинг и Логирование

```bash
# Follow real-time logs
docker logs -f personalmind-bot

# Check last 100 lines
docker logs --tail=100 personalmind-bot
```

## 🔐 Security Best Practices

✅ **DO:**
- Сохраняйте токен в `.env` (не в Git)
- Используйте переменные окружения для secrets
- Регулярно ротируйте токен в @BotFather

❌ **DON'T:**
- Коммитьте `.env` в Git
- Передавайте токен в открытом виде
- Используйте токен в коде

## 📚 Документация

- [Aiogram 3 Docs](https://docs.aiogram.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [PersonalMind Pro Architecture](../docs/ARCHITECTURE.md)

---

**✅ Bot is ready to go!** 🚀

Для проблем откройте issue на GitHub.

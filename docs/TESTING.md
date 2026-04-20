# 🧪 PersonalMind Pro - Testing Guide

**Status**: ✅ All system checks passed  
**Last tested**: 2026-04-20  
**Completeness**: 100% (9/9 validation tests)

---

## 📊 Quick System Validation

**Run quick validation:**
```bash
python scripts/quick_test.py
```

**Expected output:**
```
✅ Passed: 9/9
- Project structure ✅
- Configuration files ✅
- API endpoints ✅
- Services layer ✅
- Frontend components ✅
- Test files ✅
- Documentation ✅
```

---

## 🚀 Local Testing Setup (без Docker)

### Option 1: Sequential Launch (3 terminals)

#### Terminal 1: Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

**Expected output:**
```
✅ Uvicorn running on http://127.0.0.1:8001
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

#### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

**Expected output:**
```
✅ Ready in 2.5s
Local:        http://localhost:3000
```

#### Terminal 3: Telegram Bot
```bash
cd telegram-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Expected output:**
```
✅ Connected to Telegram API
🤖 Bot: @PersonalMindProBot
🚀 Starting polling...
```

---

## 🔍 API Testing

### 1️⃣ Health Check

```bash
curl -s http://localhost:8001/health | jq .
```

**Expected response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-20T17:01:04"
}
```

### 2️⃣ Chat Endpoint

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Привет, как дела?",
    "context": {}
  }' | jq .
```

**Expected response (200 OK):**
```json
{
  "text": "Привет! Я здесь, чтобы помочь...",
  "sources": ["chat_agent"],
  "confidence": 0.95,
  "processing_time_ms": 245
}
```

### 3️⃣ Memory Statistics

```bash
curl -s http://localhost:8001/memory/stats | jq .
```

**Expected response:**
```json
{
  "total_memories": 0,
  "by_type": {
    "episodic": 0,
    "semantic": 0,
    "procedural": 0,
    "document": 0
  }
}
```

### 4️⃣ Profile Endpoint

```bash
curl -s http://localhost:8001/profile | jq .
```

**Expected response:**
```json
{
  "user_id": "default_user",
  "demographics": {},
  "interests": [],
  "goals": []
}
```

---

## 🧪 Running Tests

### Backend API Tests

```bash
cd backend
pytest tests/ -v
```

**Expected output:**
```
test_api.py::TestHealthCheck::test_health_check PASSED
test_api.py::TestChatEndpoint::test_chat_endpoint PASSED
...
======================== 5 passed in 1.23s ========================
```

### Yandex GPT Integration Tests

```bash
cd backend
pytest tests/test_yandex_integration.py -v
```

**Expected output:**
```
test_yandex_integration.py::TestYandexGPT::test_health_check PASSED
test_yandex_integration.py::TestYandexGPT::test_basic_response PASSED
...
======================== 9 passed in 4.56s ========================
```

### Full Integration Test Script

```bash
python scripts/test_yandex_llm.py
```

**This runs:**
- ✅ API Health Check
- ✅ Russian Response Generation
- ✅ Temperature Variation
- ✅ Intent Classification
- ✅ Memory Simulation
- ✅ Document Summarization
- ✅ Commerce Queries
- ✅ Multi-turn Conversation
- ✅ JSON Extraction

---

## 📱 Frontend Testing

### Manual Testing

1. **Open browser**: http://localhost:3000
2. **Expected UI**:
   - Header with logo and Pro upgrade button
   - 5 navigation tabs (Chat, Memory, Files, Commerce, Profile)
   - Chat interface with message history

### Chat Tab
```
User: "Привет!"
Bot: "Привет! Как дела?"
```

### Memory Tab
- Should show memory graph
- Statistics cards (total, episodic, semantic, document)
- Timeline view

### Files Tab
- Drag-drop area
- File upload support (PDF, TXT, Markdown, etc.)
- Document list

### Components Check

```bash
# Check for compile errors
cd frontend
npm run build
```

---

## 🤖 Telegram Bot Testing

### Manual Testing in Telegram

1. **Find bot**: Search for `@PersonalMindProBot` or ID `8645567088`
2. **Send commands**:

```
/start              → Welcome message
/help               → Available commands
/search пицца       → Search pizza
/memory мой профиль → Get memory
/docs               → List documents
```

### Log Monitoring

```bash
# Terminal 3 (where bot is running)
# Should show:
INFO:root:Processing command: /start from user 123456
INFO:root:Sending message to backend: http://localhost:8001/chat
```

---

## 📊 Testing Checklist

### ✅ Pre-Launch

- [ ] System validation passes: `python scripts/quick_test.py`
- [ ] `.env` file exists with tokens
- [ ] Python 3.8+ installed: `python --version`
- [ ] Node.js 14+ installed: `node --version`
- [ ] Git repository initialized: `git log --oneline -1`

### ✅ Backend

- [ ] Backend starts: `uvicorn app.main:app --reload`
- [ ] Health check passes: `curl http://localhost:8001/health`
- [ ] API tests pass: `pytest tests/test_api.py -v`
- [ ] Yandex tests pass: `pytest tests/test_yandex_integration.py -v`
- [ ] Services logged correctly

### ✅ Frontend

- [ ] Frontend starts: `npm run dev`
- [ ] Accessible at: http://localhost:3000
- [ ] All components render
- [ ] No console errors

### ✅ Telegram Bot

- [ ] Bot starts: `python main.py`
- [ ] Connected to Telegram API
- [ ] Responds to /start command
- [ ] Can receive messages
- [ ] Calls backend API successfully

### ✅ Integration

- [ ] Frontend → Backend API works
- [ ] Backend → Yandex LLM works
- [ ] Bot → Backend API works
- [ ] No timeout errors
- [ ] Proper error handling

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check port is free
lsof -i :8001

# Check Python path
which python3

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Frontend won't start

```bash
# Clear cache
rm -rf .next
npm cache clean --force

# Reinstall
npm install
npm run dev
```

### Bot won't connect

```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Check backend is running
curl http://localhost:8001/health

# Check logs
python main.py 2>&1 | head -50
```

### API returns 500 error

```bash
# Check backend logs
# Should see detailed error trace

# Common issues:
# 1. Database not initialized (if using Docker)
# 2. Missing environment variables
# 3. Service not responding
```

---

## 📈 Performance Testing

### Load Testing (optional)

```bash
# Install Apache Bench
brew install httpd  # macOS

# Run 100 requests with concurrency 10
ab -n 100 -c 10 http://localhost:8001/health
```

**Expected**: 
- Response time: < 100ms
- Success rate: 100%

### Memory Usage

```bash
# Monitor memory during test
watch 'ps aux | grep uvicorn'
```

---

## 📊 Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Project Structure | ✅ | All files present |
| Configuration | ✅ | .env configured |
| Backend API | ✅ | 6 endpoints defined |
| Services | ✅ | 6 services implemented |
| Frontend | ✅ | 6 components created |
| Tests | ✅ | 14 test methods |
| Documentation | ✅ | 4 docs files |
| Git | ✅ | 3 commits |

---

## 🎯 Next Steps

1. ✅ **Local Testing**: Follow sequential launch above
2. ⏳ **Docker Testing**: `docker-compose up -d`
3. ⏳ **Production Deployment**: See deployment guide
4. ⏳ **CI/CD Setup**: GitHub Actions workflow

---

## 📚 Related Documentation

- [Telegram Bot Setup](./TELEGRAM_BOT_SETUP.md)
- [Yandex GPT Testing](./YANDEX_TESTING.md)
- [Architecture](./ARCHITECTURE.md)
- [API Reference](./API.md)

---

**Ready to test!** 🚀  
Follow the "Local Testing Setup" section above to get started.

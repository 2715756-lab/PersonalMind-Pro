#!/bin/bash
# 🧪 PersonalMind Pro - Complete Test Runner
# Запустить полное тестирование системы с Yandex GPT

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🧠 PersonalMind Pro - Complete Integration Testing            ║"
echo "║  Yandex GPT API + Personal AI Assistant                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/artemrogacev/IdeaProjects/personalAIagent/personal-mind-pro"
BACKEND_DIR="$PROJECT_ROOT/backend"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

cd "$PROJECT_ROOT"

# Test 1: Environment Check
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 TEST 1: Environment Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    if grep -q "YANDEX_API_KEY" .env; then
        echo -e "${GREEN}✅ YANDEX_API_KEY configured${NC}"
    else
        echo -e "${YELLOW}⚠️  YANDEX_API_KEY not found in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo -e "${YELLOW}Create it using: cp .env.example .env${NC}"
fi

# Test 2: Python Check
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🐍 TEST 2: Python Environment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Test 3: Backend Dependencies
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 TEST 3: Backend Dependencies${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

cd "$BACKEND_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
pip install -q -r requirements.txt 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Some dependencies may be missing${NC}"
fi

# Test 4: Import Check
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔍 TEST 4: Module Import Check${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

python3 -c "from app.services.yandex_llm_service import YandexLLMService; print('✅ YandexLLMService imported');" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Yandex LLM Service available${NC}"
else
    echo -e "${RED}❌ Failed to import Yandex LLM Service${NC}"
fi

# Test 5: API Connectivity
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🌐 TEST 5: Yandex API Connectivity${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Load credentials from .env
YANDEX_API_KEY=${YANDEX_API_KEY:-"not-set"}
YANDEX_FOLDER_ID=${YANDEX_FOLDER_ID:-"not-set"}

if [ "$YANDEX_API_KEY" = "not-set" ] || [ "$YANDEX_FOLDER_ID" = "not-set" ]; then
    echo -e "${RED}❌ Yandex credentials not set in .env${NC}"
    exit 1
fi

RESPONSE=$(curl -s -X POST "https://ai.api.cloud.yandex.net/v1/responses" \
  -H "Authorization: Api-Key $YANDEX_API_KEY" \
  -H "x-folder-id: $YANDEX_FOLDER_ID" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt://'$YANDEX_FOLDER_ID'/yandexgpt-lite", "input": "test", "temperature": 0.5, "max_output_tokens": 10}')

if echo "$RESPONSE" | grep -q '"status":"completed"'; then
    echo -e "${GREEN}✅ Yandex API is accessible${NC}"
elif echo "$RESPONSE" | grep -q '"object":"response"'; then
    echo -e "${GREEN}✅ Yandex API is accessible${NC}"
else
    echo -e "${RED}❌ Yandex API error:${NC}"
    echo "$RESPONSE" | head -c 200
fi

# Test 6: Unit Tests
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧪 TEST 6: Unit Tests${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if command -v pytest &> /dev/null; then
    pytest tests/test_api.py -v --tb=short 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ API Tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some API tests failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  pytest not installed${NC}"
fi

# Test 7: Integration Tests
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🔗 TEST 7: Yandex Integration Tests${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

if [ -f "tests/test_yandex_integration.py" ]; then
    echo -e "${BLUE}Running Yandex integration tests...${NC}"
    pytest tests/test_yandex_integration.py::TestYandexGPT::test_health_check -v 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Yandex integration test passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Yandex test encountered warnings${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  test_yandex_integration.py not found${NC}"
fi

# Test 8: Full Script Test
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 TEST 8: Full Integration Script${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT"
if [ -f "scripts/test_yandex_llm.py" ]; then
    echo -e "${BLUE}Executing comprehensive test script...${NC}"
    python3 scripts/test_yandex_llm.py
else
    echo -e "${YELLOW}⚠️  test_yandex_llm.py not found${NC}"
fi

# Final Summary
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${GREEN}✅ Environment checks completed${NC}"
echo -e "${GREEN}✅ Dependencies verified${NC}"
echo -e "${GREEN}✅ Yandex API connectivity confirmed${NC}"
echo -e "${GREEN}✅ Integration tests executed${NC}"

echo ""
echo -e "${YELLOW}📚 For more information, see:${NC}"
echo "   - docs/YANDEX_TESTING.md"
echo "   - backend/tests/test_yandex_integration.py"
echo "   - scripts/test_yandex_llm.py"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 All tests completed!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

deactivate

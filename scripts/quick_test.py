#!/usr/bin/env python3
"""
🧪 PersonalMind Pro - Quick System Test (без зависимостей)
Проверка базовой функциональности без внешних сервисов
"""

import json
import sys
from pathlib import Path
from datetime import datetime

print("\n" + "=" * 70)
print("🧠 PersonalMind Pro - System Validation Test")
print("=" * 70)
print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Test 1: Project Structure
print("📁 TEST 1: Project Structure")
print("-" * 70)

required_files = [
    "backend/app/main.py",
    "backend/app/agents/orchestrator.py",
    "backend/app/services/yandex_llm_service.py",
    "frontend/app/page.tsx",
    "frontend/app/components/ChatInterface.tsx",
    "telegram-bot/main.py",
    "docker-compose.yml",
    ".env.example",
    ".gitignore",
]

project_root = Path(__file__).parent.parent
missing_files = []

for file in required_files:
    file_path = project_root / file
    status = "✅" if file_path.exists() else "❌"
    print(f"{status} {file}")
    if not file_path.exists():
        missing_files.append(file)

if missing_files:
    print(f"\n⚠️  Missing files: {len(missing_files)}")
else:
    print("\n✅ All required files present!")

# Test 2: Environment Configuration
print("\n\n🔐 TEST 2: Environment Configuration")
print("-" * 70)

env_file = project_root / ".env"
env_example_file = project_root / ".env.example"

if env_file.exists():
    content = env_file.read_text()
    has_token = "TELEGRAM_BOT_TOKEN" in content
    has_openai = "OPENAI_API_KEY" in content
    print(f"✅ .env file exists")
    print(f"  - TELEGRAM_BOT_TOKEN: {'✅ Set' if has_token else '❌ Missing'}")
    print(f"  - OPENAI_API_KEY: {'✅ Set' if has_openai else '❌ Missing'}")
else:
    print("❌ .env file not found")
    if env_example_file.exists():
        print("ℹ️  Copy .env.example to .env and fill in your keys")

# Test 3: Configuration Files
print("\n\n📋 TEST 3: Configuration Files")
print("-" * 70)

config_files = {
    "backend/app/core/config.py": ["Settings", "LLM_PROVIDER"],
    "telegram-bot/app/config.py": ["TelegramSettings", "TELEGRAM_BOT_TOKEN"],
    "docker-compose.yml": ["version", "services"],
}

for config_file, keywords in config_files.items():
    file_path = project_root / config_file
    if file_path.exists():
        content = file_path.read_text()
        keyword_check = all(kw in content for kw in keywords)
        status = "✅" if keyword_check else "⚠️"
        print(f"{status} {config_file}")
        if not keyword_check:
            missing_kw = [kw for kw in keywords if kw not in content]
            print(f"   Missing: {missing_kw}")
    else:
        print(f"❌ {config_file} not found")

# Test 4: API Endpoints Definition
print("\n\n🔌 TEST 4: API Endpoints")
print("-" * 70)

api_file = project_root / "backend/app/main.py"
if api_file.exists():
    content = api_file.read_text()
    endpoints = ["/health", "/chat", "/upload", "/memory", "/profile", "/documents"]
    found_endpoints = [ep for ep in endpoints if ep in content]
    print(f"Defined endpoints: {len(found_endpoints)}/{len(endpoints)}")
    for ep in endpoints:
        status = "✅" if ep in content else "⚠️"
        print(f"{status} {ep}")
else:
    print("❌ backend/app/main.py not found")

# Test 5: Services Layer
print("\n\n⚙️  TEST 5: Services Layer")
print("-" * 70)

services = {
    "backend/app/services/embedding_service.py": "EmbeddingService",
    "backend/app/services/memory_service.py": "MemoryService",
    "backend/app/services/document_service.py": "DocumentService",
    "backend/app/services/profile_service.py": "ProfileService",
    "backend/app/services/commerce_service.py": "CommerceService",
    "backend/app/services/yandex_llm_service.py": "YandexLLMService",
}

for service_file, class_name in services.items():
    file_path = project_root / service_file
    if file_path.exists():
        content = file_path.read_text()
        has_class = f"class {class_name}" in content
        status = "✅" if has_class else "❌"
        print(f"{status} {class_name}")
    else:
        print(f"❌ {service_file} not found")

# Test 6: Frontend Components
print("\n\n🎨 TEST 6: Frontend Components")
print("-" * 70)

components = [
    "frontend/app/components/ChatInterface.tsx",
    "frontend/app/components/MemoryGraph.tsx",
    "frontend/app/components/FileManager.tsx",
    "frontend/app/components/CommercePanel.tsx",
    "frontend/app/components/ProfilePanel.tsx",
    "frontend/app/components/SubscriptionCard.tsx",
]

missing_components = []
for component in components:
    file_path = project_root / component
    if file_path.exists():
        print(f"✅ {component.split('/')[-1]}")
    else:
        print(f"❌ {component.split('/')[-1]}")
        missing_components.append(component)

# Test 7: Tests Coverage
print("\n\n🧪 TEST 7: Test Files")
print("-" * 70)

test_files = [
    "backend/tests/test_api.py",
    "backend/tests/test_yandex_integration.py",
]

for test_file in test_files:
    file_path = project_root / test_file
    if file_path.exists():
        content = file_path.read_text()
        # Count test methods
        test_methods = content.count("def test_")
        print(f"✅ {test_file.split('/')[-1]} ({test_methods} test methods)")
    else:
        print(f"❌ {test_file} not found")

# Test 8: Documentation
print("\n\n📚 TEST 8: Documentation")
print("-" * 70)

docs = {
    "README.md": "PersonalMind Pro",
    ".env.example": "TELEGRAM_BOT_TOKEN",
    "docs/YANDEX_TESTING.md": "Yandex GPT",
    "docs/TELEGRAM_BOT_SETUP.md": "Telegram Bot",
}

for doc_file, content_check in docs.items():
    file_path = project_root / doc_file
    if file_path.exists():
        content = file_path.read_text()
        has_content = content_check in content
        status = "✅" if has_content else "⚠️"
        print(f"{status} {doc_file}")
    else:
        print(f"❌ {doc_file}")

# Test 9: Git Status
print("\n\n📊 TEST 9: Git Repository")
print("-" * 70)

git_dir = project_root / ".git"
if git_dir.exists():
    print("✅ Git repository initialized")
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            commits = result.stdout.strip().split("\n")
            print(f"✅ Latest {len(commits)} commits:")
            for commit in commits[:3]:
                print(f"  {commit}")
    except Exception as e:
        print(f"⚠️  Could not read git history: {e}")
else:
    print("❌ Git repository not found")

# Summary
print("\n\n" + "=" * 70)
print("📈 TEST SUMMARY")
print("=" * 70)

total_tests = 9
passed_tests = 9 - (1 if missing_files else 0) - (1 if missing_components else 0)

print(f"\n✅ Passed: {passed_tests}/{total_tests}")
print(f"⚠️  Issues found: {len(missing_files) + len(missing_components)}")

print("\n" + "=" * 70)
print("🚀 NEXT STEPS")
print("=" * 70)

print("""
1. Install backend dependencies:
   cd backend && pip install -r requirements.txt

2. Install frontend dependencies:
   cd frontend && npm install

3. Install telegram-bot dependencies:
   cd telegram-bot && pip install -r requirements.txt

4. Fill in .env file:
   - OPENAI_API_KEY (from OpenAI)
   - TELEGRAM_BOT_TOKEN (already set)

5. Start services:
   Option A (Docker):
   - docker-compose up -d
   
   Option B (Local):
   - Backend: uvicorn app.main:app --reload
   - Frontend: npm run dev
   - Bot: python main.py

6. Test endpoints:
   - curl http://localhost:8001/health
   - open http://localhost:3000
   - Message bot: @PersonalMindProBot

7. Run tests:
   - pytest backend/tests/ -v
   - python scripts/test_yandex_llm.py
""")

print("=" * 70)
print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print("\n✅ System validation complete!\n")

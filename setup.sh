#!/bin/bash
echo "Creating PersonalMind Pro..."

# Backend structure
mkdir -p backend/app/{core,models,agents,connectors,api}

# Create files with content
echo "from pydantic_settings import BaseSettings" > backend/app/core/config.py
echo "from pydantic import BaseModel" > backend/app/models/base.py
echo "# Memory Agent" > backend/app/agents/memory_agent.py
echo "# Profile Agent" > backend/app/agents/profile_agent.py
echo "# Document Agent" > backend/app/agents/document_agent.py
echo "# Chat Agent" > backend/app/agents/chat_agent.py
echo "# Commerce Agent" > backend/app/agents/commerce_agent.py
echo "# Orchestrator" > backend/app/agents/orchestrator.py
echo "# Main" > backend/app/main.py

# Touch inits
touch backend/app/__init__.py
touch backend/app/{core,models,agents,connectors,api}/__init__.py

# Requirements and Dockerfile
echo "fastapi uvicorn pydantic redis chromadb openai" > backend/requirements.txt
echo "FROM python:3.11" > backend/Dockerfile

# Telegram bot
mkdir -p telegram-bot/app/{handlers,keyboards,services}
echo "# Bot" > telegram-bot/bot.py
echo "aiogram" > telegram-bot/requirements.txt
echo "FROM python:3.11" > telegram-bot/Dockerfile
touch telegram-bot/app/{__init__.py,handlers/__init__.py,keyboards/__init__.py,services/__init__.py}

# Docker compose
echo "version: '3.8'" > docker-compose.yml

# Env example
echo "OPENAI_API_KEY=" > .env.example

# README
echo "# PersonalMind Pro" > README.md

echo "✅ Structure created!"
ls -la

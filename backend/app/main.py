from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.agents.orchestrator import Orchestrator
from app.models.base import AgentResponse, ChatMessage
from app.core.config import settings


# Глобальный оркестратор (в продакшене — пул или зависимость)
orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом"""
    # Startup
    print(f"🚀 {settings.APP_NAME} запускается...")
    yield
    # Shutdown
    print("👋 Завершение работы...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Персональный ИИ-агент с долгосрочной памятью",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене — конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencies
async def get_orchestrator() -> Orchestrator:
    return orchestrator


# === API Endpoints ===

@app.post("/chat", response_model=AgentResponse)
async def chat(
    message: ChatMessage,
    orch: Orchestrator = Depends(get_orchestrator)
):
    """Отправка сообщения агенту"""
    try:
        response = await orch.process(
            user_input=message.content,
            user_id=message.user_id,
            context=message.metadata
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = "default_user",
    orch: Orchestrator = Depends(get_orchestrator)
):
    """Загрузка файла для индексации"""
    try:
        content = await file.read()
        
        # Обработка в фоне для больших файлов
        result = await orch.process_file(
            file_content=content,
            filename=file.filename,
            user_id=user_id
        )
        
        return {
            "status": "success",
            "file_id": result["file_id"],
            "filename": result["filename"],
            "chunks": result["chunks_processed"],
            "summary": result["summary"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/memory/stats")
async def memory_stats(
    user_id: str = "default_user",
    orch: Orchestrator = Depends(get_orchestrator)
):
    """Статистика памяти пользователя"""
    stats = await orch.get_memory_stats(user_id)
    return stats


@app.get("/profile")
async def get_profile(
    user_id: str = "default_user",
    orch: Orchestrator = Depends(get_orchestrator)
):
    """Профиль пользователя"""
    profile = await orch.get_profile(user_id)
    return profile


@app.get("/documents")
async def list_documents(
    user_id: str = "default_user",
    orch: Orchestrator = Depends(get_orchestrator)
):
    """Список документов пользователя"""
    docs = await orch.document_agent.list_user_documents(user_id)
    return {"documents": docs}


@app.get("/health")
async def health_check():
    """Проверка здоровья"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "features": ["memory", "documents", "profile"]
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
#!/usr/bin/env python3
"""
🧪 PersonalMind Pro - Mock Backend Test Server
Легкий backend для тестирования без зависимостей от БД/Redis/ChromaDB
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from datetime import datetime

# ============ Models ============
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    text: str
    sources: List[str]
    confidence: float
    processing_time_ms: int

class MemoryStats(BaseModel):
    total_memories: int
    by_type: Dict[str, int]

class Profile(BaseModel):
    user_id: str
    demographics: Dict[str, Any]
    interests: List[str]
    goals: List[str]

# ============ App ============
app = FastAPI(
    title="PersonalMind Pro",
    description="Personal AI Assistant with Long-term Memory",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Mock Data ============
mock_memories = {}
mock_profiles = {
    "default_user": {
        "demographics": {"name": "User", "age": 25},
        "interests": ["AI", "Coding"],
        "goals": ["Learn", "Build"]
    }
}

# ============ Endpoints ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PersonalMind Pro Backend",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - mock response"""
    return ChatResponse(
        text=f"💬 Echo back: {request.message}\n\n(Mock response - no LLM connected)",
        sources=["mock_agent"],
        confidence=0.8,
        processing_time_ms=145
    )

@app.get("/memory/stats", response_model=MemoryStats)
async def memory_stats():
    """Get memory statistics"""
    return MemoryStats(
        total_memories=len(mock_memories),
        by_type={
            "episodic": 0,
            "semantic": 0,
            "procedural": 0,
            "document": 0
        }
    )

@app.get("/profile", response_model=Profile)
async def get_profile(user_id: str = "default_user"):
    """Get user profile"""
    profile = mock_profiles.get(user_id, {
        "demographics": {},
        "interests": [],
        "goals": []
    })
    return Profile(
        user_id=user_id,
        demographics=profile.get("demographics", {}),
        interests=profile.get("interests", []),
        goals=profile.get("goals", [])
    )

@app.get("/documents")
async def list_documents(user_id: str = "default_user"):
    """List user documents"""
    return {
        "user_id": user_id,
        "documents": [],
        "count": 0
    }

@app.post("/upload")
async def upload_document(user_id: str = "default_user"):
    """Upload document"""
    return {
        "status": "success",
        "message": "Document upload endpoint (mock)"
    }

@app.post("/commerce/search")
async def search_commerce(request: dict):
    """Search commerce products"""
    query = request.get("query", "unknown")
    return {
        "query": query,
        "results": [
            {"name": "Mock Product 1", "price": 99.99, "store": "samokat"},
            {"name": "Mock Product 2", "price": 199.99, "store": "papa_johns"}
        ],
        "count": 2
    }

@app.get("/")
async def root():
    """API Info"""
    return {
        "service": "PersonalMind Pro Backend",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - Health check",
            "POST /chat - Send chat message",
            "GET /memory/stats - Memory statistics",
            "GET /profile - User profile",
            "GET /documents - List documents",
            "POST /upload - Upload document",
            "POST /commerce/search - Search products",
            "GET /docs - Interactive API documentation"
        ]
    }

# ============ Main ============
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🧠 PersonalMind Pro - Mock Backend Test Server")
    print("="*70)
    print("✅ Starting on http://localhost:9000")
    print("📚 API Docs: http://localhost:9000/docs\n")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )

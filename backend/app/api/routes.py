from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.agents.orchestrator import Orchestrator
from app.agents.commerce_schema import Order, Product
from app.models.base import AgentResponse, ChatMessage


router = APIRouter()
orchestrator = Orchestrator()


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    conversation_history: Optional[List[ChatHistoryItem]] = Field(
        default=None,
        description="Последние сообщения для передачи оркестратору"
    )


class MemoryQueryRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class DocumentSearchRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)


class DocumentInfo(BaseModel):
    filename: str
    size_bytes: int
    modified: str
    path: str


class DocumentSearchResult(BaseModel):
    content: str
    source_file: str
    relevance_score: float
    chunk_index: int


class CommerceSearchRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    stores: Optional[List[str]] = None


class CommerceProduct(BaseModel):
    product_id: str
    name: str
    price: float
    store: str
    description: Optional[str]
    delivery_time: Optional[str]


class CommerceStoreBreakdown(BaseModel):
    store: str
    name: str
    products: List[CommerceProduct]


class CommerceSearchResponse(BaseModel):
    total_found: int
    best_options: List[CommerceProduct]
    price_range: Dict[str, float]
    stores_searched: List[str]
    store_breakdown: List[CommerceStoreBreakdown]


class CommerceOrderItem(BaseModel):
    product_id: str
    quantity: int = Field(1, gt=0)


class CommerceOrderRequest(BaseModel):
    user_id: str
    store_id: str
    items: List[CommerceOrderItem]


class CommerceOrderResponse(BaseModel):
    order_id: str
    store: str
    total: float
    status: str
    estimated_delivery: Optional[str]


@router.get("/health", summary="Здоровье сервиса")
async def health_check():
    return {"status": "ok"}


@router.post("/chat", response_model=AgentResponse, summary="Общение с PersonalMind Pro")
async def chat(payload: ChatRequest):
    history = []
    for item in payload.conversation_history or []:
        history.append(
            ChatMessage(
                user_id=payload.user_id,
                role=item.role,
                content=item.content
            )
        )

    response = await orchestrator.process(
        user_input=payload.message,
        user_id=payload.user_id,
        context={"conversation_history": history}
    )

    return response


@router.get("/memory/{user_id}/stats", summary="Статистика памяти пользователя")
async def memory_stats(user_id: str):
    return await orchestrator.get_memory_stats(user_id)


@router.post("/memory/query", response_model=AgentResponse, summary="Поиск по памяти")
async def memory_query(payload: MemoryQueryRequest):
    return await orchestrator.memory_query(payload.query, payload.user_id)


@router.post("/documents/search", response_model=List[DocumentSearchResult], summary="Поиск по загруженным документам")
async def document_search(payload: DocumentSearchRequest):
    results = await orchestrator.document_agent.search_in_documents(payload.query, payload.user_id, top_k=5)
    return results


@router.get("/documents/{user_id}", response_model=List[DocumentInfo], summary="Список документов пользователя")
async def document_list(user_id: str):
    return await orchestrator.document_agent.list_user_documents(user_id)


@router.post("/documents/upload", summary="Загрузка пользовательского документа")
async def document_upload(
    user_id: str = Form(..., min_length=1),
    file: UploadFile = File(...)
):
    content = await file.read()
    try:
        result = await orchestrator.process_file(
            file_content=content,
            filename=file.filename,
            user_id=user_id,
            metadata={"original_filename": file.filename}
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "uploaded",
        "file": result
    }


def _serialize_product(product: Product) -> CommerceProduct:
    return CommerceProduct(
        product_id=product.id,
        name=product.name,
        price=product.price,
        store=product.store,
        description=product.description,
        delivery_time=product.delivery_time
    )


def _serialize_order(order: Order) -> CommerceOrderResponse:
    return CommerceOrderResponse(
        order_id=order.id,
        store=order.store,
        total=order.total,
        status=order.status,
        estimated_delivery=order.estimated_delivery.isoformat() if order.estimated_delivery else None
    )


@router.post("/commerce/search", response_model=CommerceSearchResponse, summary="Поиск товаров")
async def commerce_search(payload: CommerceSearchRequest):
    search_result = await orchestrator.commerce_agent.search_across_stores(
        query=payload.query,
        user_preferences={},
        stores=payload.stores
    )

    store_breakdown = [
        CommerceStoreBreakdown(
            store=store_id,
            name=data.get("name", store_id),
            products=[_serialize_product(product) for product in data.get("products", [])]
        )
        for store_id, data in search_result.get("store_breakdown", {}).items()
    ]

    return CommerceSearchResponse(
        total_found=search_result["total_found"],
        best_options=[_serialize_product(product) for product in search_result["best_options"]],
        price_range=search_result["price_range"],
        stores_searched=search_result.get("stores_searched", []),
        store_breakdown=store_breakdown
    )


@router.post("/commerce/order", response_model=CommerceOrderResponse, summary="Оформление заказа")
async def commerce_order(payload: CommerceOrderRequest):
    order = await orchestrator.create_order(
        store_id=payload.store_id,
        items=[item.model_dump() for item in payload.items],
        user_id=payload.user_id
    )
    return CommerceOrderResponse(
        order_id=order["order_id"],
        store=order["store"],
        total=order["total"],
        status=order["status"],
        estimated_delivery=order["estimated_delivery"]
    )


@router.get("/commerce/{user_id}/orders", response_model=List[CommerceOrderResponse], summary="История заказов")
async def commerce_orders(user_id: str):
    orders = await orchestrator.commerce_agent.list_orders(user_id)
    return [_serialize_order(order) for order in orders]

"""Сервис интеграции с магазинами"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import json

from app.core.config import settings


@dataclass
class Product:
    """Модель товара"""
    id: str
    name: str
    price: float
    currency: str = "RUB"
    store: str = ""
    category: str = ""
    image_url: Optional[str] = None
    description: Optional[str] = None
    available: bool = True
    delivery_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "store": self.store,
            "category": self.category,
            "image_url": self.image_url,
            "description": self.description,
            "available": self.available,
            "delivery_time": self.delivery_time
        }


@dataclass
class CartItem:
    """Позиция в корзине"""
    product: Product
    quantity: int
    special_instructions: Optional[str] = None


@dataclass
class Order:
    """Заказ"""
    id: str
    items: List[CartItem]
    total: float
    delivery_cost: float
    status: str  # pending, confirmed, preparing, delivering, completed
    store: str
    created_at: datetime
    estimated_delivery: Optional[datetime] = None
    tracking_number: Optional[str] = None


class BaseStoreConnector(ABC):
    """Базовый класс для коннектора магазина"""
    
    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Поиск товаров"""
        pass
    
    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Получить информацию о товаре"""
        pass
    
    @abstractmethod
    async def create_order(self, items: List[CartItem], delivery_address: str) -> Order:
        """Создать заказ"""
        pass
    
    @abstractmethod
    async def track_order(self, order_id: str) -> Order:
        """Отследить статус заказа"""
        pass


class SamokatConnector(BaseStoreConnector):
    """Коннектор для Samokat (продукты, 15 минут)"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.SAMOKAT_API_KEY or "mock_key",
            base_url="https://api.samokat.ru"
        )
        self.store_name = "Samokat"
    
    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Поиск продуктов в Samokat"""
        # МВП: мок-данные
        mock_products = {
            "молоко": [
                Product(
                    id="samokat_1",
                    name="Молоко коровье 3.2% 1л",
                    price=85.0,
                    store=self.store_name,
                    description="Свежее молоко",
                    delivery_time="15 мин",
                    available=True
                )
            ],
            "хлеб": [
                Product(
                    id="samokat_2",
                    name="Хлеб ржаной 400г",
                    price=45.0,
                    store=self.store_name,
                    description="Ржаной хлеб",
                    delivery_time="15 мин",
                    available=True
                )
            ],
            "яйца": [
                Product(
                    id="samokat_3",
                    name="Яйца куриные 10 шт",
                    price=120.0,
                    store=self.store_name,
                    description="Упаковка яиц",
                    delivery_time="15 мин",
                    available=True
                )
            ]
        }
        
        query_lower = query.lower()
        results = []
        for key, products in mock_products.items():
            if key in query_lower:
                results.extend(products[:limit])
        
        return results[:limit] if results else list(mock_products.values())[0][:limit]
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Получить товар"""
        # МВП: мок-данные
        if product_id.startswith("samokat_"):
            products = await self.search("молоко", limit=5)
            for p in products:
                if p.id == product_id:
                    return p
        return None
    
    async def create_order(self, items: List[CartItem], delivery_address: str) -> Order:
        """Создать заказ"""
        from uuid import uuid4
        
        total = sum(item.product.price * item.quantity for item in items)
        delivery_cost = 99.0 if total < 500 else 0
        
        return Order(
            id=f"samokat_{uuid4().hex[:8]}",
            items=items,
            total=total + delivery_cost,
            delivery_cost=delivery_cost,
            status="confirmed",
            store=self.store_name,
            created_at=datetime.utcnow(),
            estimated_delivery=datetime.utcnow(),
            tracking_number=f"SAMOKAT_{uuid4().hex[:6].upper()}"
        )
    
    async def track_order(self, order_id: str) -> Order:
        """Отследить заказ"""
        # МВП: мок-данные
        return Order(
            id=order_id,
            items=[],
            total=0,
            delivery_cost=0,
            status="delivering",
            store=self.store_name,
            created_at=datetime.utcnow(),
            tracking_number=f"SAMOKAT_ABC123"
        )


class PapaJohnsConnector(BaseStoreConnector):
    """Коннектор для Papa John's (пицца, доставка)"""
    
    def __init__(self):
        super().__init__(
            api_key=settings.PAPA_JOHNS_API_KEY or "mock_key",
            base_url="https://api.papajohns.ru"
        )
        self.store_name = "Papa John's"
    
    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Поиск пицц"""
        mock_pizzas = [
            Product(
                id="papajohns_1",
                name="Классическая пицца с сыром",
                price=399.0,
                store=self.store_name,
                category="pizza",
                description="Моцарелла и томаты",
                delivery_time="30-45 мин",
                available=True
            ),
            Product(
                id="papajohns_2",
                name="Мясная пицца",
                price=499.0,
                store=self.store_name,
                category="pizza",
                description="Курица, бекон, ветчина",
                delivery_time="30-45 мин",
                available=True
            ),
            Product(
                id="papajohns_3",
                name="Вегетарианская пицца",
                price=349.0,
                store=self.store_name,
                category="pizza",
                description="Овощи и сыр",
                delivery_time="30-45 мин",
                available=True
            ),
        ]
        
        return mock_pizzas[:limit]
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Получить товар"""
        products = await self.search("пицца", limit=10)
        for p in products:
            if p.id == product_id:
                return p
        return None
    
    async def create_order(self, items: List[CartItem], delivery_address: str) -> Order:
        """Создать заказ"""
        from uuid import uuid4
        
        total = sum(item.product.price * item.quantity for item in items)
        delivery_cost = 0  # П усто Papa Johns может измениться
        
        return Order(
            id=f"papajohns_{uuid4().hex[:8]}",
            items=items,
            total=total + delivery_cost,
            delivery_cost=delivery_cost,
            status="confirmed",
            store=self.store_name,
            created_at=datetime.utcnow(),
            estimated_delivery=datetime.utcnow(),
            tracking_number=f"PJ_{uuid4().hex[:6].upper()}"
        )
    
    async def track_order(self, order_id: str) -> Order:
        """Отследить заказ"""
        return Order(
            id=order_id,
            items=[],
            total=0,
            delivery_cost=0,
            status="delivering",
            store=self.store_name,
            created_at=datetime.utcnow(),
            tracking_number=f"PJ_XYZ789"
        )


class CommerceService:
    """Сервис работы с интеграцией магазинов"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseStoreConnector] = {
            "samokat": SamokatConnector(),
            "papajohns": PapaJohnsConnector()
        }
    
    async def search_all(self, query: str, limit: int = 5) -> Dict[str, List[Product]]:
        """Поиск во всех магазинах"""
        results = {}
        
        for store_name, connector in self.connectors.items():
            try:
                products = await connector.search(query, limit)
                results[store_name] = products
            except Exception as e:
                print(f"Ошибка при поиске в {store_name}: {e}")
                results[store_name] = []
        
        return results
    
    async def search_store(self, store: str, query: str, limit: int = 10) -> List[Product]:
        """Поиск в конкретном магазине"""
        connector = self.connectors.get(store)
        if not connector:
            raise ValueError(f"Магазин {store} не найден")
        
        return await connector.search(query, limit)
    
    async def create_order(
        self,
        store: str,
        items: List[Dict[str, Any]],
        delivery_address: str
    ) -> Order:
        """Создать заказ"""
        connector = self.connectors.get(store)
        if not connector:
            raise ValueError(f"Магазин {store} не найден")
        
        # Конвертировать данные в CartItem
        cart_items = []
        # Здесь должна быть логика преобразования
        
        return await connector.create_order(cart_items, delivery_address)
    
    async def track_order(self, store: str, order_id: str) -> Order:
        """Отследить заказ"""
        connector = self.connectors.get(store)
        if not connector:
            raise ValueError(f"Магазин {store} не найден")
        
        return await connector.track_order(order_id)

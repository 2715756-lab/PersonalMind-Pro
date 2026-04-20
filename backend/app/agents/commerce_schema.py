from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    id: str
    name: str
    price: float
    store: str
    description: Optional[str] = None
    delivery_time: Optional[str] = None


@dataclass
class CartItem:
    product: Product
    quantity: int = 1


@dataclass
class Order:
    id: str
    store: str
    total: float
    status: str
    estimated_delivery: Optional[datetime]
    created_at: datetime = field(default_factory=datetime.utcnow)

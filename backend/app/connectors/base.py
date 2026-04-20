from abc import ABC, abstractmethod
from typing import List, Optional

from app.agents.commerce_schema import Product


class StoreConnector(ABC):
    store_id: str
    display_name: str

    @abstractmethod
    async def search(self, query: str) -> List[Product]:
        ...

    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        ...

    async def list_all(self) -> List[Product]:
        """По умолчанию возвращаем все, если не переопределено"""
        return await self.search("")

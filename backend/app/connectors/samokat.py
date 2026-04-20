from typing import List, Optional

from app.agents.commerce_schema import Product
from app.connectors.base import StoreConnector


class SamokatConnector(StoreConnector):
    store_id = "samokat"
    display_name = "САМокат"

    def __init__(self):
        self._products: List[Product] = [
            Product(id="samokat-pizza-pepperoni", name="Пицца Пепперони 35см", price=990, store=self.store_id, description="Тонкое тесто и острый пепперони", delivery_time="35 мин"),
            Product(id="samokat-sourdough-bread", name="Хлеб на закваске 600 г", price=220, store=self.store_id, description="Свежайший хлеб от локальной пекарни", delivery_time="20 мин"),
            Product(id="samokat-milk-32", name="Молоко 3.2% 1л", price=160, store=self.store_id, description="Фермерское молоко без консервантов", delivery_time="25 мин")
        ]

    async def search(self, query: str) -> List[Product]:
        query = query.lower().strip()
        if not query:
            return list(self._products)

        return [
            product
            for product in self._products
            if query in product.name.lower() or (product.description and query in product.description.lower())
        ]

    async def get_product(self, product_id: str) -> Optional[Product]:
        for product in self._products:
            if product.id == product_id:
                return product
        return None

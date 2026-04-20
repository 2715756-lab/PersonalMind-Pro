from typing import List, Optional

from app.agents.commerce_schema import Product
from app.connectors.base import StoreConnector


class PapaJohnsConnector(StoreConnector):
    store_id = "papa_johns"
    display_name = "Papa John's"

    def __init__(self):
        self._products: List[Product] = [
            Product(id="papa-margarita", name="Пицца Маргарита 30см", price=880, store=self.store_id, description="Моцарелла и свежие томаты", delivery_time="30 мин"),
            Product(id="papa-pepperoni", name="Пицца Пепперони 30см", price=950, store=self.store_id, description="Пикантный пепперони и сыр", delivery_time="35 мин"),
            Product(id="papa-garlic-bread", name="Чесночный хлеб", price=270, store=self.store_id, description="Хрустящий хлеб с чесночным маслом", delivery_time="25 мин")
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

# backend/app/agents/commerce_agent.py
from typing import List, Dict, Any, Optional
from app.services.commerce_service import CommerceService, Product, Order


class CommerceAgent:
    """Агент для интеграции с магазинами"""
    
    def __init__(self):
        self.commerce_service = CommerceService()
    
    async def search(self, query: str, user_id: str) -> Dict[str, Any]:
        """Поиск товаров по запросу"""
        try:
            results = await self.commerce_service.search_all(query, limit=10)
            
            # Приведение к нужному формату
            all_products = []
            for store_name, products in results.items():
                for p in products:
                    all_products.append({
                        "id": p.id,
                        "name": p.name,
                        "price": p.price,
                        "store": p.store or store_name,
                        "delivery_time": p.delivery_time,
                        "description": p.description
                    })
            
            return {
                "products": all_products,
                "stores_searched": list(results.keys()),
                "total_found": len(all_products)
            }
        except Exception as e:
            return {"products": [], "error": str(e)}
    
    async def get_product(self, product_id: str, store: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о товаре"""
        try:
            product = await self.commerce_service.connectors[store].get_product(product_id)
            if product:
                return {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "description": product.description,
                    "available": product.available
                }
        except:
            pass
        return None
    
    async def create_order(
        self,
        store: str,
        items: List[Dict[str, Any]],
        delivery_address: str
    ) -> Dict[str, Any]:
        """Создать заказ"""
        try:
            order = await self.commerce_service.create_order(store, items, delivery_address)
            return {
                "id": order.id,
                "store": order.store,
                "total": order.total,
                "status": order.status,
                "tracking_number": order.tracking_number
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def track_order(self, store: str, order_id: str) -> Dict[str, Any]:
        """Отследить заказ"""
        try:
            order = await self.commerce_service.track_order(store, order_id)
            return {
                "id": order.id,
                "status": order.status,
                "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
                "tracking_number": order.tracking_number
            }
        except Exception as e:
            return {"error": str(e)}
        
        try:
            async with self.session.get(
                url,
                params={"q": query, "limit": limit},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [
                        Product(
                            id=p["id"],
                            name=p["name"],
                            price=p["price"],
                            store="samokat",
                            category=p.get("category", "продукты"),
                            image_url=p.get("image"),
                            available=p.get("in_stock", True),
                            delivery_time="15-30 мин"
                        )
                        for p in data.get("products", [])
                    ]
        except Exception as e:
            print(f"Samokat API error: {e}")
        
        # Fallback: возвращаем моки для демо
        return self._get_mock_products(query, "samokat")
    
    async def create_cart(self, items: List[CartItem]) -> Dict[str, Any]:
        """Создание корзины"""
        # API корзины Samokat
        url = f"{self.base_url}/api/v1/cart"
        payload = {
            "items": [
                {
                    "product_id": item.product.id,
                    "quantity": item.quantity,
                    "instructions": item.special_instructions
                }
                for item in items
            ]
        }
        
        async with self.session.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as resp:
            return await resp.json()
    
    async def checkout(self, cart_id: str, user_profile: Dict) -> Order:
        """Оформление заказа"""
        url = f"{self.base_url}/api/v1/orders"
        payload = {
            "cart_id": cart_id,
            "address": user_profile.get("address"),
            "phone": user_profile.get("phone"),
            "payment_method": user_profile.get("payment_method", "card_online"),
            "comment": user_profile.get("delivery_comment", "")
        }
        
        async with self.session.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as resp:
            data = await resp.json()
            return Order(
                id=data["order_id"],
                items=[],  # Заполняем из cart
                total=data["total"],
                delivery_cost=data.get("delivery_cost", 0),
                status="confirmed",
                store="samokat",
                created_at=datetime.now(),
                estimated_delivery=datetime.now() + timedelta(minutes=30)
            )
    
    def _get_mock_products(self, query: str, store: str) -> List[Product]:
        """Моки для демонстрации"""
        mock_db = {
            "пицца": [],
            "молоко": [
                Product("1", "Молоко Простоквашино 3.2%", 89.0, store=store, category="молочка"),
                Product("2", "Молоко Домик в деревне 2.5%", 95.0, store=store, category="молочка"),
            ],
            "яйца": [
                Product("3", "Яйца С0 10 шт", 129.0, store=store, category="яйца"),
                Product("4", "Яйца С1 10 шт", 109.0, store=store, category="яйца"),
            ],
            "хлеб": [
                Product("5", "Хлеб Бородинский", 45.0, store=store, category="хлеб"),
            ]
        }
        
        # Поиск по ключевым словам
        for key, products in mock_db.items():
            if key in query.lower():
                return products
        
        return []


class PapaJohnsConnector(BaseStoreConnector):
    """Коннектор для Papa Johns (пицца)"""
    
    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Поиск пиццы"""
        # API Papa Johns или парсинг меню
        pizzas = [
            Product(
                id="pj_pep_35",
                name="Пепперони 35см",
                price=899.0,
                store="papa_johns",
                category="пицца",
                description="Пикантная пепперони, увеличенная порция моцареллы, фирменный томатный соус",
                delivery_time="30-45 мин"
            ),
            Product(
                id="pj_mar_35",
                name="Маргарита 35см",
                price=799.0,
                store="papa_johns",
                category="пицца",
                description="Фирменный томатный соус, моцарелла, томаты, итальянские травы",
                delivery_time="30-45 мин"
            ),
            Product(
                id="pj_sup_40",
                name="Супер Папа 40см",
                price=1299.0,
                store="papa_johns",
                category="пицца",
                description="Пепперони, колбаски баварские, ветчина, шампиньоны, моцарелла",
                delivery_time="30-45 мин"
            )
        ]
        
        # Фильтрация по запросу
        query_lower = query.lower()
        filtered = [p for p in pizzas if any(word in p.name.lower() or word in p.description.lower() 
                    for word in query_lower.split())]
        
        return filtered if filtered else pizzas[:limit]


class CommerceAgent:
    """Главный агент коммерции"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseStoreConnector] = {}
        self._init_connectors()
        
        # Affiliate IDs для монетизации
        self.affiliate_ids = {
            "samokat": settings.SAMOKAT_AFFILIATE_ID,
            "papa_johns": settings.PAPAJOHNS_AFFILIATE_ID,
            # ...
        }
    
    def _init_connectors(self):
        """Инициализация коннекторов"""
        if settings.SAMOKAT_API_KEY:
            self.connectors["samokat"] = SamokatConnector(
                settings.SAMOKAT_API_KEY,
                "https://api.samokat.ru"
            )
        
        if settings.PAPAJOHNS_API_KEY:
            self.connectors["papa_johns"] = PapaJohnsConnector(
                settings.PAPAJOHNS_API_KEY,
                "https://api.papajohns.ru"
            )
        
        # Добавляем моки для демо, если нет реальных ключей
        if not self.connectors:
            self.connectors["samokat"] = SamokatConnector("demo", "https://demo.api")
            self.connectors["papa_johns"] = PapaJohnsConnector("demo", "https://demo.api")
    
    async def search_across_stores(
        self,
        query: str,
        stores: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Поиск across всех магазинов с сравнением цен"""
        
        target_stores = stores or list(self.connectors.keys())
        
        # Параллельный поиск
        tasks = []
        for store_id in target_stores:
            if store_id in self.connectors:
                connector = self.connectors[store_id]
                tasks.append(self._safe_search(connector, query))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Агрегация
        all_products = []
        store_results = {}
        
        for store_id, result in zip(target_stores, results):
            if isinstance(result, Exception):
                store_results[store_id] = {"error": str(result), "products": []}
            else:
                store_results[store_id] = {"products": result, "count": len(result)}
                all_products.extend(result)
        
        # Ранжирование
        ranked = self._rank_products(all_products, user_preferences)
        
        # Группировка по категориям
        by_category = {}
        for product in ranked:
            cat = product.category
            by_category.setdefault(cat, []).append(product)
        
        return {
            "query": query,
            "stores_searched": target_stores,
            "total_found": len(all_products),
            "best_options": ranked[:5],
            "by_category": by_category,
            "price_range": {
                "min": min(p.price for p in all_products) if all_products else 0,
                "max": max(p.price for p in all_products) if all_products else 0
            },
            "store_breakdown": store_results
        }
    
    async def _safe_search(self, connector: BaseStoreConnector, query: str):
        """Безопасный поиск с обработкой ошибок"""
        try:
            async with connector:
                return await connector.search(query, limit=10)
        except Exception as e:
            print(f"Search error in {connector.__class__.__name__}: {e}")
            return []
    
    def _rank_products(
        self,
        products: List[Product],
        preferences: Optional[Dict]
    ) -> List[Product]:
        """Умное ранжирование с учётом предпочтений"""
        scored = []
        
        for product in products:
            score = 0.0
            
            # Базовый скор: цена (ниже лучше, но не всегда)
            # Нормализуем цену (предполагаем диапазон 0-5000)
            price_score = max(0, 1 - (product.price / 5000))
            score += price_score * 0.3
            
            # Доступность
            if product.available:
                score += 0.2
            
            # Скорость доставки
            if product.delivery_time:
                if "15" in product.delivery_time or "30" in product.delivery_time:
                    score += 0.3
                elif "45" in product.delivery_time or "60" in product.delivery_time:
                    score += 0.15
            
            # Предпочтения пользователя
            if preferences:
                preferred_stores = preferences.get("preferred_stores", [])
                if product.store in preferred_stores:
                    score += 0.2
                
                # Диетические предпочтения
                if preferences.get("dietary_restrictions"):
                    # Проверка на запрещённые ингредиенты
                    pass
            
            scored.append((product, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [p for p, s in scored]
    
    async def create_order(
        self,
        store_id: str,
        items: List[CartItem],
        user_profile: Dict
    ) -> Order:
        """Создание заказа в выбранном магазине"""
        if store_id not in self.connectors:
            raise ValueError(f"Unknown store: {store_id}")
        
        connector = self.connectors[store_id]
        
        async with connector:
            # Создание корзины
            cart = await connector.create_cart(items)
            
            # Оформление
            order = await connector.checkout(cart["cart_id"], user_profile)
            
            # Добавляем affiliate tracking
            order.affiliate_id = self.affiliate_ids.get(store_id)
            
            return order
    
    async def get_order_status(self, order_id: str, store_id: str) -> Order:
        """Трекинг заказа"""
        connector = self.connectors.get(store_id)
        if not connector:
            raise ValueError(f"Unknown store: {store_id}")
        
        async with connector:
            return await connector.track_order(order_id)
    
    async def suggest_based_on_context(
        self,
        user_context: str,
        time_of_day: Optional[datetime] = None,
        user_history: Optional[List] = None
    ) -> List[Dict[str, Any]]:
        """Умные предложения на основе контекста"""
        suggestions = []
        hour = time_of_day.hour if time_of_day else datetime.now().hour
        
        # Временные паттерны
        if 7 <= hour <= 11:
            suggestions.append({
                "type": "breakfast",
                "query": "завтрак круассан кофе",
                "stores": ["samokat", "yandex_lavka"],
                "reason": "Утреннее время"
            })
        elif 11 <= hour <= 14:
            suggestions.append({
                "type": "lunch",
                "query": "обед бизнес-ланч",
                "stores": ["yandex_eats"],
                "reason": "Обеденное время"
            })
        elif 18 <= hour <= 22:
            suggestions.append({
                "type": "dinner",
                "query": "ужин пицца паста",
                "stores": ["papa_johns", "dodo"],
                "reason": "Вечернее время"
            })
        
        # Контекст из памяти
        if "пицца" in user_context.lower():
            suggestions.append({
                "type": "repeat",
                "query": "пицца пепперони",
                "stores": ["papa_johns"],
                "reason": "Упоминание пиццы в разговоре"
            })
        
        return suggestions
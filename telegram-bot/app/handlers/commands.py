"""Обработчики команд Telegram Bot"""

from aiogram import Dispatcher, types
import httpx
import logging

logger = logging.getLogger(__name__)


def register_commands(dp: Dispatcher, backend_client):
    """Регистрация обработчиков команд"""
    
    @dp.message_handler(commands=["start", "help"])
    async def send_welcome(message: types.Message):
        """Команда /start и /help"""
        welcome_msg = """
👋 Добро пожаловать в PersonalMind Pro!

Я твой персональный ИИ-ассистент с долгосрочной памятью.

Команды:
• Обычное сообщение - чат с ассистентом
• /memory <текст> - поиск в памяти
• /docs - список документов
• /commerce <запрос> - поиск товаров
• /search <товар> - поиск в Samokat/Papa Johns
• /help - этот текст
"""
        await message.reply(welcome_msg)
    
    @dp.message_handler(commands=["memory"])
    async def memory_query(message: types.Message):
        """Поиск в памяти"""
        text = message.get_args().strip()
        if not text:
            await message.reply("📚 Укажи, что искать: /memory <текст>")
            return
        
        try:
            # Отправка запроса в backend
            result = await backend_client.memory_search(str(message.from_user.id), text)
            await message.reply(f"📚 Найдено:\n{result}")
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            await message.reply(f"⚠️ Ошибка: {str(e)}")
    
    @dp.message_handler(commands=["docs"])
    async def list_documents(message: types.Message):
        """Список документов"""
        try:
            docs = await backend_client.get_documents(str(message.from_user.id))
            if not docs:
                await message.reply("📁 У тебя пока нет документов.")
                return
            
            doc_list = "\n".join([f"• {d.get('filename', 'Unknown')} ({d.get('size_bytes', 0)} б)" for d in docs[:10]])
            await message.reply(f"📁 Твои документы:\n{doc_list}")
        except Exception as e:
            logger.error(f"Document list error: {e}")
            await message.reply(f"⚠️ Ошибка: {str(e)}")
    
    @dp.message_handler(commands=["commerce", "search"])
    async def search_products(message: types.Message):
        """Поиск товаров"""
        query = message.get_args().strip()
        if not query:
            await message.reply("🛒 Что искать? /search <товар>")
            return
        
        try:
            products = await backend_client.search_products(query)
            if not products:
                await message.reply(f"Товары по '{query}' не найдены :(")
                return
            
            result = "🛒 Найдено товаров:\n"
            for p in products[:5]:
                result += f"\n🏪 {p.get('name', 'Unknown')} - ₽{p.get('price', 'N/A')}"
                if p.get('store'):
                    result += f" ({p['store']})"
            
            await message.reply(result)
        except Exception as e:
            logger.error(f"Search error: {e}")
            await message.reply(f"⚠️ Ошибка поиска: {str(e)}")
    async def search_documents(message: types.Message):
        query = message.get_args().strip()
        if not query:
            await message.reply("🔎 Укажи, что искать. Пример: /finddoc бюджет")
            return
        try:
            matches = await backend.search_documents(await _user_id(message), query)
        except BackendError as exc:
            await message.reply(f"⚠️ Ошибка поиска: {exc}")
            return
        if not matches:
            await message.reply("🔍 Ничего не нашёл в документах.")
            return
        summary = "\n".join([f"• {match['source_file']}: {match['content'][:80]}..." for match in matches[:3]])
        await message.reply(f"🔍 Результаты:\n{summary}")

    @dp.message_handler(commands=["commerce"])
    async def commerce_search(message: types.Message):
        query = message.get_args().strip()
        if not query:
            await message.reply("🛒 Пример: /commerce пицца")
            return
        try:
            data = await backend.search_commerce(await _user_id(message), query)
        except BackendError as exc:
            await message.reply(f"⚠️ Ошибка поиска: {exc}")
            return
        options = data.get("best_options", [])
        if not options:
            await message.reply("🛍️ Ничего не нашёл.")
            return
        formatted = "\n".join(
            f"• {item['store']} / {item['product_id']} — {item['name']} ({item['price']}₽)"
            for item in options[:3]
        )
        await message.reply(f"🛒 Товары:\n{formatted}\n\nДля заказа отправь /order <магазин> <product_id>")

    @dp.message_handler(commands=["order"])
    async def create_order(message: types.Message):
        parts = message.get_args().split()
        if len(parts) < 2:
            await message.reply("🛒 Формат: /order <store_id> <product_id>")
            return
        store_id, product_id = parts[0], parts[1]
        try:
            order = await backend.create_order(await _user_id(message), store_id, product_id, quantity=1)
        except BackendError as exc:
            await message.reply(f"❌ Не удалось оформить заказ: {exc}")
            return
        await message.reply(f"✅ Заказ {order['order_id']} ({order['store']}) оформлен на {order['total']}₽")

    @dp.message_handler(commands=["orders"])
    async def list_orders(message: types.Message):
        try:
            orders = await backend.list_orders(await _user_id(message))
        except BackendError as exc:
            await message.reply(f"⚠️ Не удалось загрузить историю: {exc}")
            return
        if not orders:
            await message.reply("🧾 История заказов пуста.")
            return
        lines = [
            f"• {order['order_id']} — {order['store']} ({order['total']}₽) {order['status']}"
            for order in orders[-5:]
        ]
        await message.reply("🧾 История заказов:\n" + "\n".join(lines))

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, FSInputFile, LabeledPrice
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp
import magic  # python-magic для определения типа файла

from app.core.config import settings

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# States
class UploadState(StatesGroup):
    waiting_for_file = State()

class OrderState(StatesGroup):
    selecting_store = State()
    confirming_order = State()
    payment = State()


class PersonalMindTelegramBot:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.router = Router()
        self.api_url = settings.API_URL  # http://backend:8000
        
        self._setup_handlers()
        self.dp.include_router(self.router)
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        
        # === Команды ===
        @self.router.message(CommandStart())
        async def cmd_start(message: Message):
            """Приветствие и onboarding"""
            user_id = str(message.from_user.id)
            
            # Проверка/создание профиля
            await self._ensure_user_exists(user_id, message.from_user)
            
            welcome_text = f"""👋 Привет, {message.from_user.first_name}!

🧠 Я <b>PersonalMind Pro</b> — твой персональный ИИ с долгосрочной памятью.

<b>Что я умею:</b>
• 💬 Помню всё, что ты мне рассказываешь
• 📄 Читаю твои документы и файлы
• 🛒 Заказываю еду и товары (пиццу, продукты, технику)
• 🔍 Ищу лучшие цены across магазинов

<b>Быстрый старт:</b>
• Просто пиши мне — я запоминаю всё
• Отправь файл — я проиндексирую
• Скажи "закажи пиццу" — и я сделаю это!

Начни с команды /help или просто напиши что-нибудь 👇"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Мой профиль", callback_data="profile")],
                [InlineKeyboardButton(text="🧠 Моя память", callback_data="memory_stats")],
                [InlineKeyboardButton(text="📁 Мои файлы", callback_data="documents")],
                [InlineKeyboardButton(text="⭐ Обновить до Pro", callback_data="upgrade_pro")]
            ])
            
            await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")
        
        @self.router.message(Command("help"))
        async def cmd_help(message: Message):
            """Помощь"""
            help_text = """<b>📚 Команды PersonalMind:</b>

<b>Общение:</b>
• Любое сообщение — я отвечу с учётом памяти
• /memory — статистика памяти
• /profile — твой профиль
• /forget — удалить воспоминание

<b>Документы:</b>
• Отправь файл — я сохраню и проиндексирую
• /documents — список файлов
• /search [запрос] — поиск по документам

<b>Покупки (Pro):</b>
• "Закажи пиццу" — заказ еды
• "Купи [товар]" — поиск и заказ
• /stores — доступные магазины
• /orders — история заказов

<b>Настройки:</b>
• /settings — предпочтения
• /upgrade — обновить тариф

<b>Поддержка:</b> @personalmind_support"""
            
            await message.answer(help_text, parse_mode="HTML")
        
        @self.router.message(Command("memory"))
        async def cmd_memory(message: Message):
            """Статистика памяти"""
            user_id = str(message.from_user.id)
            stats = await self._api_call("GET", f"/memory/stats?user_id={user_id}")
            
            if not stats:
                await message.answer("❌ Ошибка получения статистики")
                return
            
            # Проверка лимитов (для Free)
            total = stats.get("total_memories", 0)
            limit = 1000 if await self._is_pro(user_id) else 100  # Условные лимиты
            
            text = f"""<b>🧠 Твоя память:</b>

📊 Воспоминаний: <b>{total}</b> / {limit if not await self._is_pro(user_id) else '∞'}
🗂️ По типам: {self._format_types(stats.get("by_type", {}))}
📈 Средняя важность: {stats.get("avg_importance", 0):.2f}
🕐 Создано: {stats.get("newest_memory", "недавно")[:10] if stats.get("newest_memory") else "N/A"}

{"✅ Pro: безлимитная память" if await self._is_pro(user_id) else f"⚠️ Free: осталось {limit - total} слотов"}"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Поиск в памяти", switch_inline_query_current_chat="что я говорил о ")],
                [InlineKeyboardButton(text="⭐ Обновить до Pro", callback_data="upgrade_pro")] if not await self._is_pro(user_id) else []
            ])
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        @self.router.message(Command("profile"))
        async def cmd_profile(message: Message):
            """Профиль пользователя"""
            user_id = str(message.from_user.id)
            profile = await self._api_call("GET", f"/profile?user_id={user_id}")
            
            if not profile:
                await message.answer("❌ Профиль не найден")
                return
            
            demo = profile.get("demographics", {})
            interests = profile.get("interests", [])
            prefs = profile.get("communication_style", {})
            
            text = f"""<b>👤 Твой профиль:</b>

📍 Локация: {demo.get('location', 'не указана')}
💼 Работа: {demo.get('occupation', 'не указана')}
🎯 Интересы: {', '.join([i['name'] for i in interests[:5]]) if interests else 'пока не выявлены'}
🗣️ Стиль: {prefs.get('response_length', 'сбалансированный')}

<i>Профиль обновляется автоматически из наших разговоров</i>"""
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile")],
                [InlineKeyboardButton(text="📊 Подробнее", callback_data="profile_details")]
            ])
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        @self.router.message(Command("documents"))
        async def cmd_documents(message: Message):
            """Список документов"""
            user_id = str(message.from_user.id)
            docs = await self._api_call("GET", f"/documents?user_id={user_id}")
            
            if not docs or not docs.get("documents"):
                await message.answer(
                    "📁 У тебя пока нет загруженных файлов.\n\n"
                    "Просто отправь мне PDF, TXT, DOCX или другой документ — я сохраню и проиндексирую его!"
                )
                return
            
            documents = docs["documents"]
            text = f"<b>📁 Твои файлы ({len(documents)}):</b>\n\n"
            
            for i, doc in enumerate(documents[:10], 1):
                size_mb = doc.get("size_bytes", 0) / 1024 / 1024
                text += f"{i}. <b>{doc['filename'][:30]}</b> ({size_mb:.1f} MB)\n"
                text += f"   🕐 {doc['modified'][:10]}\n\n"
            
            if len(documents) > 10:
                text += f"... и ещё {len(documents) - 10} файлов"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔍 Поиск по файлам", switch_inline_query_current_chat="найди в файлах ")],
                [InlineKeyboardButton(text="⬆️ Загрузить ещё", callback_data="upload_file")]
            ])
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        
        # === Обработка файлов ===
        @self.router.message(F.document | F.photo)
        async def handle_file(message: Message, state: FSMContext):
            """Обработка загруженных файлов"""
            user_id = str(message.from_user.id)
            
            # Проверка лимитов Free
            if not await self._is_pro(user_id):
                stats = await self._api_call("GET", f"/memory/stats?user_id={user_id}")
                if stats and stats.get("total_memories", 0) > 100:
                    await message.answer(
                        "⚠️ <b>Лимит Free тарифа достигнут!</b>\n\n"
                        "Ты использовал 100 воспоминаний из 100 доступных.\n"
                        "Загрузи больше файлов в Pro-версии.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="⭐ Обновить до Pro $9.99", callback_data="upgrade_pro")]
                        ]),
                        parse_mode="HTML"
                    )
                    return
            
            # Определение файла
            if message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
                mime_type = message.document.mime_type
            else:
                # Фото — берём самое большое
                photo = message.photo[-1]
                file_id = photo.file_id
                file_name = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                mime_type = "image/jpeg"
            
            # Скачивание
            processing_msg = await message.answer("⏳ Скачиваю файл...")
            
            try:
                file = await self.bot.get_file(file_id)
                file_content = await self.bot.download_file(file.file_path)
                
                await processing_msg.edit_text("🧠 Индексирую документ...")
                
                # Отправка в API
                result = await self._upload_file(file_content.read(), file_name, user_id)
                
                if result:
                    success_text = f"""✅ <b>Файл обработан!</b>

📄 <b>{file_name}</b>
📊 Фрагментов: {result.get('chunks', 0)}
📝 Сводка: {result.get('summary', 'Документ проиндексирован')}

Теперь ты можешь спрашивать меня о содержимом этого файла!"""
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔍 Найти в файле", switch_inline_query_current_chat=f"что написано в {file_name} про ")],
                        [InlineKeyboardButton(text="📁 Все файлы", callback_data="documents")]
                    ])
                    
                    await processing_msg.edit_text(success_text, reply_markup=keyboard, parse_mode="HTML")
                else:
                    await processing_msg.edit_text("❌ Ошибка обработки файла")
                    
            except Exception as e:
                logger.error(f"File processing error: {e}")
                await processing_msg.edit_text(f"❌ Ошибка: {str(e)[:100]}")
        
        # === Основной чат ===
        @self.router.message(F.text)
        async def handle_message(message: Message):
            """Обработка текстовых сообщений"""
            user_id = str(message.from_user.id)
            text = message.text
            
            # Проверка коммерческих интентов
            commerce_keywords = ["закажи", "купи", "доставь", "пицца", "продукты", "самокат", "яндекс"]
            is_commerce = any(kw in text.lower() for kw in commerce_keywords)
            
            if is_commerce and not await self._is_pro(user_id):
                # Commerce только в Pro (или ограниченно в Free)
                await message.answer(
                    "🛒 <b>Функция заказов доступна в Pro!</b>\n\n"
                    "В Free-версии я могу только искать товары.\n"
                    "Для оформления заказа обнови тариф.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="⭐ Попробовать Pro", callback_data="upgrade_pro")]
                    ]),
                    parse_mode="HTML"
                )
                return
            
            # Индикатор набора
            await self.bot.send_chat_action(message.chat.id, "typing")
            
            # Отправка в API
            response = await self._api_call(
                "POST",
                "/chat",
                {
                    "content": text,
                    "user_id": user_id,
                    "role": "user",
                    "metadata": {
                        "chat_id": message.chat.id,
                        "message_id": message.message_id
                    }
                }
            )
            
            if response:
                reply_text = response.get("text", "Извини, не понял 🤔")
                
                # Добавление кнопок действий
                keyboard = None
                if response.get("sources"):
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="📋 Источники", callback_data=f"sources:{message.message_id}")],
                        [InlineKeyboardButton(text="🧠 Подробнее", callback_data=f"expand:{message.message_id}")]
                    ])
                
                await message.answer(reply_text, reply_markup=keyboard, parse_mode="HTML")
            else:
                await message.answer("❌ Ошибка обработки. Попробуй ещё раз.")
        
        # === Callback handlers ===
        @self.router.callback_query(F.data == "upgrade_pro")
        async def callback_upgrade(callback: CallbackQuery):
            """Обновление до Pro"""
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить $9.99/мес", callback_data="pay_pro_monthly")],
                [InlineKeyboardButton(text="💳 Оплатить $99/год (экономия 17%)", callback_data="pay_pro_yearly")],
                [InlineKeyboardButton(text="❓ Что входит в Pro", callback_data="pro_features")]
            ])
            
            await callback.message.edit_text(
                """<b>⭐ PersonalMind Pro</b>

<b>Включает:</b>
✅ Безлимитная память (храни всё!)
✅ Заказы в 10+ магазинах (пицца, продукты, техника)
✅ Приоритетная обработка (быстрее ответы)
✅ API доступ (интегрируй свои сервисы)
✅ Расширенный профиль (глубже понимание)
✅ Поддержка 24/7

<b>Цена:</b> $9.99/мес или $99/год""",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback.answer()
        
        @self.router.callback_query(F.data.startswith("pay_pro"))
        async def process_payment(callback: CallbackQuery):
            """Обработка оплаты через Telegram Payments"""
            plan = "monthly" if "monthly" in callback.data else "yearly"
            amount = 999 if plan == "monthly" else 9900  # в копейках/центах
            
            prices = [LabeledPrice(label=f"Pro {plan}", amount=amount)]
            
            await self.bot.send_invoice(
                chat_id=callback.message.chat.id,
                title=f"PersonalMind Pro ({plan})",
                description="Безлимитная память и все функции",
                payload=f"pro_{plan}_{callback.from_user.id}",
                provider_token=settings.PAYMENT_PROVIDER_TOKEN,  # ЮKassa/Stripe
                currency="USD",
                prices=prices,
                start_parameter="upgrade_pro"
            )
            await callback.answer()
        
        @self.router.message(F.successful_payment)
        async def successful_payment(message: Message):
            """Успешная оплата"""
            payment = message.successful_payment
            user_id = str(message.from_user.id)
            
            # Активация Pro в базе
            await self._activate_pro(user_id, payment.invoice_payload)
            
            await message.answer(
                "🎉 <b>Добро пожаловать в Pro!</b>\n\n"
                "Твоя подписка активирована. Теперь доступны все функции:\n"
                "• Безлимитная память\n"
                "• Заказы в магазинах\n"
                "• Приоритетная обработка\n\n"
                "Начни с команды /help или просто напиши мне!",
                parse_mode="HTML"
            )
    
    # === Вспомогательные методы ===
    async def _api_call(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Вызов backend API"""
        url = f"{self.api_url}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url) as resp:
                        return await resp.json() if resp.status == 200 else None
                else:
                    async with session.post(url, json=data) as resp:
                        return await resp.json() if resp.status == 200 else None
        except Exception as e:
            logger.error(f"API call error: {e}")
            return None
    
    async def _upload_file(self, content: bytes, filename: str, user_id: str) -> dict:
        """Загрузка файла в API"""
        url = f"{self.api_url}/upload?user_id={user_id}"
        try:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', content, filename=filename)
                async with session.post(url, data=data) as resp:
                    return await resp.json() if resp.status == 200 else None
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None
    
    async def _ensure_user_exists(self, user_id: str, tg_user):
        """Создание пользователя при первом старте"""
        # Вызов API для создания профиля
        await self._api_call("POST", "/profile/init", {
            "user_id": user_id,
            "username": tg_user.username,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name
        })
    
    async def _is_pro(self, user_id: str) -> bool:
        """Проверка Pro-статуса"""
        # В реальности — запрос к базе
        # Заглушка для MVP
        return False
    
    async def _activate_pro(self, user_id: str, payload: str):
        """Активация Pro после оплаты"""
        await self._api_call("POST", "/billing/activate", {
            "user_id": user_id,
            "payload": payload,
            "activated_at": datetime.utcnow().isoformat()
        })
    
    def _format_types(self, types_dict: dict) -> str:
        """Форматирование типов памяти"""
        if not types_dict:
            return "нет данных"
        return ", ".join([f"{k}: {v}" for k, v in types_dict.items()])
    
    async def start(self):
        """Запуск бота"""
        logger.info("Starting Telegram Bot...")
        await self.dp.start_polling(self.bot)


# Запуск
if __name__ == "__main__":
    bot = PersonalMindTelegramBot()
    asyncio.run(bot.start())
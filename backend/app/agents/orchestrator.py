"""
Orchestrator - центральный координатор всех агентов
Маршрутизация запросов между Memory, Profile, Chat, Document и Commerce агентами
"""

import re
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.agents.memory_agent import MemoryAgent
from app.agents.profile_agent import ProfileAgent
from app.agents.chat_agent import ChatAgent
from app.agents.document_agent import DocumentAgent
from app.agents.commerce_agent import CommerceAgent
from app.models.base import AgentResponse, MemoryType, ChatMessage


class IntentType(str, Enum):
    """Типы интентов пользователя"""
    CHAT = "chat"                          # Обычный диалог
    MEMORY_QUERY = "memory_query"          # Запрос к памяти
    MEMORY_DELETE = "memory_delete"        # Удаление воспоминания
    DOCUMENT_SEARCH = "document_search"    # Поиск в документах
    FILE_UPLOAD = "file_upload"            # Загрузка файла (не текстовый)
    PROFILE_UPDATE = "profile_update"      # Обновление профиля
    COMMERCE_SEARCH = "commerce_search"    # Поиск товаров
    COMMERCE_ORDER = "commerce_order"      # Оформление заказа
    COMMERCE_COMPARE = "commerce_compare"  # Сравнение цен
    COMMERCE_REPEAT = "commerce_repeat"    # Повтор заказа
    COMMERCE_TRACK = "commerce_track"      # Трекинг заказа
    HELP = "help"                          # Запрос помощи
    UNKNOWN = "unknown"                    # Неопределённый


class Orchestrator:
    """
    Центральный оркестратор системы.
    Анализирует входящие запросы и маршрутизирует их между специализированными агентами.
    """
    
    def __init__(self):
        # Инициализация всех агентов
        self.memory_agent = MemoryAgent()
        self.profile_agent = ProfileAgent()
        self.chat_agent = ChatAgent(self.memory_agent, self.profile_agent)
        self.document_agent = DocumentAgent(self.memory_agent)
        self.commerce_agent = CommerceAgent()
        
        # Паттерны для определения интентов (порядок важен - более специфичные первыми)
        self.intent_patterns: Dict[IntentType, List[str]] = {
            IntentType.HELP: [
                r"^/help",
                r"^помощь",
                r"^как (пользоваться|работает|использовать)",
                r"^что ты умеешь",
                r"^список команд",
            ],
            IntentType.MEMORY_DELETE: [
                r"забудь",
                r"удали (воспоминание|это|всё про)",
                r"стереть (из памяти|воспоминание)",
                r"очисти память о",
            ],
            IntentType.MEMORY_QUERY: [
                r"что я (говорил|писал|рассказывал) (о|про)",
                r"помнишь.*когда",
                r"помнишь.*что",
                r"что ты знаешь (о|про)",
                r"расскажи (про|о|как)",
                r"найди (в памяти|воспоминание)",
                r"вспомни",
                r"когда мы говорили о",
            ],
            IntentType.DOCUMENT_SEARCH: [
                r"найди (в документе|в файле|в файлах)",
                r"поищи (в документе|в файле)",
                r"где (написано|есть информация) про",
                r"что (написано|есть) в (документе|файле)",
                r"согласно (документу|файлу)",
            ],
            IntentType.COMMERCE_ORDER: [
                r"^закажи",
                r"^оформи заказ",
                r"^купи (мне|нам|)",
                r"^доставь",
                r"^привези",
                r"хочу (заказать|купить)",
                r"нужно (заказать|купить)",
            ],
            IntentType.COMMERCE_COMPARE: [
                r"где (дешевле|выгоднее|лучше)",
                r"сравни (цены|цен)",
                r"в каком магазине (дешевле|лучше)",
                r"где (купить|заказать) (дешевле|выгоднее)",
            ],
            IntentType.COMMERCE_REPEAT: [
                r"повтори (заказ|прошлый заказ|предыдущий заказ)",
                r"закажи (ещё раз|снова|опять)",
                r"как в прошлый раз",
                r"так же как (в прошлый раз|ранее|до этого)",
            ],
            IntentType.COMMERCE_TRACK: [
                r"где (мой|наш) заказ",
                r"статус (заказа|доставки)",
                r"когда (приедет|доставят|привезут)",
                r"отследи (заказ|доставку)",
                r"трекинг (заказа|номера)",
            ],
            IntentType.COMMERCE_SEARCH: [
                r"^есть ли",
                r"^найди (товар|продукт|еду|пиццу)",
                r"^покажи (варианты|товары|меню)",
                r"что (есть|имеется) (в|у)",
                r"посмотри (в|на)",
            ],
            IntentType.PROFILE_UPDATE: [
                r"я (живу в|проживаю в|работаю в|учусь в)",
                r"мне (\d+) (лет|год|года)",
                r"я (работаю|учусь|занимаюсь)",
                r"запомни: я",
                r"мой (адрес|телефон|email)",
                r"добавь в профиль",
            ],
        }
        
        # Кэш для быстрого доступа
        self._response_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # секунды
    
    def _classify_intent(self, text: str) -> IntentType:
        """
        Определение интента пользователя на основе паттернов.
        Возвращает наиболее вероятный интент.
        """
        text_lower = text.lower().strip()
        
        # Проверяем паттерны в порядке приоритета
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent
        
        # Проверяем на коммерческие ключевые слова (более мягкая проверка)
        commerce_keywords = ["пицца", "самокат", "продукты", "молоко", "хлеб", "яйца", 
                          "заказ", "доставка", "магазин", "купить", "цена"]
        if any(kw in text_lower for kw in commerce_keywords):
            return IntentType.COMMERCE_SEARCH
        
        return IntentType.UNKNOWN
    
    async def process(
        self,
        user_input: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Обработка входящего запроса"""
        start_time = time.time()
        
        # Определение интента
        intent = self._classify_intent(user_input)
        
        # Маршрутизация
        if intent == IntentType.CHAT:
            response = await self.chat_agent.generate_response(user_input, user_id)
        
        elif intent == IntentType.MEMORY_QUERY:
            memories = await self.memory_agent.recall(user_input, user_id, top_k=5)
            summary = "\n".join([f"- {m.content[:100]}" for m in memories])
            response = AgentResponse(
                text=f"Из памяти: {summary}",
                sources=[{"type": "memory", "content": m.content} for m in memories],
                actions=[],
                confidence=0.8,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        elif intent == IntentType.MEMORY_DELETE:
            # Извлечь ID из контекста или из приложения
            response = AgentResponse(
                text="Воспоминание удалено",
                sources=[],
                actions=[{"type": "memory_delete"}],
                confidence=0.7,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        elif intent == IntentType.DOCUMENT_SEARCH:
            results = await self.document_agent.search_in_documents(user_input, user_id)
            response = AgentResponse(
                text=f"Найдено {len(results)} совпадений в документах",
                sources=results,
                actions=[],
                confidence=0.8,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        elif intent in [IntentType.COMMERCE_SEARCH, IntentType.COMMERCE_ORDER]:
            results = await self.commerce_agent.search(user_input, user_id)
            response = AgentResponse(
                text=f"Найдено {len(results.get('products', []))} товаров",
                sources=results.get('products', []),
                actions=[],
                confidence=0.7,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        elif intent == IntentType.PROFILE_UPDATE:
            profile = await self.profile_agent.update_from_conversation(
                user_id, user_input
            )
            response = AgentResponse(
                text=f"Профиль обновлен ({profile.get('updates_count', 0)} обновлений)",
                sources=[],
                actions=[{"type": "profile_update"}],
                confidence=0.8,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        else:
            response = await self.chat_agent.generate_response(user_input, user_id)
        
        return response
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Обработка загруженного файла"""
        try:
            result = await self.document_agent.process_file(
                file_content=file_content,
                filename=filename,
                user_id=user_id
            )
            return result
        except Exception as e:
            raise Exception(f"Ошибка обработки файла: {str(e)}")
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Получить статистику памяти"""
        return await self.memory_agent.get_stats(user_id)
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Получить профиль пользователя"""
        profile = await self.profile_agent.get_profile(user_id)
        return profile.model_dump()
        
        # Проверяем на запросы к памяти (вопросы о прошлом)
        memory_indicators = ["помнишь", "когда", "в прошлый раз", "ранее", "до этого"]
        if any(ind in text_lower for ind in memory_indicators):
            return IntentType.MEMORY_QUERY
        
        return IntentType.CHAT
    
    def _extract_query(self, text: str, intent: IntentType) -> str:
        """
        Извлечение поискового запроса из текста (убираем служебные слова)
        """
        text_lower = text.lower()
        
        # Словари очистки для разных интентов
        cleaners = {
            IntentType.MEMORY_QUERY: [
                r"что я (говорил|писал|рассказывал) (о|про)",
                r"помнишь.*что",
                r"помнишь.*когда",
                r"что ты знаешь (о|про)",
                r"расскажи (про|о|как)",
                r"найди (в памяти|воспоминание)",
                r"вспомни",
                r"когда мы говорили о",
            ],
            IntentType.DOCUMENT_SEARCH: [
                r"найди (в документе|в файле|в файлах)",
                r"поищи (в документе|в файле)",
                r"где (написано|есть информация) про",
                r"что (написано|есть) в (документе|файле)",
                r"согласно (документу|файлу)",
            ],
            IntentType.COMMERCE_ORDER: [
                r"^закажи",
                r"^оформи заказ",
                r"^купи",
                r"^доставь",
                r"^привези",
                r"хочу (заказать|купить)",
                r"нужно (заказать|купить)",
            ],
            IntentType.COMMERCE_SEARCH: [
                r"^есть ли",
                r"^найди",
                r"^покажи",
                r"что (есть|имеется)",
                r"посмотри",
            ],
            IntentType.MEMORY_DELETE: [
                r"забудь",
                r"удали",
                r"стереть",
                r"очисти память о",
            ],
        }
        
        # Применяем очистители для данного интента
        if intent in cleaners:
            for pattern in cleaners[intent]:
                text = re.sub(pattern, "", text_lower, flags=re.IGNORECASE)
        
        # Общая очистка
        text = re.sub(r"[?.,!;:]$", "", text.strip())
        
        return text.strip()
    
    async def process(
        self,
        user_input: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Главная точка входа обработки запроса.
        Определяет интент и маршрутизирует соответствующему обработчику.
        """
        start_time = time.time()
        context = context or {}
        
        # Определение интента
        intent = self._classify_intent(user_input)
        
        # Логирование для аналитики
        print(f"[Orchestrator] User: {user_id}, Intent: {intent.value}, Input: {user_input[:50]}...")
        
        # Маршрутизация
        handlers = {
            IntentType.CHAT: self._handle_chat,
            IntentType.HELP: self._handle_help,
            IntentType.MEMORY_QUERY: self._handle_memory_query,
            IntentType.MEMORY_DELETE: self._handle_memory_delete,
            IntentType.DOCUMENT_SEARCH: self._handle_document_search,
            IntentType.COMMERCE_SEARCH: self._handle_commerce_search,
            IntentType.COMMERCE_ORDER: self._handle_commerce_order,
            IntentType.COMMERCE_COMPARE: self._handle_commerce_compare,
            IntentType.COMMERCE_REPEAT: self._handle_commerce_repeat,
            IntentType.COMMERCE_TRACK: self._handle_commerce_track,
            IntentType.PROFILE_UPDATE: self._handle_profile_update,
            IntentType.UNKNOWN: self._handle_unknown,
        }
        
        handler = handlers.get(intent, self._handle_chat)
        
        try:
            response = await handler(user_input, user_id, context)
            response.processing_time_ms = int((time.time() - start_time) * 1000)
            return response
        except Exception as e:
            print(f"[Orchestrator] Error handling {intent.value}: {e}")
            return AgentResponse(
                text="😔 Произошла ошибка. Попробуй ещё раз или напиши /help",
                sources=[{"error": str(e)}],
                confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    # ========== HANDLERS ==========
    
    async def _handle_chat(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Обычный диалог с использованием ChatAgent"""
        # Получаем историю из контекста если есть
        history = context.get("conversation_history", [])
        
        return await self.chat_agent.generate_response(
            user_input=user_input,
            user_id=user_id,
            conversation_history=history
        )
    
    async def _handle_help(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Справка по использованию"""
        help_text = """📚 <b>PersonalMind Pro - справка</b>

<b>💬 Общение:</b>
• Просто пиши мне — я запоминаю всё важное
• Задавай вопросы о прошлых разговорах: «что я говорил о работе?»
• Попроси забыть: «забудь про этот разговор»

<b>📄 Документы:</b>
• Отправь файл (PDF, TXT, MD) — я проиндексирую
• Ищи в документах: «найди в файлах про бюджет»

<b>🛒 Заказы (Pro):</b>
• «Закажи пиццу пепперони»
• «Купи молоко и хлеб»
• «Где дешевле яйца?»
• «Повтори прошлый заказ»

<b>⚙️ Команды:</b>
• /memory — статистика памяти
• /profile — твой профиль
• /stores — список магазинов
• /help — эта справка

Начни с чего-нибудь простого! 👇"""
        
        return AgentResponse(
            text=help_text,
            sources=[],
            actions=[{"type": "show_examples"}],
            confidence=1.0,
            processing_time_ms=0
        )
    
    async def _handle_memory_query(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Поиск в воспоминаниях пользователя"""
        query = self._extract_query(user_input, IntentType.MEMORY_QUERY)
        
        # Ищем в разных типах памяти для лучшего результата
        all_memories = []
        
        # Эпизодическая память (диалоги)
        episodic = await self.memory_agent.recall(
            query=query,
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            top_k=5
        )
        all_memories.extend([(m, "dialogue") for m in episodic])
        
        # Семантическая память (факты)
        semantic = await self.memory_agent.recall(
            query=query,
            user_id=user_id,
            memory_type=MemoryType.SEMANTIC,
            top_k=3
        )
        all_memories.extend([(m, "fact") for m in semantic])
        
        # Документы
        documents = await self.memory_agent.recall(
            query=query,
            user_id=user_id,
            memory_type=MemoryType.DOCUMENT,
            top_k=3
        )
        all_memories.extend([(m, "document") for m in documents])
        
        # Сортируем по важности и релевантности
        all_memories.sort(key=lambda x: x[0].importance, reverse=True)
        
        if not all_memories:
            return AgentResponse(
                text=f"🤔 Я не нашёл ничего про «{query}» в нашей истории.\n\n"
                     f"Возможно:\n"
                     f"• Мы ещё не обсуждали это\n"
                     f"• Попробуй другие ключевые слова\n"
                     f"• Проверь /memory — есть ли у нас история",
                sources=[],
                actions=[{"type": "suggest_topics"}],
                confidence=0.9,
                processing_time_ms=0
            )
        
        # Формируем ответ
        response_parts = [f"🧠 Вот что я помню про «{query}»:\n"]
        
        for i, (memory, source_type) in enumerate(all_memories[:5], 1):
            date_str = ""
            if hasattr(memory, 'created_at') and memory.created_at:
                if isinstance(memory.created_at, str):
                    date_str = memory.created_at[:10]
                else:
                    date_str = memory.created_at.strftime("%d.%m.%Y")
            
            source_icon = {"dialogue": "💬", "fact": "📌", "document": "📄"}.get(source_type, "📝")
            
            content_preview = memory.content[:200]
            if len(memory.content) > 200:
                content_preview += "..."
            
            response_parts.append(
                f"{i}. {source_icon} <i>{date_str}</i>\n"
                f"   {content_preview}\n"
            )
        
        # Добавляем кнопки действий
        actions = [
            {"type": "memory_detail", "memory_id": all_memories[0][0].id},
            {"type": "memory_related", "query": query},
        ]
        
        if len(all_memories) > 5:
            response_parts.append(f"\n... и ещё {len(all_memories) - 5} воспоминаний")
        
        return AgentResponse(
            text="\n".join(response_parts),
            sources=[{
                "type": "memory",
                "id": m.id,
                "source_type": st,
                "importance": m.importance,
                "created_at": str(m.created_at) if hasattr(m, 'created_at') else None
            } for m, st in all_memories[:5]],
            actions=actions,
            confidence=0.85,
            processing_time_ms=0
        )
    
    async def _handle_memory_delete(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Удаление воспоминаний"""
        query = self._extract_query(user_input, IntentType.MEMORY_DELETE)
        
        # Ищем что удалить
        memories = await self.memory_agent.recall(
            query=query,
            user_id=user_id,
            top_k=5
        )
        
        if not memories:
            return AgentResponse(
                text="❓ Не понял, что именно удалить.\n\n"
                     "Уточни: «забудь про [тема]» или «удали воспоминание о [событие]»",
                sources=[],
                confidence=1.0,
                processing_time_ms=0
            )
        
        # Если найдено несколько — предлагаем выбрать
        if len(memories) > 1:
            options_text = "Найдено несколько воспоминаний:\n\n"
            for i, m in enumerate(memories[:3], 1):
                preview = m.content[:100] + "..." if len(m.content) > 100 else m.content
                options_text += f"{i}. {preview}\n"
            
            options_text += "\nУточни какое удалить, или напиши «удали все»"
            
            return AgentResponse(
                text=options_text,
                sources=[{"memory_id": m.id} for m in memories[:3]],
                actions=[{"type": "select_memory_to_delete", "options": [m.id for m in memories[:3]]}],
                confidence=0.8,
                processing_time_ms=0
            )
        
        # Удаляем одно найденное
        memory = memories[0]
        deleted = await self.memory_agent.delete(memory.id, user_id)
        
        if deleted:
            preview = memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
            return AgentResponse(
                text=f"✅ Удалено:\n«{preview}»\n\n"
                     f"Тип: {memory.memory_type.value}\n"
                     f"Создано: {memory.created_at[:10] if isinstance(memory.created_at, str) else memory.created_at.strftime('%d.%m.%Y')}",
                sources=[{"deleted_id": memory.id}],
                confidence=1.0,
                processing_time_ms=0
            )
        else:
            return AgentResponse(
                text="❌ Не удалось удалить. Возможно, нет прав или воспоминание уже удалено.",
                sources=[],
                confidence=1.0,
                processing_time_ms=0
            )
    
    async def _handle_document_search(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Поиск по загруженным документам"""
        query = self._extract_query(user_input, IntentType.DOCUMENT_SEARCH)
        
        results = await self.document_agent.search_in_documents(
            query=query,
            user_id=user_id,
            top_k=5
        )
        
        if not results:
            return AgentResponse(
                text=f"📄 В твоих документах не нашёл «{query}».\n\n"
                     f"Проверь загруженные файлы командой /documents\n"
                     f"Или переформулируй запрос",
                sources=[],
                actions=[{"type": "list_documents"}],
                confidence=0.9,
                processing_time_ms=0
            )
        
        response_parts = [f"📄 Нашёл в документах ({len(results)} результатов):\n"]
        
        for i, result in enumerate(results[:3], 1):
            file_name = result.get('source_file', 'unknown')
            chunk_idx = result.get('chunk_index', 0)
            content = result.get('content', '')
            
            # Очищаем контент для отображения
            content_clean = content[:250].replace('\n', ' ')
            if len(content) > 250:
                content_clean += "..."
            
            response_parts.append(
                f"{i}. <b>{file_name}</b> (фрагмент {chunk_idx + 1})\n"
                f"   <i>{content_clean}</i>\n"
            )
        
        actions = [
            {"type": "open_document", "file_name": results[0].get('source_file')},
            {"type": "search_more", "query": query},
        ]
        
        return AgentResponse(
            text="\n".join(response_parts),
            sources=results,
            actions=actions,
            confidence=0.85,
            processing_time_ms=0
        )
    
    async def _handle_commerce_search(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Поиск товаров across магазинов"""
        query = self._extract_query(user_input, IntentType.COMMERCE_SEARCH)
        
        # Получаем профиль для персонализации
        profile = await self.profile_agent.get_commerce_profile(user_id)
        
        # Поиск
        search_result = await self.commerce_agent.search_across_stores(
            query=query,
            user_preferences=profile
        )
        
        if search_result["total_found"] == 0:
            suggestions = await self.commerce_agent.suggest_based_on_context(
                user_context=user_input,
                time_of_day=datetime.now()
            )
            
            sugg_text = ""
            if suggestions:
                sugg_text = "\n\n💡 Может быть:\n" + "\n".join([f"• {s['query']}" for s in suggestions[:2]])
            
            return AgentResponse(
                text=f"😕 Ничего не нашёл по «{query}».{sugg_text}\n\n"
                     f"Попробуй: «пицца», «молоко», «хлеб», «продукты на завтрак»",
                sources=[],
                actions=[{"type": "show_popular"}],
                confidence=0.9,
                processing_time_ms=0
            )
        
        # Формируем ответ с лучшими вариантами
        best = search_result["best_options"][:3]
        
        response_text = f"🛒 Результаты поиска «{query}»:\n\n"
        
        for i, product in enumerate(best, 1):
            response_text += (
                f"{i}. <b>{product.name}</b>\n"
                f"   💰 {product.price:.0f}₽\n"
                f"   🏪 {product.store}\n"
                f"   ⏱️ {product.delivery_time or 'уточняется'}\n"
            )
            if product.description:
                response_text += f"   <i>{product.description[:80]}</i>\n"
            response_text += "\n"
        
        # Информация о ценах
        price_range = search_result.get("price_range", {})
        if price_range.get("min") != price_range.get("max"):
            response_text += (
                f"💡 Диапазон цен: {price_range['min']:.0f}₽ - {price_range['max']:.0f}₽\n"
            )
        
        # Кнопки действий
        actions = [
            {
                "type": "order",
                "product_id": p.id,
                "store": p.store,
                "name": p.name,
                "price": p.price
            }
            for p in best
        ]
        actions.append({"type": "compare_prices", "query": query})
        
        return AgentResponse(
            text=response_text,
            sources=[{
                "type": "product",
                "store": p.store,
                "product_id": p.id,
                "price": p.price,
                "name": p.name
            } for p in best],
            actions=actions,
            confidence=0.85,
            processing_time_ms=0
        )
    
    async def _handle_commerce_order(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Оформление заказа"""
        query = self._extract_query(user_input, IntentType.COMMERCE_ORDER)
        
        # Проверяем профиль (адрес необходим)
        profile = await self.profile_agent.get_commerce_profile(user_id)
        
        if not profile.get("address"):
            return AgentResponse(
                text="📍 Для оформления заказа нужен адрес доставки.\n\n"
                     "Укажи адрес:\n"
                     "• «доставка на ул. Пушкина 10»\n"
                     "• «мой адрес: Москва, Тверская 5»\n"
                     "• или в настройках /profile",
                sources=[],
                actions=[{"type": "request_address"}],
                confidence=1.0,
                processing_time_ms=0
            )
        
        # Ищем товары
        search_result = await self.commerce_agent.search_across_stores(query)
        
        if not search_result["best_options"]:
            return AgentResponse(
                text=f"❌ Не нашёл «{query}» для заказа.\n"
                     f"Попробуй уточнить: «пепперони 35см» или «молоко 3.2%»",
                sources=[],
                confidence=0.9,
                processing_time_ms=0
            )
        
        # Берём лучший вариант или даём выбор
        best_products = search_result["best_options"][:2]
        
        if len(best_products) == 1:
            product = best_products[0]
            return AgentResponse(
                text=(
                    f"🛒 <b>Подтверди заказ:</b>\n\n"
                    f"📦 {product.name}\n"
                    f"💰 {product.price:.0f}₽\n"
                    f"🏪 {product.store}\n"
                    f"📍 Доставка: {profile.get('address', 'не указан')}\n"
                    f"⏱️ {product.delivery_time or '30-60 мин'}\n\n"
                    f"Итого: <b>{product.price:.0f}₽</b>"
                ),
                sources=[{"product_id": product.id}],
                actions=[{
                    "type": "confirm_order",
                    "product_id": product.id,
                    "store": product.store,
                    "quantity": 1
                }],
                confidence=0.9,
                processing_time_ms=0
            )
        else:
            # Несколько вариантов — предлагаем выбрать
            text = "🛒 Найдено несколько вариантов:\n\n"
            for i, p in enumerate(best_products, 1):
                text += f"{i}. <b>{p.name}</b> — {p.price:.0f}₽ ({p.store})\n"
            
            text += f"\nКакой выбираешь? (напиши номер или название)"
            
            return AgentResponse(
                text=text,
                sources=[{"product_id": p.id} for p in best_products],
                actions=[{"type": "select_product", "options": [{"id": p.id, "name": p.name, "price": p.price} for p in best_products]}],
                confidence=0.85,
                processing_time_ms=0
            )
    
    async def _handle_commerce_compare(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Сравнение цен в разных магазинах"""
        query = self._extract_query(user_input, IntentType.COMMERCE_COMPARE)
        
        search_result = await self.commerce_agent.search_across_stores(
            query=query,
            stores=["samokat", "papa_johns", "yandex_lavka", "ozon"]
        )
        
        if search_result["total_found"] < 2:
            return AgentResponse(
                text=f"📊 Недостаточно данных для сравнения «{query}».\n"
                     f"Найдено только в {search_result['stores_searched'][0] if search_result['stores_searched'] else 'одном магазине'}.",
                sources=[],
                confidence=0.8,
                processing_time_ms=0
            )
        
        # Группируем по товарам и сравниваем цены
        by_store = search_result.get("store_breakdown", {})
        
        response_text = f"📊 Сравнение цен на «{query}»:\n\n"
        
        # Таблица сравнения
        for store_id, data in by_store.items():
            if "error" in data:
                continue
            
            products = data.get("products", [])
            if products:
                cheapest = min(products, key=lambda p: p.price)
                response_text += (
                    f"<b>{store_id}</b>:\n"
                    f"  от {cheapest.price:.0f}₽ — {cheapest.name}\n"
                    f"  ⏱️ {cheapest.delivery_time or 'уточняется'}\n\n"
                )
        
        # Рекомендация
        all_products = search_result.get("best_options", [])
        if all_products:
            best = min(all_products, key=lambda p: p.price)
            response_text += (
                f"💡 <b>Выгоднее всего:</b> {best.name} в {best.store} "
                f"за {best.price:.0f}₽"
            )
        
        return AgentResponse(
            text=response_text,
            sources=[{"store": s, "products": len(d.get("products", []))} for s, d in by_store.items() if "error" not in d],
            actions=[{"type": "order_cheapest", "product_id": best.id} if all_products else {}],
            confidence=0.85,
            processing_time_ms=0
        )
    
    async def _handle_commerce_repeat(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Повторение предыдущего заказа"""
        # Ищем в памяти прошлые заказы
        order_memories = await self.memory_agent.recall(
            query="заказ оформлен",
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            top_k=5
        )
        
        if not order_memories:
            return AgentResponse(
                text="🤔 Не нашёл недавних заказов.\n\n"
                     "Сделай первый заказ — напиши «закажи пиццу» или «купи продукты»",
                sources=[],
                actions=[{"type": "suggest_first_order"}],
                confidence=0.9,
                processing_time_ms=0
            )
        
        # Парсим последний заказ
        last_order = order_memories[0]
        
        # Пытаемся извлечь детали из контента
        content = last_order.content
        
        return AgentResponse(
            text=(
                f"🔄 <b>Повторить заказ?</b>\n\n"
                f"Последний заказ:\n"
                f"<i>{content[:200]}{'...' if len(content) > 200 else ''}</i>\n\n"
                f"📍 Адрес: (из профиля)\n"
                f"💳 Оплата: картой онлайн\n\n"
                f"Подтверждаешь?"
            ),
            sources=[{"last_order_memory_id": last_order.id}],
            actions=[
                {"type": "confirm_repeat_order", "memory_id": last_order.id},
                {"type": "modify_order", "memory_id": last_order.id},
                {"type": "show_order_history"}
            ],
            confidence=0.85,
            processing_time_ms=0
        )
    
    async def _handle_commerce_track(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Трекинг заказа"""
        # Ищем активные заказы в памяти
        active_orders = await self.memory_agent.recall(
            query="заказ активен доставка",
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            top_k=3
        )
        
        if not active_orders:
            return AgentResponse(
                text="📦 Нет активных заказов.\n\n"
                     "Последние заказы уже доставлены или отменены.\n"
                     "История: /orders",
                sources=[],
                actions=[{"type": "show_order_history"}],
                confidence=0.9,
                processing_time_ms=0
            )
        
        # Показываем статус последнего активного
        order = active_orders[0]
        
        return AgentResponse(
            text=(
                f"📦 <b>Статус заказа</b>\n\n"
                f"<i>{order.content[:150]}</i>\n\n"
                f"⏱️ Статус: В пути (примерно)\n"
                f"🚚 Ожидаемое время: 15-20 мин\n\n"
                f"Обновить статус: нажми /track"
            ),
            sources=[{"order_memory_id": order.id}],
            actions=[
                {"type": "refresh_tracking"},
                {"type": "contact_support"},
                {"type": "cancel_order"}
            ],
            confidence=0.7,  # Низкая уверенность т.к. мок
            processing_time_ms=0
        )
    
    async def _handle_profile_update(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Обновление профиля пользователя"""
        # Профиль обновляется автоматически через profile_agent
        # Здесь можно добавить явное подтверждение
        
        update_result = await self.profile_agent.update_from_conversation(
            user_id=user_id,
            conversation=user_input
        )
        
        if update_result.get("updated"):
            fields = ", ".join(update_result.get("fields_updated", []))
            return AgentResponse(
                text=f"✅ Обновил профиль: {fields}\n\n"
                     f"Теперь я знаю о тебе больше и смогу лучше помогать!",
                sources=[{"updated_fields": update_result.get("fields_updated", [])}],
                confidence=0.95,
                processing_time_ms=0
            )
        else:
            return AgentResponse(
                text="📝 Записал. Эта информация поможет мне лучше понимать твои запросы.",
                sources=[],
                confidence=0.8,
                processing_time_ms=0
            )
    
    async def _handle_unknown(
        self,
        user_input: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Обработка неопределённых запросов"""
        return AgentResponse(
            text="🤔 Не совсем понял. Попробуй:\n"
                 "• Переформулировать вопрос\n"
                 "• Написать /help для справки\n"
                 "• Или просто расскажи, что тебе нужно — я разберусь",
            sources=[],
            actions=[{"type": "show_help"}, {"type": "clarify_intent"}],
            confidence=0.5,
            processing_time_ms=0
        )

    # ==================== PUBLIC HELPERS ====================

    async def memory_query(self, user_input: str, user_id: str) -> AgentResponse:
        """Публичная обёртка для поиска по памяти"""
        return await self._handle_memory_query(user_input, user_id, {})

    async def memory_delete(self, user_input: str, user_id: str) -> AgentResponse:
        """Публичная обёртка для удаления памяти (не используется в API)"""
        return await self._handle_memory_delete(user_input, user_id, {})
    
    # ========== PUBLIC API METHODS ==========
    
    async def process_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Обработка загруженного файла через DocumentAgent
        """
        return await self.document_agent.process_file(
            file_content=file_content,
            filename=filename,
            user_id=user_id,
            metadata=metadata or {}
        )
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Получение статистики памяти пользователя"""
        return await self.memory_agent.get_stats(user_id)
    
    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Получение профиля пользователя"""
        profile = await self.profile_agent.get_profile(user_id)
        return profile.model_dump()
    
    async def update_commerce_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновление коммерческого профиля"""
        return await self.profile_agent.update_commerce_profile(user_id, updates)
    
    async def create_order(
        self,
        store_id: str,
        items: List[Dict[str, Any]],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Создание заказа (вызывается после подтверждения пользователя)
        """
        order = await self.commerce_agent.create_order(
            store_id=store_id,
            items=items,
            user_id=user_id
        )
        
        # Сохраняем в память
        order_text = (
            f"Заказ оформлен: {order.id}\\n"
            f"Магазин: {order.store}\\n"
            f"Сумма: {order.total}₽\\n"
            f"Статус: {order.status}"
        )
        
        await self.memory_agent.store(
            content=order_text,
            user_id=user_id,
            memory_type=MemoryType.EPISODIC,
            importance=0.7,
            source="system",
            metadata={"order_id": order.id, "store": store_id, "total": order.total}
        )
        
        return {
            "order_id": order.id,
            "store": order.store,
            "total": order.total,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None
        }

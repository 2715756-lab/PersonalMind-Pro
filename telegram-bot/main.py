"""Telegram Bot основной файл"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from telegram_bot.app.config import BOT_TOKEN, BACKEND_URL
from telegram_bot.app.handlers.commands import start, help_command
from telegram_bot.app.handlers.messages import handle_message
from telegram_bot.app.handlers.commerce import search_command, order_command
from telegram_bot.app.handlers.files import handle_file


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Запуск бота"""
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers для команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("order", order_command))

    # Handler для текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handler для файлов
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Запуск бота
    logger.info("🤖 Telegram Bot запускается...")
    application.run_polling()


if __name__ == "__main__":
    main()

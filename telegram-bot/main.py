"""🤖 PersonalMind Pro - Telegram Bot Entry Point"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import commands, messages, files, callbacks


# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск Telegram Bot"""
    
    logger.info("🤖 Initializing PersonalMind Pro Telegram Bot...")
    
    # Check token
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment!")
        sys.exit(1)
    
    logger.info(f"✅ Bot Token configured")
    logger.info(f"✅ Backend URL: {settings.BACKEND_URL}")
    
    # Initialize bot & dispatcher
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register handlers
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    dp.include_router(files.router)
    dp.include_router(callbacks.router)
    
    logger.info("📝 Event handlers registered")
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"✅ Connected to Telegram API")
        logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.first_name})")
        
        # Start polling
        logger.info("🚀 Starting polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

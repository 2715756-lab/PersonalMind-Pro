from io import BytesIO

from aiogram import Bot, Dispatcher, types

from app.services.api_client import BackendClient, BackendError


def register_message_handlers(dp: Dispatcher, backend: BackendClient, bot: Bot):
    @dp.message_handler(content_types=types.ContentType.TEXT)
    async def handle_text(message: types.Message):
        text = (message.text or "").strip()
        if not text or text.startswith("/"):
            return
        try:
            response = await backend.chat(str(message.from_user.id), text)
        except BackendError as exc:
            await message.reply(f"⚠️ Ошибка: {exc}")
            return
        await message.reply(response)

    @dp.message_handler(content_types=types.ContentType.DOCUMENT)
    async def handle_document(message: types.Message):
        if not message.document:
            return
        try:
            file_info = await bot.get_file(message.document.file_id)
            buffer = BytesIO()
            await bot.download_file(file_info.file_path, buffer)
            buffer.seek(0)
            await backend.upload_document(
                user_id=str(message.from_user.id),
                filename=message.document.file_name or "document",
                content=buffer.read()
            )
            await message.reply("📁 Документ принят! Я добавил его в память.")
        except BackendError as exc:
            await message.reply(f"⚠️ Не удалось загрузить файл: {exc}")
        except Exception as exc:
            await message.reply(f"⚠️ Не удалось обработать файл: {exc}")

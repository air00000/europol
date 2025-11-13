# bot/telegram_bot.py — основной функционал бота
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import requests
import os

from config import BOT_TOKEN, API_URL
from database.users import init_db, is_user_allowed
from bot.admin import get_admin_handlers, is_admin

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

WAITING_LINK = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверяем доступ
    if not is_user_allowed(user_id) and not is_admin(user_id):
        await update.message.reply_text(
            "❌ Доступ запрещен.\n\n"
            "Вы не находитесь в списке разрешенных пользователей. "
            "Обратитесь к администратору для получения доступа."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "🇪🇺 Europol PDF генератор\n\n"
        "Пришли мне ссылку для верификации (http/https)\n"
        "Я вставлю её в кнопку в PDF и пришлю готовый файл.\n\n"
        "⚡ Просто отправь мне ссылку!"
    )
    return WAITING_LINK


async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверяем доступ
    if not is_user_allowed(user_id) and not is_admin(user_id):
        await update.message.reply_text("❌ Доступ запрещен")
        return ConversationHandler.END

    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Ошибка: ссылка должна начинаться с http:// или https://")
        return WAITING_LINK

    await update.message.reply_text("⏳ Генерирую PDF с твоей ссылкой...")

    try:
        r = requests.post("http://localhost:8000/generate_pdf", json={"url": url}, timeout=60)
        if r.status_code == 200:
            path = os.path.join(TEMP_DIR, "europol_verification.pdf")
            with open(path, "wb") as f:
                f.write(r.content)
            with open(path, "rb") as f:
                await update.message.reply_document(
                    f,
                    filename="Europol_Verification.pdf",
                    caption="✅ Готово! Кнопка в PDF кликабельная."
                )
            os.remove(path)
        else:
            await update.message.reply_text(f"❌ Ошибка сервера: {r.status_code}\n{r.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id) and not is_admin(user_id):
        await update.message.reply_text("❌ Доступ запрещен")
        return

    help_text = (
        "🇪🇺 Europol PDF Generator Help\n\n"
        "📋 Доступные команды:\n"
        "/start - Начать генерацию PDF\n"
        "/help - Показать эту справку\n"
        "/cancel - Отменить текущую операцию\n\n"
        "🛠️ Административные команды:\n"
        "/add_user <id> - Добавить пользователя\n"
        "/remove_user <id> - Удалить пользователя\n"
        "/list_users - Список пользователей\n"
        "/stats - Статистика бота\n\n"
        "💡 Просто отправьте мне ссылку после команды /start!"
    )

    await update.message.reply_text(help_text)


def setup_bot():
    """Настройка и запуск бота"""
    # Инициализация БД
    init_db()

    # Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # Основной conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Добавляем обработчики
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))

    # Административные команды
    for handler in get_admin_handlers():
        app.add_handler(handler)

    return app
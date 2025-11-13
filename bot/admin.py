# bot/admin.py — административные команды бота
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
import re

from database.users import add_user, remove_user, get_all_users, is_user_allowed
from config import ADMIN_IDS


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


async def admin_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить пользователя в разрешенные"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет прав администратора")
        return

    if not context.args:
        await update.message.reply_text(
            "Использование: /add_user <user_id> или /add_user @username"
        )
        return

    target = context.args[0]

    # Определяем ID пользователя
    if target.startswith('@'):
        # По username - в реальном боте нужно получить ID через API
        await update.message.reply_text("❌ Добавление по username пока не поддерживается. Используйте user_id.")
        return
    elif re.match(r'^\d+$', target):
        user_id = int(target)

        # Добавляем пользователя
        success = add_user(
            user_id=user_id,
            username="",  # Можно дополнительно получать информацию о пользователе
            first_name="",
            last_name="",
            added_by=update.effective_user.id
        )

        if success:
            await update.message.reply_text(f"✅ Пользователь {user_id} добавлен в разрешенные")
        else:
            await update.message.reply_text("❌ Ошибка при добавлении пользователя")
    else:
        await update.message.reply_text("❌ Неверный формат. Используйте: /add_user <user_id>")


async def admin_remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить пользователя из разрешенных"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет прав администратора")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Использование: /remove_user <user_id>")
        return

    user_id = int(context.args[0])

    if remove_user(user_id):
        await update.message.reply_text(f"✅ Пользователь {user_id} удален из разрешенных")
    else:
        await update.message.reply_text(f"❌ Пользователь {user_id} не найден в списке разрешенных")


async def admin_list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список разрешенных пользователей"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет прав администратора")
        return

    users = get_all_users()

    if not users:
        await update.message.reply_text("📝 Список разрешенных пользователей пуст")
        return

    message = "📋 Разрешенные пользователи:\n\n"
    for user in users:
        message += f"🆔 ID: {user['user_id']}\n"
        if user['username']:
            message += f"👤 @{user['username']}\n"
        if user['first_name']:
            message += f"📛 Имя: {user['first_name']}"
            if user['last_name']:
                message += f" {user['last_name']}"
            message += "\n"
        message += f"📅 Добавлен: {user['added_at']}\n"
        message += "─" * 20 + "\n"

    # Разбиваем сообщение если оно слишком длинное
    if len(message) > 4096:
        chunks = [message[i:i + 4096] for i in range(0, len(message), 4096)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(message)


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У вас нет прав администратора")
        return

    users = get_all_users()

    message = (
        "📊 Статистика бота:\n\n"
        f"👥 Всего разрешенных пользователей: {len(users)}\n"
        f"🛠️ Администраторов: {len(ADMIN_IDS)}\n"
        f"🔧 Ваш ID: {update.effective_user.id}"
    )

    await update.message.reply_text(message)


def get_admin_handlers():
    """Получить обработчики административных команд"""
    return [
        CommandHandler("add_user", admin_add_user),
        CommandHandler("remove_user", admin_remove_user),
        CommandHandler("list_users", admin_list_users),
        CommandHandler("stats", admin_stats),
    ]
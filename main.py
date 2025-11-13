# main.py — запуск приложения
import threading
import uvicorn
import logging
from bot.telegram_bot import setup_bot
from api.pdf_generator import app as api_app
from config import API_HOST, API_PORT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def run_api():
    """Запуск FastAPI сервера"""
    logging.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(api_app, host="0.0.0.0", port=8001)


def run_bot():
    """Запуск Telegram бота"""
    logging.info("Starting Telegram bot...")
    app = setup_bot()
    app.run_polling()


if __name__ == "__main__":
    print("🚀 Europol PDF Generator Starting...")
    print("📊 API Server: http://localhost:8001")
    print("🤖 Telegram Bot: Running...")
    print("🛠️  Admin features: Enabled")

    # Запускаем API в отдельном потоке
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Запускаем бота в основном потоке
    run_bot()
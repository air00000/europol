# config.py — настройки приложения
import os
from dotenv import load_dotenv

load_dotenv()

# Figma API
FIGMA_TOKEN = os.getenv('FIGMA_TOKEN')
FILE_KEY = os.getenv('FILE_KEY')
FRAME_NAME = "europol1"
BUTTON_NAME = "europol1botton"
PAGE_NAME = "Page 2"
SCALE = 2
CONV = 72 / 96

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

# API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
API_URL = f"http://localhost:{API_PORT}/generate_pdf"

# Admin
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
from telegram import Bot
from telegram.error import TimedOut
from telegram.request import HTTPXRequest
from .config import TELEGRAM_TOKEN, CHAT_ID, LOG_FILE

import asyncio
import time

_request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
bot = Bot(token=TELEGRAM_TOKEN, request=_request)

# Funkcja: Wiadomość ze zdjęciem
async def send_telegram_message(message, photo_url=None):
    for attempt in range(3):  # do 3 prób
        try:
            if photo_url:
                await bot.send_photo(chat_id=CHAT_ID, photo=photo_url, caption=message)
            else:
                await bot.send_message(chat_id=CHAT_ID, text=message)
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{time.ctime()}] Wysłano: {message}\n")
            break
        except TimedOut:
            print(f"[{time.ctime()}] Timeout, ponawiam próbę...")
            time.sleep(5)
        except Exception as e:
            error_msg = f"[{time.ctime()}] Błąd wysyłania: {str(e)}\n"
            print(error_msg)
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(error_msg)
            break

# Funkcja: Wiele wiadomości
async def send_multiple_telegram_messages(messages):
    for message, photo_url in messages:
        await send_telegram_message(message, photo_url)
        await asyncio.sleep(3)

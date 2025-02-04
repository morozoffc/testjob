import requests
import json
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from typing import List


# Настройки./
API_TOKEN = "e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b"
TG_BOT_TOKEN = "8107341922:AAGU959m9dqsnRCpC9vcsA-oxezLRjek3Ho"
AUTHORIZED_USERS = {989765619}  # Замените на реальные ID пользователей
AUTHORIZED_API_TOKENS = {"secure_token_123"}  # Токены для API
IMEI_API_URL = "https://imeicheck.net/api"

# Инициализация FastAPI
app = FastAPI()


class IMEIRequest(BaseModel):
    imei: str
    token: str


def check_imei(imei: str):
    response = requests.get(f"{IMEI_API_URL}?imei={imei}&token={API_TOKEN}")
    return response.json()


@app.post("/api/check-imei")
def api_check_imei(request: IMEIRequest):
    if request.token not in AUTHORIZED_API_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid token")

    imei_info = check_imei(request.imei)
    return imei_info


# Инициализация Telegram-бота
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def handle_imei_check(message: Message):
    if message.from_user.id not in AUTHORIZED_USERS:
        await message.reply("У вас нет доступа к боту.")
        return

    imei = message.text.strip()
    if not imei.isdigit() or len(imei) not in (14, 15):
        await message.reply("Некорректный IMEI. Введите 14-15 цифр.")
        return

    imei_info = check_imei(imei)
    response_text = json.dumps(imei_info, indent=4, ensure_ascii=False)
    await message.reply(f"Результат проверки IMEI:\n{response_text}")


if __name__ == "__main__":
    from threading import Thread
    import uvicorn


    def start_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)


    Thread(target=start_fastapi, daemon=True).start()
    executor.start_polling(dp, skip_updates=True)

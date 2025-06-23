import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiohttp import web
import aiohttp
import json

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GIFT_URL = os.getenv("GIFT_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Получить подарок 🎁", callback_data="get_gift"))
    await message.answer("Привет! Нажми на кнопку ниже, чтобы получить подарок за подписку на канал 😊", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "get_gift")
async def handle_gift_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await bot.send_message(user_id, f"Спасибо за подписку! Вот ваш подарок 🎁:\n{GIFT_URL}")
    else:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{os.getenv('CHANNEL_USERNAME')}")
        )
        await bot.send_message(user_id, "Пожалуйста, подпишитесь на канал, чтобы получить подарок.", reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)

async def on_startup(_):
    print("Бот запущен")

# Для запуска вебхука
async def webhook_handler(request):
    data = await request.json()
    update = types.Update.to_object(data)
    await dp.process_update(update)
    return web.Response()

def start():
    app = web.Application()
    app.router.add_post('/', webhook_handler)
    return app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(start(), port=80)


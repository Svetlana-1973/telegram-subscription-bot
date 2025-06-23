import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GIFT_URL = os.getenv("GIFT_URL")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📥 Получить подарок", callback_data="get_gift"),
        InlineKeyboardButton("📌 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME}")
    )
    await message.answer("Привет! Подпишись и получи подарок 🎁", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "get_gift")
async def handle_gift_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await bot.send_message(user_id, f"Спасибо за подписку! Вот твой подарок 🎁:\n{GIFT_URL}")
    else:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📌 Подписаться", url=f"https://t.me/{CHANNEL_USERNAME}")
        )
        await bot.send_message(user_id, "Похоже, ты ещё не подписан на канал. Подпишись и вернись за подарком 😉", reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)

async def webhook_handler(request):
    try:
        data = await request.json()
        update = types.Update.to_object(data)
        await dp.process_update(update)
        return web.Response()
    except:
        return web.Response(status=500)

def start():
    app = web.Application()
    app.router.add_post('/', webhook_handler)
    return app

if __name__ == '__main__':
    web.run_app(start(), port=80)

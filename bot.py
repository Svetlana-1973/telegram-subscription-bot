import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import aiohttp
import json

# Получаем переменные окружения
API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GIFT_URL = os.getenv("GIFT_URL")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Проверка подписки
async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Получить подарок 🎁", callback_data="get_gift")
    )
    await message.answer(
        "Привет! Подпишись на канал и получи подарок 😊",
        reply_markup=keyboard
    )

# Обработка кнопки "Получить подарок"
@dp.callback_query_handler(lambda c: c.data == "get_gift")
async def handle_gift_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await bot.send_message(user_id, f"Спасибо за подписку! Вот ваш подарок 🎁:\n{GIFT_URL}")
    else:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Подписаться на канал", url=CHANNEL_LINK)
        )
        await bot.send_message(
            user_id,
            "Пожалуйста, подпишитесь на канал, чтобы получить подарок.",
            reply_markup=keyboard
        )
    await bot.answer_callback_query(callback_query.id)

# Обработка webhook
async def webhook_handler(request):
    data = await request.json()
    update = types.Update.to_object(data)
    await dp.process_update(update)
    return web.Response()

# Старт веб-приложения
def start():
    app = web.Application()
    app.router.add_post('/', webhook_handler)
    return app

# Запуск
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(start(), port=80)

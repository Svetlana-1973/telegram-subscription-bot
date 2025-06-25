import os
import ssl
from dotenv import load_dotenv
load_dotenv()

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
GIFT_URL = os.getenv("GIFT_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SSL_KEY_PATH = os.getenv("SSL_KEY_PATH", "ssl/key.pem")
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "ssl/cert.pem")

if not all([BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, CHANNEL_LINK, GIFT_URL, WEBHOOK_URL]):
    print("ОШИБКА: Не все переменные окружения заданы.")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.is_chat_member()
    except:
        return False

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("👉 Подписаться", url=CHANNEL_LINK),
        InlineKeyboardButton("🎁 Получить подарок", callback_data="get_gift")
    )
    await message.reply("Привет! Подпишись на канал и получи подарок 🎁", reply_markup=keyboard)

@dp.callback_query_handler(text="get_gift")
async def handle_get_gift_button(call: types.CallbackQuery):
    user_id = call.from_user.id
    if await is_subscribed(user_id):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("⬇️ Скачать подарок", url=GIFT_URL))
        await call.message.reply("Спасибо за подписку! Вот твой подарок 🎁", reply_markup=keyboard)
    else:
        await call.message.reply("Пожалуйста, подпишись на канал, чтобы получить подарок 🎁")
    await call.answer()

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен на: {WEBHOOK_URL}")

async def on_shutdown(dp):
    print("Бот выключается.")

async def handle(request):
    if request.method == "POST":
        data = await request.text()
        update = types.Update.de_json(data)
        await dp.process_update(update)
        return web.Response(text="ok")
    else:
        return web.Response(status=405)

if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)

    app = web.Application()
    app.router.add_post('/', handle)

    web.run_app(
        app,
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 443)),
        ssl_context=ssl_context
    )

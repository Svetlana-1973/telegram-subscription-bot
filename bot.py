import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. Загрузка данных из файла .env ---
# Бот будет читать свои настройки (токен, ID канала и т.д.) из файла .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_LINK = os.getenv("CHANNEL_LINK") # Специальная ссылка для отслеживания статистики
GIFT_URL = os.getenv("GIFT_URL")

if not all([BOT_TOKEN, CHANNEL_ID, CHANNEL_USERNAME, CHANNEL_LINK, GIFT_URL]):
    print("ОШИБКА: Один или несколько параметров в файле .env отсутствуют. Пожалуйста, проверьте файл .env.")
    exit(1) # Завершаем работу, если нет важных данных

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.is_chat_member()
    except Exception as e:
        print(f"Ошибка при проверке подписки пользователя {user_id} в канале {CHANNEL_ID}: {e}")
        return False # Если ошибка, считаем, что пользователь не подписан

@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    user_id = message.from_user.id

    keyboard = InlineKeyboardMarkup()
    button_subscribe = InlineKeyboardButton("👉 Подписаться", url=CHANNEL_LINK) # Ведет на спец. ссылку
    button_get_gift = InlineKeyboardButton("🎁 Получить подарок", callback_data="get_gift") # Кнопка для получения подарка

    keyboard.add(button_subscribe, button_get_gift)

    await message.reply("Привет! Подпишись на канал и получи подарок 🎁", reply_markup=keyboard)

@dp.callback_query_handler(text="get_gift")
async def handle_get_gift_button(call: types.CallbackQuery):
    user_id = call.from_user.id

    if await is_subscribed(user_id):
       
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("⬇️ Скачать подарок", url=GIFT_URL)) # Кнопка для скачивания подарка
        await call.message.reply("Спасибо за подписку! Вот твой подарок 🎁", reply_markup=keyboard)
    else:
        await call.message.reply("Пожалуйста, подпишись на канал, чтобы получить подарок 🎁")

    await call.answer()

async def on_startup(dp):
    print("Бот успешно запущен и готов принимать обновления через вебхук.")

async def on_shutdown(dp):
    print("Бот выключается.")

if __name__ == '__main__':
  
    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/', 
        on_startup=on_startup, 
        on_shutdown=on_shutdown, 
        skip_updates=True, 
        host='0.0.0.0',   
        port=int(os.environ.get("PORT", 80)) 
    )

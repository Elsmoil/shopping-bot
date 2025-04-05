from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import aiohttp

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

# Tracked products (in-memory for demo; use KV later)
tracked_products = {}

# Command: /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🛍️ Welcome! Use:\n"
                      "/search [product] - Compare prices\n"
                      "/track [URL] - Track price drops")

# Command: /search (price comparison)
@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    product = ' '.join(message.text.split()[1:])
    affiliate_links = {
        "Amazon": f"https://amazon.com/s?k={product}&tag=YOUR_AFFILIATE_ID",
        "AliExpress": f"https://aliexpress.com/wholesale?SearchText={product}"
    }
    reply = "🔍 Results:\n" + "\n".join([f"{store}: {link}" for store, link in affiliate_links.items()])
    await message.reply(reply)

# Command: /track (price tracking)
@dp.message_handler(commands=['track'])
async def track(message: types.Message):
    url = message.text.split()[1]
    tracked_products[url] = message.chat.id
    await message.reply("✅ Tracking this product! I’ll alert you if the price drops.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)

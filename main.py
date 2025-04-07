import os
import aiohttp
import json
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from typing import Dict, Optional, List

# --- Configuration ---
class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    AMAZON_AFF_ID = os.getenv("AMAZON_AFF_ID", "smartshopp0db-20")
    ALIEXPRESS_PID = os.getenv("ALIEXPRESS_PID")
    CLOUDFLARE_WORKER_URL = os.getenv("CLOUDFLARE_WORKER_URL")
    KV_NAMESPACE_ID = os.getenv("KV_NAMESPACE_ID")  # From Cloudflare Workers KV

# --- Initialize Bot ---
bot = Bot(token=Config.TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- KV Database Helper ---
async def kv_fetch(key: str) -> Optional[Dict]:
    """Fetch data from Cloudflare KV"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{Config.CLOUDFLARE_WORKER_URL}/kv/{key}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"KV Fetch Error: {e}")
    return None

async def kv_store(key: str, data: Dict) -> bool:
    """Store data in Cloudflare KV"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{Config.CLOUDFLARE_WORKER_URL}/kv/{key}"
            async with session.post(url, json=data) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"KV Store Error: {e}")
        return False

# --- Affiliate Logic ---
def generate_affiliate_links(product: str) -> Dict[str, str]:
    return {
        "Amazon": f"https://www.amazon.com/s?k={product}&tag={Config.AMAZON_AFF_ID}",
        "AliExpress": f"https://www.aliexpress.com/wholesale?SearchText={product}&aff_fcid={Config.ALIEXPRESS_PID}"
    }

# --- Handlers ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply(
        "🛍️ *Smart Shopping Assistant*\n\n"
        "Track prices and find deals:\n"
        "/search [product] - Compare prices\n"
        "/track [url] - Monitor price drops\n"
        "/mytracks - Your tracked items",
        parse_mode="Markdown"
    )

@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    product = ' '.join(message.text.split()[1:])
    if not product:
        await message.reply("⚠️ Please specify a product!")
        return

    links = generate_affiliate_links(product)
    reply = (
        "🔍 *Product Search Results*\n\n"
        f"🛒 **Amazon**: [View]({links['Amazon']})\n"
        f"🛒 **AliExpress**: [View]({links['AliExpress']})\n\n"
        "#ad - Prices may vary"
    )
    await message.reply(reply, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message_handler(commands=['track'])
async def track(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("⚠️ Please include a product URL!")
        return

    user_id = message.from_user.id
    product_url = args[1]
    
    # Get existing tracks
    user_data = await kv_fetch(f"user:{user_id}") or {"tracks": []}
    
    # Add new track
    if product_url not in user_data["tracks"]:
        user_data["tracks"].append(product_url)
        await kv_store(f"user:{user_id}", user_data)
        await message.reply("✅ Price tracking activated!")
    else:
        await message.reply("ℹ️ You're already tracking this item.")

@dp.message_handler(commands=['mytracks'])
async def my_tracks(message: types.Message):
    user_id = message.from_user.id
    user_data = await kv_fetch(f"user:{user_id}")
    
    if not user_data or not user_data.get("tracks"):
        await message.reply("You're not tracking any items yet.")
        return
    
    reply = "📋 *Your Tracked Items*\n\n" + "\n".join(
        f"• [Item {i+1}]({url})" for i, url in enumerate(user_data["tracks"])
    )
    await message.reply(reply, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == '__main__':
    # Validate config
    if not all([Config.TELEGRAM_TOKEN, Config.AMAZON_AFF_ID]):
        raise ValueError("Missing required environment variables")
    
    executor.start_polling(dp, skip_updates=True)

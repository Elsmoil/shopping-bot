import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Initialize bot with environment variables
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

# Tracked products (in-memory for demo)
tracked_products = {}

def generate_affiliate_links(product: str) -> dict:
    """Generate affiliate links safely using env vars."""
    return {
        "Amazon": f"https://www.amazon.com/s?k={product}&tag={os.getenv('AMAZON_AFF_ID')}",
        "AliExpress": f"https://www.aliexpress.com/wholesale?SearchText={product}&aff_fcid={os.getenv('ALIEXPRESS_PID')}"
    }

@dp.message_handler(commands=['search'])
async def search(message: types.Message):
    product = ' '.join(message.text.split()[1:])
    if not product:
        await message.reply("⚠️ Please specify a product! Example: /search wireless earbuds")
        return
    
    links = generate_affiliate_links(product)
    reply = (
        "🔍 *Product Search Results*\n\n"
        f"🛒 **Amazon**: [Click Here]({links['Amazon']})\n"
        f"🛒 **AliExpress**: [Click Here]({links['AliExpress']})\n\n"
        "#ad - Prices may vary"
    )
    await message.reply(reply, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == '__main__':
    executor.start_polling(dp)

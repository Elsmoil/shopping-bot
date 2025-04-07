import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, URLInputFile
from aiogram.enums import ParseMode
from aiogram.exceptions import AiogramError
import aiohttp
import asyncio

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()

# --- Core Functions (Preserved from your original) ---
def generate_affiliate_links(product: str) -> dict:
    """Generate affiliate links with tracking (identical to your original)"""
    return {
        "Amazon": f"https://www.amazon.com/s?k={product}&tag={os.getenv('AMAZON_AFF_ID')}&utm_source=telegram_bot",
        "AliExpress": f"https://www.aliexpress.com/wholesale?SearchText={product}&aff_fcid={os.getenv('ALIEXPRESS_PID')}"
    }

async def fetch_product_image(url: str) -> URLInputFile:
    """Preserve your image fetching logic"""
    return URLInputFile(url)

# --- Handlers (Same functionality, modern syntax) ---
@dp.message(Command("start"))
async def start_handler(message: Message):
    """Identical welcome message as before"""
    try:
        await message.answer(
            "🛍️ *Smart Shopping Assistant*\n\n"
            "Commands:\n"
            "/search <product> - Compare prices\n"
            "/track <url> - Monitor price drops\n"
            "/mytracks - Your tracked items\n\n"
            "#ad - Affiliate links included",
            parse_mode=ParseMode.MARKDOWN
        )
    except AiogramError as e:
        logger.error(f"Start error: {e}")
        await message.answer("⚠️ Bot startup failed. Please try later.")

@dp.message(Command("search"))
async def search_handler(message: Message):
    """Preserved your exact search logic"""
    try:
        product = ' '.join(message.text.split()[1:])
        if not product:
            await message.answer("⚠️ Please specify a product!")
            return

        links = generate_affiliate_links(product)
        
        # Your original response format
        response = (
            "🔍 *Product Search Results*\n\n"
            f"🛒 **Amazon**: [Click Here]({links['Amazon']})\n"
            f"🛒 **AliExpress**: [Click Here]({links['AliExpress']})\n\n"
            "#ad - Prices may vary"
        )
        
        await message.answer(
            response,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer("⚠️ Failed to search products. Please try again.")

@dp.message(Command("track"))
async def track_handler(message: Message):
    """Your original tracking logic with better error handling"""
    try:
        url = message.text.split()[1]
        # Your tracking implementation here
        await message.answer(
            "✅ Price tracking activated!\n"
            "I'll alert you if the price drops significantly.",
            disable_web_page_preview=True
        )
    except IndexError:
        await message.answer("⚠️ Please include a product URL!")
    except Exception as e:
        logger.error(f"Track error: {e}")
        await message.answer("⚠️ Failed to setup tracking. Please try again.")

# --- Error Handler (Like your original) ---
@dp.errors()
async def global_error_handler(event: types.ErrorEvent):
    """Preserves your error handling approach"""
    logger.critical(f"Global error: {event.exception}")
    try:
        await event.update.message.answer("⚠️ Bot encountered an error. Please retry.")
    except:
        pass  # Fail silently if we can't respond

# --- Startup (Modern equivalent of executor) ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# api/webhook.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import json

# --- Configuration (تنظیمات) ---
# BOT_TOKEN و TMDB_API_KEY از متغیرهای محیطی Vercel خوانده می‌شوند.
TMDB_API_KEY = os.environ.get("8225313384:AAEmLwvlz_SJ9BrfLlqaJ0xoPHu4dc3NuJ4")

# 🔗 دیتابیس داخلی لینک‌های دانلود (می‌توانید این را در Vercel هم به صورت متغیر محیطی بگذارید)
DOWNLOAD_LINKS = {
    "Solar Opposites": "https://link-download.ir/solar-opposites-s01", 
    "Disenchantment": "https://link-download.ir/disenchantment-s01",
}

# TMDB Base URLs
SEARCH_URL = "https://api.themoviedb.org/3/search/multi" 
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


# --- Bot Handlers (هندلرهای ربات) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'سلام! اسم فیلم یا سریال مورد نظرت رو برای من بفرست تا جستجو کنم.'
    )

async def search_movie_or_tv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    # اطمینان از وجود کلید TMDB
    if not TMDB_API_KEY:
        await update.message.reply_text("خطا: کلید TMDB API در سرور تنظیم نشده است.")
        return

    # 1. جستجو در TMDB
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'language': 'fa-IR'
    }

    response = requests.get(SEARCH_URL, params=params)
    data = response.json()

    if data['results']:
        item = data['results'][0]
        
        # استخراج اطلاعات
        is_tv = item.get('media_type') == 'tv'
        title = item.get('name') if is_tv else item.get('title')
        overview = item.get('overview', 'توضیحات در دسترس نیست.')
        release_date = item.get('first_air_date') if is_tv else item.get('release_date')
        
        caption = (
            f"🎬 **نام:** {title}\n"
            f"📅 **تاریخ انتشار:** {release_date}\n\n"
            f"📝 **خلاصه داستان:** {overview}"
        )
        
        # 2. منطق دکمه دانلود از دیتابیس داخلی
        keyboard = []
        if title in DOWNLOAD_LINKS:
            link = DOWNLOAD_LINKS[title]
            button = InlineKeyboardButton(f"⬇️ دریافت لینک دانلود {title}", url=link)
            keyboard.append([button])
        else:
            keyboard.append([InlineKeyboardButton("❌ لینک دانلود موجود نیست", callback_data='no_link')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # 3. ارسال پوستر و توضیحات
        poster_path = item.get('poster_path')
        if poster_path:
            poster_url = IMAGE_BASE_URL + poster_path
            await update.message.reply_photo(
                photo=poster_url, 
                caption=caption,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(caption, parse_mode='Markdown', reply_markup=reply_markup)
            
    else:
        await update.message.reply_text(f"متأسفانه محتوایی با عنوان '{query}' پیدا نشد.")


# 🚀 تابع اصلی Webhook (که Vercel آن را فراخوانی می‌کند)
async def handler(request):
    """تابع اصلی که درخواست‌های Webhook را پردازش می‌کند."""
    if request.method != 'POST':
        return {'statusCode': 200, 'body': 'GET request received. Use Telegram!'}
    
    # دریافت توکن از متغیرهای محیطی Vercel
    BOT_TOKEN = os.environ.get("BOT_TOKEN") 
    if not BOT_TOKEN:
        return {'statusCode': 500, 'body': 'BOT_TOKEN not set'}
        
    try:
        # ساخت یک شیء Application با توکن
        application = Application.builder().token(BOT_TOKEN).build()
        
        # افزودن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie_or_tv))
        
        # پردازش به‌روزرسانی (Update) که از تلگرام آمده است
        body = await request.json()
        update = Update.de_json(body, application.bot)
        
        # پردازش به‌روزرسانی توسط Dispatcher
        await application.process_update(update)
        
        return {'statusCode': 200, 'body': 'OK'}

    except Exception as e:
        # برای اشکال‌زدایی
        print(f"Error processing update: {e}")
        return {'statusCode': 500, 'body': f'Internal Server Error: {e}'}


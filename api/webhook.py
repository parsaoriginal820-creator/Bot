# api/webhook.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import json

# --- Configuration ---
# کلیدها از Vercel خوانده می‌شوند
# اصلاح: در اینجا باید نام متغیر (Key) را از Vercel بخوانید، نه مقدار آن را.
TMDB_API_KEY = os.environ.get("TMDB_API_KEY") 

# دیتابیس داخلی لینک‌ها
DOWNLOAD_LINKS = {
    "Solar Opposites": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Series/Pluribus/S01/Pluribus.S01E01.1080p.Dubbed.Film2Movie.mp4?type=dl", 
    "Disenchantment": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Series/Pluribus/S01/Pluribus.S01E01.1080p.Dubbed.Film2Movie.mp4?type=dl",
}

SEARCH_URL = "https://api.themoviedb.org/3/search/multi" 
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('سلام! اسم فیلم یا سریال مورد نظرت رو برای من بفرست.')

async def search_movie_or_tv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if not TMDB_API_KEY:
        # اگر توکن TMDB پیدا نشد (برای عیب‌یابی)
        await update.message.reply_text("خطا: کلید TMDB API تنظیم نشده یا در Vercel پیدا نشد.")
        return

    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'fa-IR'}
    response = requests.get(SEARCH_URL, params=params)
    data = response.json()

    if data['results']:
        item = data['results'][0]

        # استخراج و ساخت کپشن
        title = item.get('name') if item.get('media_type') == 'tv' else item.get('title')
        overview = item.get('overview', 'توضیحات در دسترس نیست.')
        caption = f"🎬 **نام:** {title}\n\n📝 **خلاصه داستان:** {overview}"

        # منطق دکمه دانلود
        keyboard = []
        if title in DOWNLOAD_LINKS:
            link = DOWNLOAD_LINKS[title]
            button = InlineKeyboardButton(f"⬇️ دریافت لینک دانلود {title}", url=link)
            keyboard.append([button])
        else:
            keyboard.append([InlineKeyboardButton("❌ لینک دانلود موجود نیست", callback_data='no_link')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # ارسال پوستر
        poster_path = item.get('poster_path')
        poster_url = IMAGE_BASE_URL + poster_path if poster_path else None

        if poster_url:
            await update.message.reply_photo(photo=poster_url, caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(caption, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"محتوایی با عنوان '{query}' پیدا نشد.")


# 🚀 تابع اصلی Webhook
async def handler(request):
    if request.method != 'POST':
        return {'statusCode': 200, 'body': 'GET request received. Use Telegram!'}

    # BOT_TOKEN توسط os.environ.get("BOT_TOKEN") در اینجا استفاده می‌شود
    BOT_TOKEN = os.environ.get("BOT_TOKEN") 
    if not BOT_TOKEN:
        return {'statusCode': 500, 'body': 'BOT_TOKEN not set in Environment Variables'}

    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie_or_tv))

        # پردازش به‌روزرسانی
        body = await request.json()
        update = Update.de_json(body, application.bot)
        await application.process_update(update)

        return {'statusCode': 200, 'body': 'OK'}
    except Exception as e:
        # برای مشاهده دقیق خطا در لاگ‌های Vercel
        return {'statusCode': 500, 'body': f'Internal Server Error: {e}'}

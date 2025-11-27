# api/webhook.py
# این فایل نقطه ورودی (Webhook) برای سرور Vercel است.
# تمام کتابخانه‌های مورد نیاز را وارد کنید.
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import json

# --- Configuration (تنظیمات) ---

# کلید TMDB API از متغیرهای محیطی Vercel خوانده می‌شود.
# اگر این کلید در Vercel تنظیم نشده باشد، مقدار آن None خواهد بود.
TMDB_API_KEY = os.environ.get("TMDB_API_KEY") 

# دیتابیس داخلی لینک‌های دانلود (می‌توانید اینجا لینک‌های خود را اضافه کنید)
DOWNLOAD_LINKS = {
    "Solar Opposites": "https://link-dl.example.com/solar-opposites", 
    "Disenchantment": "https://link-dl.example.com/disenchantment",
    # برای افزودن لینک‌های بیشتر، به این صورت عمل کنید:
    # "نام کامل فیلم یا سریال": "لینک دانلود آن",
}

SEARCH_URL = "https://api.themoviedb.org/3/search/multi" 
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# --- Handlers (توابع پاسخ‌دهنده) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به فرمان /start."""
    await update.message.reply_text('سلام! 🎬 به ربات جستجوی فیلم و سریال خوش آمدید.\n\nاسم فیلم یا سریال مورد نظرت رو برای من بفرست تا پوستر و اطلاعاتش رو برات پیدا کنم.')

async def search_movie_or_tv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی فیلم/سریال در TMDB و ارسال اطلاعات."""
    query = update.message.text.strip()
    
    # 1. بررسی عدم تنظیم کلید TMDB در Vercel
    if not TMDB_API_KEY:
        await update.message.reply_text("❌ خطا: کلید TMDB API در سرور تنظیم نشده است.")
        return

    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': 'fa-IR'}
    
    data = None
    
    # 2. مدیریت خطاهای ارتباطی و API
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        # اگر کد وضعیت 4xx (مثلاً 401 Unauthorized) یا 5xx بود، خطا را پرتاب کن
        response.raise_for_status() 
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB Request Error: {e}")
        await update.message.reply_text("⚠️ خطا در برقراری ارتباط با دیتابیس فیلم‌ها (TMDB). لطفا اتصال اینترنت سرور را بررسی کنید.")
        return
    except json.JSONDecodeError:
        print("TMDB returned non-JSON response, likely due to invalid API key or server issue.")
        await update.message.reply_text("❌ خطا: پاسخ غیرمنتظره از TMDB. لطفا مطمئن شوید که کلید TMDB API در Vercel به درستی وارد شده است.")
        return
    
    # 3. بررسی پیام خطای احتمالی از سمت TMDB (مثلاً کلید نامعتبر)
    if data and 'status_message' in data and data.get('status_code') != 1:
        error_message = data.get('status_message', 'کلید API نامعتبر است.')
        print(f"TMDB API Error: {error_message}")
        await update.message.reply_text(f"❌ خطا در TMDB: کلید API نامعتبر است. لطفا مقدار TMDB_API_KEY را در Vercel چک کنید.")
        return

    # 4. بررسی نتایج جستجو
    if data and 'results' in data and data['results']:
        item = data['results'][0]

        # استخراج و ساخت کپشن
        title = item.get('name') if item.get('media_type') == 'tv' else item.get('title')
        overview = item.get('overview', 'توضیحات در دسترس نیست.')
        caption = f"🎬 **نام:** {title}\n\n📝 **خلاصه داستان:** {overview}"

        # منطق دکمه دانلود
        keyboard = []
        if title and title in DOWNLOAD_LINKS:
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
        # اگر جستجو نتیجه‌ای نداشت
        await update.message.reply_text(f"محتوایی با عنوان '{query}' پیدا نشد. لطفا املای نام را بررسی کنید.")


# 🚀 تابع اصلی Webhook (این تابع توسط Vercel فراخوانی می‌شود)
async def handler(request):
    """نقطه ورود Webhook برای دریافت به‌روزرسانی‌های تلگرام."""
    if request.method != 'POST':
        return {'statusCode': 200, 'body': 'GET request received. Use Telegram!'}

    # BOT_TOKEN را از متغیرهای محیطی Vercel دریافت کنید
    BOT_TOKEN = os.environ.get("BOT_TOKEN") 
    if not BOT_TOKEN:
        # اگر توکن اصلی ربات تنظیم نشده باشد، با کد 500 پاسخ می‌دهد
        return {'statusCode': 500, 'body': 'BOT_TOKEN is not set in Environment Variables'}

    try:
        # ساختاردهی و افزودن Handlerها
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie_or_tv))

        # پردازش به‌روزرسانی
        body = await request.json()
        update = Update.de_json(body, application.bot)
        await application.process_update(update)

        # پاسخ موفقیت آمیز به تلگرام
        return {'statusCode': 200, 'body': 'OK'}
    except Exception as e:
        # ثبت خطای کلی برای مشاهده در لاگ‌های Vercel
        print(f"Fatal Internal Server Error: {e}")
        return {'statusCode': 500, 'body': f'Internal Server Error: {e}'}

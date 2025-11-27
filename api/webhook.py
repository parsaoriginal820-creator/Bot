# api/webhook.py
# این کد فقط برای تست اتصال تلگرام به Vercel استفاده می‌شود.
# اگر این کد کار کند، یعنی همه تنظیمات اصلی درست است.

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به فرمان /start."""
    # اگر ربات پاسخ داد، یعنی اتصال Vercel به تلگرام کاملاً درست است.
    await update.message.reply_text('✅ ربات فعال است! این یک پیام تستی است.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """به هر پیام متنی، با یک پیام تستی پاسخ می‌دهد."""
    text = update.message.text
    # اگر ربات پاسخ داد، یعنی پیام‌های شما به Vercel می‌رسند.
    await update.message.reply_text(f'پیام شما دریافت شد: "{text}"')


# 🚀 تابع اصلی Webhook (نقطه ورود Vercel)
async def handler(request):
    """پردازش به‌روزرسانی‌های دریافتی از تلگرام."""
    if request.method != 'POST':
        # پاسخ به درخواست‌های GET (مانند باز کردن لینک در مرورگر)
        return {'statusCode': 200, 'body': 'Webhook is active and listening for POST requests.'}

    # BOT_TOKEN را از متغیرهای محیطی Vercel دریافت کنید
    BOT_TOKEN = os.environ.get("BOT_TOKEN") 
    if not BOT_TOKEN:
        # اگر توکن اصلی ربات تنظیم نشده باشد، با کد 500 پاسخ می‌دهد
        return {'statusCode': 500, 'body': 'BOT_TOKEN is not set in Environment Variables'}

    try:
        # ساختاردهی و افزودن Handlerها
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

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

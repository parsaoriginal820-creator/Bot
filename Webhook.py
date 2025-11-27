# content of api/webhook.py

from telegram import Update
from telegram.ext import Dispatcher, MessageHandler, filters, Application
import os
import json

# --- Configuration (از Environment Variables استفاده کنید) ---
# در Vercel، توکن را مستقیماً در کد قرار نمی‌دهیم!

# 🔑 لینک‌های دانلود (فعلاً اینجا می‌مانند)
DOWNLOAD_LINKS = {
    "اینسپشن": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Movies/2025/One.Battle.After.Another.2025/One.Battle.After.Another.2025.1080p.HardSub.Film2Movie.mp4?type=dl", 
    "شوالیه تاریکی": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Movies/2025/One.Battle.After.Another.2025/One.Battle.After.Another.2025.1080p.HardSub.Film2Movie.mp4?type=dl",
}

# 🛠️ تابع اصلی پردازش دانلود
async def search_download_link(update: Update, context):
    query = update.message.text.strip()
    
    # ... (منطق جستجو و ساخت دکمه‌ها عیناً حفظ می‌شود) ...

    # به دلیل محدودیت‌های Vercel، ما منطق کامل دانلود را به همین شکل ساده حفظ می‌کنیم.
    if query in DOWNLOAD_LINKS:
        link = DOWNLOAD_LINKS[query]
        # ... (ساخت دکمه‌ها و ارسال پیام) ...
        await update.message.reply_text(
            f"✅ لینک دانلود فیلم '{query}' پیدا شد. از طریق دکمه زیر اقدام کنید:",
            # ... (reply_markup را اینجا قرار دهید)
        )
    else:
        await update.message.reply_text(
            f"❌ متأسفانه فیلمی با عنوان '{query}' در دیتابیس من موجود نیست."
        )


# 🚀 تابع اصلی Webhook (که Vercel آن را فراخوانی می‌کند)
async def webhook(event, context):
    if event.get('httpMethod') == 'POST':
        # دریافت توکن از متغیرهای محیطی Vercel
        BOT_TOKEN = os.environ.get("8225313384:AAEmLwvlz_SJ9BrfLlqaJ0xoPHu4dc3NuJ4) 
        if not BOT_TOKEN:
            return {'statusCode': 500, 'body': '8225313384:AAEmLwvlz_SJ9BrfLlqaJ0xoPHu4dc3NuJ4 not set'}
            
        # ساخت یک شیء Application با توکن
        application = Application.builder().token(BOT_TOKEN).build()
        
        # افزودن هندلرها
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_download_link))
        
        # پردازش به‌روزرسانی (Update) که از تلگرام آمده است
        body = json.loads(event.get('body'))
        update = Update.de_json(body, application.bot)
        
        # پردازش به‌روزرسانی توسط Dispatcher
        await application.process_update(update)
        
        return {'statusCode': 200, 'body': 'OK'}
    
    return {'statusCode': 200, 'body': 'GET request received. Go to Telegram!'}

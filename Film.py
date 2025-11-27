from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
BOT_TOKEN = "8225313384:AAEmLwvlz_SJ9BrfLlqaJ0xoPHu4dc3NuJ4"

DOWNLOAD_LINKS = {
    "اینسپشن": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Movies/2025/One.Battle.After.Another.2025/One.Battle.After.Another.2025.1080p.HardSub.Film2Movie.mp4?type=dl", 
    "شوالیه تاریکی": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Movies/2025/One.Battle.After.Another.2025/One.Battle.After.Another.2025.1080p.HardSub.Film2Movie.mp4?type=dl",
    "بین ستاره ای": "https://cdn.ftk.pw/dl18/user/mehdi/sd/Movies/2025/One.Battle.After.Another.2025/One.Battle.After.Another.2025.1080p.HardSub.Film2Movie.mp4?type=dl",
}

# --- Bot Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'سلام! اسم فیلم یا سریال مورد نظرت رو دقیقاً برام بفرست تا لینک دانلودش رو بهت بدم.'
    )

async def search_download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    keyboard = []
    
    if query in DOWNLOAD_LINKS:
        link = DOWNLOAD_LINKS[query]
        
        button = InlineKeyboardButton(f"⬇️ دانلود فیلم {query}", url=link)
        keyboard.append([button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ لینک دانلود فیلم '{query}' پیدا شد. از طریق دکمه زیر اقدام کنید:",
            reply_markup=reply_markup
        )
    
    else:
        await update.message.reply_text(
            f"❌ متأسفانه فیلمی با عنوان '{query}' در دیتابیس من موجود نیست. لطفاً نام را دقیقاً وارد کنید."
        )


# --- Main Function to Run the Bot ---

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_download_link))
    
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

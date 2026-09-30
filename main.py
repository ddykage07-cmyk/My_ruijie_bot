import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 မင်္ဂလာပါ! Ruijie Voucher စကင်န်ဖတ်မည့် ကိုယ်ပိုင် Bot အသင့်ဖြစ်ပါပြီ။ Portal URL ကို ပို့ပေးပါ။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" in url:
        await update.message.reply_text("🔍 Portal URL ကို လက်ခံရရှိပါပြီ။ စစ်ဆေးနေပါပြီ...")
    else:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ မှန်ကန်သော HTTP လိပ်စာ (URL) ကို ပို့ပေးပါ။")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN ကို Replit Secrets ထဲတွင် ထည့်သွင်းပေးပါ။")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 ကိုယ်ပိုင် Telegram Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
  

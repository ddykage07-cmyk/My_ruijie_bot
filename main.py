import os
import logging
import asyncio
import aiohttp
import ddddocr
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ddddocr for captcha solving
ocr = ddddocr.DdddOcr(show_ad=False)

# Dictionary to track scanning state per user/chat
scanning_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 မင်္ဂလာပါ! Ruijie Voucher စကင်န်ဖတ်မည့် ကိုယ်ပိုင် Bot အသင့်ဖြစ်ပါပြီ။\n\n"
        "🔗 ပထမဦးစွာ Ruijie Portal URL ကို ပို့ပေးပါ။"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if "http" in text:
        context.user_data['portal_url'] = text
        await update.message.reply_text(
            f"✅ Portal URL ကို အောင်မြင်စွာ မှတ်သားပြီးပါပြီ:\n`{text}`\n\n"
            "🚀 စကင်န်ဖတ်ခြင်း စတင်ရန် `/scan` ဟု ရိုက်ပါ၊ ရပ်တန့်ရန် `/stop` ဟု ရိုက်ပါ။",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ မှန်ကန်သော HTTP လိပ်စာ (URL) ကို ပို့ပေးပါ။")

async def run_scanner(update: Update, context: ContextTypes.DEFAULT_TYPE, portal_url: str):
    chat_id = update.effective_chat.id
    scanning_states[chat_id] = True
    
    status_message = await update.message.reply_text("⚡ **Ruijie Live Scanner စတင်နေပါပြီ...**", parse_mode="Markdown")
    
    tried = 0
    hits = 0
    
    async with aiohttp.ClientSession() as session:
        while scanning_states.get(chat_id, False):
            tried += 1
            # ဥပမာ ကုဒ်ထုတ်လုပ်ပုံ (လိုအပ်သလို ပြင်ဆင်နိုင်သည်)
            test_code = f"{tried:08d}" 
            
            try:
                # ဤနေရာတွင် Ruijie Portal သို့ Request ပို့မည့် ပုံစံ (POST/GET) ကို ထည့်သွင်းရပါမည်
                # ဥပမာ Captcha လိုအပ်ပါက:
                # async with session.get(f"{portal_url}/captcha") as resp:
                #     captcha_bytes = await resp.read()
                #     code_text = ocr.classification(captcha_bytes)
                
                async with session.get(portal_url, timeout=5) as response:
                    status_code = response.status
            except Exception as e:
                status_code = "Error"

            # Telegram message ကို Live Update လုပ်ခြင်း (Rate limit ထိန်းရန် ၅ ကြိမ်လျှင် တစ်ကြိမ် ပို့ပါမည်)
            if tried % 5 == 0 or tried == 1:
                live_text = (
                    "⚡ **Ruijie Scanner Running (Live Request)** ⚡\n"
                    f"🔗 Portal: Connected ({status_code})\n\n"
                    f"🏹 Tried: {tried}\n"
                    f"🎯 Current Code: {test_code}\n"
                    f"🔥 Hits: {hits}\n"
                    "❌ Expired: 0\n"
                    "⚠️ Limits: 0\n"
                    "⚡ Speed: 120.0 c/m\n\n"
                    "🔥 **Hit Codes:**\n"
                    "None yet"
                )
                try:
                    await status_message.edit_text(live_text, parse_mode="Markdown")
                except Exception:
                    pass
            
            # Request အကြား အမြန်နှုန်း ထိန်းရန် ခဏစောင့်ခြင်း
            await asyncio.sleep(1)
            
            if not scanning_states.get(chat_id, False):
                break

    await update.message.reply_text("🛑 စကင်န်ဖတ်ခြင်း ရပ်တန့်သွားပါပြီ။")

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    portal_url = context.user_data.get('portal_url')
    if not portal_url:
        await update.message.reply_text("⚠️ ကျေးဇူးပြု၍ ပထမဦးစွာ Portal URL ကို အရင်ပို့ပေးပါ။")
        return
    
    chat_id = update.effective_chat.id
    if scanning_states.get(chat_id, False):
        await update.message.reply_text("⚠️ စကင်န်ဖတ်ခြင်း လုပ်ငန်းစဉ် လက်ရှိ လုပ်ဆောင်ဆဲ ဖြစ်ပါသည်။")
        return

    # Background task အနေဖြင့် စကင်န်ဖတ်ခြင်းကို စတင်ခြင်း
    asyncio.create_task(run_scanner(update, context, portal_url))

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if scanning_states.get(chat_id, False):
        scanning_states[chat_id] = False
        await update.message.reply_text("🛑 စကင်န်ဖတ်ခြင်းကို ရပ်တန့်နေပါပြီ...")
    else:
        await update.message.reply_text("ℹ️ လက်ရှိ အလုပ်လုပ်နေသော စကင်န် မရှိပါ။")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN ကို Replit Secrets ထဲတွင် ထည့်သွင်းပေးပါ။")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 ကိုယ်ပိုင် Telegram Bot စတင် အလုပ်လုပ်နေပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
              

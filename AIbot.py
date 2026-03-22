import telebot
import pandas as pd
from binance.um_futures import UMFutures
import time
from telebot import types
import threading

# --- ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ ---
client = UMFutures()
TOKEN = '8669488027:AAEYEtae_rN5VM8VmKhz-v7fROruS0zPBuo'
bot = telebot.TeleBot(TOKEN)

COIN_LIST = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'TRXUSDT', 'LTCUSDT', 'LINKUSDT']

# --- ՏԵՔՍՏԵՐ (ՔՈ ՍՔՐԻՆՇՈԹՆԵՐԻՑ) ---
strings = {
    "am": {
        "select_lang": "🌐 Ընտրեք լեզուն:",
        "select_coin": "💰 Ընտրեք մետաղադրամը ցանկից.",
        "welcome": "✅ Ընտրված է: Անալիզը սկսված է:\n🌚 {coin}\n\n👋 Օգտագործեք /help բոլոր հրամանների համար:",
        "help_msg": "📜 Հրամանների ցանկ\n\n/start - Լեզվի ընտրություն\n/help - Հրամանների ցանկ\n\n🛑 Գործարքների կարգավորումներ\n/trading - Ազդանշաններ (Buy/Sell)\n/stoptrading - Անջատել ազդանշանները\n\n🔔 Տեղեկության կարգավորումներ\n/about - Գնի հիշեցում\n/changeabout - Փոխել տեղեկությունը\n/stopabout - Անջատել գնի հիշեցումը\n\n🌚 Մետաղադրամի կարգավորումներ\n/changecoin - Փոխել կրիպտոն\n/multicoin - Ավելացնել նորը",
        "about_ask": "⏰ Քանի՞ րոպեն մեկ ցույց տամ գինը: (Գրեք միայն թիվը)",
        "about_set": "✅ Պահպանվեց:"
    },
    "ru": {
        "select_lang": "🌐 Выберите язык:",
        "select_coin": "💰 Выберите монету из списка.",
        "welcome": "✅ Выбрано: Анализ запущен:\n🌚 {coin}\n\n👋 Используйте /help для всех команд:",
        "help_msg": "📜 Список команд\n\n/start - Выбор языка\n/help - Список команд\n\n🛑 Настройки сделок\n/trading - Сигналы (Buy/Sell)\n/stoptrading - Выключить сигналы\n\n🔔 Настройки информации\n/about - Напоминание цены\n/changeabout - Изменить интервал\n/stopabout - Выключить напоминание\n\n🌚 Настройки монеты\n/changecoin - Изменить монету\n/multicoin - Добавить новую",
        "about_ask": "⏰ Через сколько минут присылать цену?",
        "about_set": "✅ Сохранено:"
    },
    "en": {
        "select_lang": "🌐 Select language:",
        "select_coin": "💰 Select a coin from the list.",
        "welcome": "✅ Selected: Analysis started:\n🌚 {coin}\n\n👋 Use /help for all commands:",
        "help_msg": "📜 Commands List\n\n/start - Language selection\n/help - Commands list\n\n🛑 Trade Settings\n/trading - Signals (Buy/Sell)\n/stoptrading - Disable signals\n\n🔔 Info Settings\n/about - Price Alert\n/changeabout - Change interval\n/stopabout - Disable price alert\n\n🌚 Coin Settings\n/changecoin - Change coin\n/multicoin - Add new",
        "about_ask": "⏰ Every how many minutes show price?",
        "about_set": "✅ Saved:"
    }
}

users = {}
last_triggered_zones = {}

# --- BINANCE DATA ---
def get_live_data(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, '30m', limit=50))
        resp = resp.iloc[:, :6].astype(float)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        return resp
    except: return None

# --- ՀՐԱՄԱՆՆԵՐ ---
@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    users[cid] = {"lang": "am", "coins": [], "trading": True, "alert_min": 0, "last_alert": 0, "waiting_about": False}
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data='lang_am'),
           types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
           types.InlineKeyboardButton("🇺🇸 English", callback_data='lang_en'))
    bot.send_message(cid, strings["am"]["select_lang"], reply_markup=kb)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    cid = message.chat.id
    lang = users.get(cid, {"lang":"am"})["lang"]
    bot.send_message(cid, strings[lang]["help_msg"])

@bot.message_handler(commands=['about', 'changeabout'])
def about_cmd(message):
    cid = message.chat.id
    if cid in users:
        users[cid]["waiting_about"] = True
        bot.send_message(cid, strings[users[cid]["lang"]]["about_ask"])

@bot.message_handler(commands=['stopabout'])
def stop_about(message):
    cid = message.chat.id
    if cid in users:
        users[cid]["alert_min"] = 0
        bot.send_message(cid, "🔕 Alert OFF")

# --- ՏԵՔՍՏԻ ՄՇԱԿՈՒՄ (About-ի համար) ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    cid = message.chat.id
    if cid in users and users[cid].get("waiting_about"):
        try:
            minutes = int(message.text)
            users[cid]["alert_min"] = minutes
            users[cid]["waiting_about"] = False
            lang = users[cid]["lang"]
            bot.send_message(cid, f"{strings[lang]['about_set']} {minutes} min.")
        except:
            bot.send_message(cid, "🔢 Numbers only:")

# --- CALLBACKS ---
@bot.callback_query_handler(func=lambda call: True)
def cb_handler(call):
    cid = call.message.chat.id
    if call.data.startswith('lang_'):
        lang = call.data.split('_')[1]
        users[cid]["lang"] = lang
        kb = types.InlineKeyboardMarkup()
        for c in COIN_LIST:
            kb.add(types.InlineKeyboardButton(c.replace("USDT",""), callback_data=f"coin_{c}"))
        bot.edit_message_text(strings[lang]["select_coin"], cid, call.message.message_id, reply_markup=kb)
    
    elif call.data.startswith('coin_'):
        coin = call.data.split('_')[1]
        if cid not in users: users[cid] = {"lang": "am", "coins": [], "trading": True, "alert_min": 0, "last_alert": 0}
        users[cid]["coins"] = [coin]
        lang = users[cid]["lang"]
        bot.send_message(cid, strings[lang]["welcome"].format(coin=coin))

# --- ԱՆԱԼԻԶ ---
def analysis_loop():
    while True:
        try:
            now = time.time()
            for cid, data in list(users.items()):
                if not data["coins"]: continue
                for symbol in data["coins"]:
                    df = get_live_data(symbol)
                    if df is None: continue
                    curr_p = df['Close'].iloc[-1]

                    if data["alert_min"] > 0:
                        if now - data["last_alert"] >= data["alert_min"] * 60:
                            bot.send_message(cid, f"🔔 {symbol} Price: {curr_p}$")
                            users[cid]["last_alert"] = now
                    
                    if data["trading"]:
                        m1_h, m1_l = df['High'].iloc[-3], df['Low'].iloc[-3]
                        m2_c = df['Close'].iloc[-2]
                        m3_h, m3_l = df['High'].iloc[-1], df['Low'].iloc[-1]
                        zone_id = f"{cid}_{symbol}_{df['Time'].iloc[-2]}"

                        if m3_l > m1_h and m2_c > m1_h:
                            if last_triggered_zones.get(zone_id + "b") != True:
                                bot.send_message(cid, f"🚀 **BUY SIGNAL**: {symbol}\nPrice: {curr_p}$", parse_mode='Markdown')
                                last_triggered_zones[zone_id + "b"] = True
                        elif m3_h < m1_l and m2_c < m1_l:
                            if last_triggered_zones.get(zone_id + "s") != True:
                                bot.send_message(cid, f"⚠️ **SELL SIGNAL**: {symbol}\nPrice: {curr_p}$", parse_mode='Markdown')
                                last_triggered_zones[zone_id + "s"] = True
            time.sleep(20)
        except: time.sleep(10)

threading.Thread(target=analysis_loop, daemon=True).start()
bot.infinity_polling()

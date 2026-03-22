import telebot
import pandas as pd
from binance.um_futures import UMFutures
import time
from telebot import types
import threading

# 1. ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ
client = UMFutures()
TOKEN = '8166948827:AAEYEtAe_rh5VM8VeKhz-v7FR0ruS8zPBuo'
bot = telebot.TeleBot(TOKEN)

COIN_LIST = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'TRXUSDT', 'LTCUSDT', 'LINKUSDT']

strings = {
    "am": {
        "select_lang": "🌐 Ընտրեք լեզուն / Выберите язык / Select language:",
        "select_coin": "💰 Ընտրեք մետաղադրամը ցանկից.",
        "welcome": "✅ Ընտրված է: Անալիզը սկսված է: \n🪙 ",
        "help_hint": "\n\n👋 **Օգտագործեք /help բոլոր հրամանների համար:**",
        "help_msg": "📜 **Հրամանների ցանկ**\n\n/start - Լեզվի ընտրություն\n/help - Հրամանների ցանկ\n\n**🛑 Գործարքների կարգավորումներ**\n/trading - Ազդանշաններ (Buy/Sell)\n/stoptrading - Անջատել ազդանշանները\n\n**🔔 Տեղեկության կարգավորումներ**\n/about - Գնի հիշեցում\n/changeabout - Փոխել տեղեկությունը\n/stopabout - Անջատել ազդանշանները\n\n**🪙 Մետաղադրամի կարգավորումներ**\n/changecoin - Փոխել կրիպտոն\n/multicoin - Ավելացնել նորը",
        "about_ask": "⏰ Որքա՞ն հաճախ ցույց տամ գինը?",
        "custom_time": "⌨️ Գրեք րոպեների քանակը (օրինակ՝ 15):",
        "about_set": "✅ Կարգավորումը պահպանվեց:",
        "stop_about": "🔔 Գնի հիշեցումը անջատվեց:",
        "price_msg": "🔔 {} Price: {}$",
        "added_multi": "✅ Ավելացվեց Multi-coin ցանկին: ",
        "trade_group": "**🛑 Գործարքների կարգավորումներ**\n\n",
        "about_group": "**🔔 Տեղեկության կարգավորումներ**\n\n",
        "coin_group": "**🪙 Մետաղադրամի կարգավորումներ**\n\n",
        "trading_on": "Ազդանշանները միացված են:",
        "trading_off": "Ազդանշանները անջատված են:"
    },
    "ru": {
        "select_lang": "🌐 Выберите язык:",
        "select_coin": "💰 Выберите монету из списка.",
        "welcome": "✅ Выбрано: Анализ запущен: \n🪙 ",
        "help_hint": "\n\n👋 **Используйте /help для просмотра всех команд.**",
        "help_msg": "📜 **Список команд**\n\n/start - Выбор языка\n/help - Список команд\n\n**🛑 Настройки торговли**\n/trading - Сигналы (Buy/Sell)\n/stoptrading - Выключить сигналы\n\n**🔔 Настройки инфо**\n/about - Напоминание цены\n/changeabout - Изменить инфо\n/stopabout - Выключить напоминание\n\n**🪙 Настройки монет**\n/changecoin - Изменить монету\n/multicoin - Добавить новую",
        "about_ask": "⏰ Как часто показывать цену?",
        "custom_time": "⌨️ Введите количество минут:",
        "about_set": "✅ Настройка сохранена!",
        "stop_about": "🔔 Напоминание цены выключено.",
        "price_msg": "🔔 {} Цена: {}$",
        "added_multi": "✅ Добавлено в Multi-coin: ",
        "trade_group": "**🛑 Настройки торговли**\n\n",
        "about_group": "**🔔 Настройки инфо**\n\n",
        "coin_group": "**🪙 Настройки монет**\n\n",
        "trading_on": "Сигналы включены:",
        "trading_off": "Сигналы выключены:"
    },
    "en": {
        "select_lang": "🌐 Select language:",
        "select_coin": "💰 Select a coin from the list.",
        "welcome": "✅ Selected: Analysis started: \n🪙 ",
        "help_hint": "\n\n👋 **Use /help to see all commands.**",
        "help_msg": "📜 **Commands list**\n\n/start - Language selection\n/help - Commands list\n\n**🛑 Trading settings**\n/trading - Signals (Buy/Sell)\n/stoptrading - Disable signals\n\n**🔔 About settings**\n/about - Price alert\n/changeabout - Change info\n/stopabout - Disable alert\n\n**🪙 Coin settings**\n/changecoin - Change coin\n/multicoin - Add new coin",
        "about_ask": "⏰ How often should I show the price?",
        "custom_time": "⌨️ Enter minutes:",
        "about_set": "✅ Settings saved!",
        "stop_about": "🔔 Price alert disabled.",
        "price_msg": "🔔 {} Price: {}$",
        "added_multi": "✅ Added to Multi-coin: ",
        "trade_group": "**🛑 Trading settings**\n\n",
        "about_group": "**🔔 About settings**\n\n",
        "coin_group": "**🪙 Coin settings**\n\n",
        "trading_on": "Signals enabled:",
        "trading_off": "Signals disabled:"
    }
}

users = {}
last_triggered_zones = {}

def get_live_data(symbol):
    try:
        resp = pd.DataFrame(client.klines(symbol, '30m', limit=100))
        resp = resp.iloc[:, :6].astype(float)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        return resp
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    users[cid] = {"lang": "am", "coins": [], "trading": True, "alert_min": 0, "last_alert": 0, "waiting_min": False}
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data='am'),
           types.InlineKeyboardButton("🇷🇺 Русский", callback_data='ru'),
           types.InlineKeyboardButton("🇺🇸 English", callback_data='en'))
    bot.send_message(cid, strings["am"]["select_lang"], reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data in ['am', 'ru', 'en'])
def set_lang(call):
    cid = call.message.chat.id
    users[cid]["lang"] = call.data
    kb = types.InlineKeyboardMarkup()
    for c in COIN_LIST:
        kb.add(types.InlineKeyboardButton(c.replace("USDT", ""), callback_data=f"first_{c}"))
    bot.edit_message_text(strings[call.data]["select_coin"], cid, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith('first_'))
def set_first_coin(call):
    cid = call.message.chat.id
    coin = call.data.replace("first_", "")
    users[cid]["coins"] = [coin]
    lang = users[cid]["lang"]
    bot.send_message(cid, f"{strings[lang]['welcome']}{coin}{strings[lang]['help_hint']}", parse_mode='Markdown')

# Անալիզի ֆունկցիա (Աշխատում է հետին պլանում)
def run_analysis():
    while True:
        try:
            now = time.time()
            for cid, ud in list(users.items()):
                if ud["trading"] and ud.get("coins"):
                    for sym in ud["coins"]:
                        df = get_live_data(sym)
                        if df is not None and len(df) > 5:
                            curr_p = df['Close'].iloc[-1]
                            m1_h, m1_l = df['High'].iloc[-3], df['Low'].iloc[-3]
                            m2_c = df['Close'].iloc[-2]
                            m3_h, m3_l = df['High'].iloc[-1], df['Low'].iloc[-1]
                            z_id = f"{cid}_{sym}_{df['Time'].iloc[-2]}"

                            if m3_l > m1_h and m2_c > m1_h:
                                if last_triggered_zones.get(z_id + "_b") != True:
                                    bot.send_message(cid, f"🚀 **Buy Signal**: {sym}\nPrice: {curr_p}$", parse_mode='Markdown')
                                    last_triggered_zones[z_id + "_b"] = True
                            elif m3_h < m1_l and m2_c < m1_l:
                                if last_triggered_zones.get(z_id + "_s") != True:
                                    bot.send_message(cid, f"⚠️ **Sell Signal**: {sym}\nPrice: {curr_p}$", parse_mode='Markdown')
                                    last_triggered_zones[z_id + "_s"] = True
            time.sleep(15)
        except Exception as e:
            print(f"Analysis error: {e}")
            time.sleep(10)

threading.Thread(target=run_analysis, daemon=True).start()

print("Բոտը միացված է Render-ում...")
bot.infinity_polling()

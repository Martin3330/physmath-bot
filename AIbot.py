import ta
import pandas as pd
from binance.um_futures import UMFutures
import asyncio
import nest_asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import time

# 1. ԿԱՐԳԱՎՈՐՈՒՄՆԵՐ
client = UMFutures(proxies={'https': 'http://proxy.server:3128'})
TOKEN = '8669488027:AAEYEtae_rN5VM8VmKhz-v7fROruS0zPBuo'
bot = Bot(token=TOKEN)

COIN_LIST = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'TRXUSDT', 'LTCUSDT', 'LINKUSDT']

strings = {
    "am": {
        "select_lang": "🌐 Ընտրեք լեզուն / Выберите язык / Select language:",
        "select_coin": "💰 Ընտրեք մետաղադրամը ցանկից.",
        "welcome": "✅ Ընտրված է: Անալիզը սկսված է: \n🪙 ",
        "help_hint": "\n\n👋 **Օգտագործեք /help բոլոր հրամանների համար:**",
        "help_msg": "📜 **Հրամանների ցանկ**\n\n/start - Լեզվի ընտրություն\n/help - Հրամանների ցանկ\n\n**🛑 Գործարքների կարգավորումներ**\n/trading - Ազդանշաններ (Buy/Sell)\n/stoptrading - Անջատել ազդանշանները\n\n**🔔 Տեղեկության կարգավորումներ**\n/about - Գնի հիշեցում\n/changeabout - Փոխել տեղեկությունը\n/stopabout - Անջատել գնի հիշեցումը\n\n**🪙 Մետաղադրամի կարգավորումներ**\n/changecoin - Փոխել կրիպտոն\n/multicoin - Ավելացնել նորը",
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

async def main():
    nest_asyncio.apply()
    print("Բոտը ակտիվ է...")
    last_update_id = -1

    while True:
        try:
            updates = await bot.get_updates(offset=last_update_id + 1, timeout=5)

            if updates:
                for update in updates:
                    last_update_id = update.update_id
                    chat_id = update.effective_chat.id
                    if update.message:
                        text = update.message.text
                        is_callback = False
                    elif update.callback_query:
                        text = update.callback_query.data
                        is_callback = True
                    else:
                        continue
                    if chat_id not in users:
                        users[chat_id] = {"lang": "am", "coins": [], "trading": True, "alert_min": 0, "last_alert": 0, "waiting_min": False}

                    u = users[chat_id]
                    lang = u["lang"]

                    if text == "/start":
                        kb = [[InlineKeyboardButton("🇦🇲 Հայերեն", callback_data='am')], [InlineKeyboardButton("🇷🇺 Русский", callback_data='ru')], [InlineKeyboardButton("🇺🇸 English", callback_data='en')]]
                        await bot.send_message(chat_id=chat_id, text=strings["am"]["select_lang"], reply_markup=InlineKeyboardMarkup(kb))
                    elif text == "/help":
                        await bot.send_message(chat_id=chat_id, text=strings[lang]["help_msg"], parse_mode='Markdown')
                    elif text in ["am", "ru", "en"] and is_callback:
                        u["lang"] = text
                        kb = [[InlineKeyboardButton(c.replace("USDT", ""), callback_data=f"first_{c}")] for c in COIN_LIST]
                        await bot.send_message(chat_id=chat_id, text=strings[text]["select_coin"], reply_markup=InlineKeyboardMarkup(kb))
                    elif text == "/trading":
                        u["trading"] = True
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['trade_group']}{strings[lang]['trading_on']}", parse_mode='Markdown')
                    elif text == "/stoptrading":
                        u["trading"] = False
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['trade_group']}{strings[lang]['trading_off']}", parse_mode='Markdown')
                    elif text in ["/about", "/changeabout"]:
                        kb = [[InlineKeyboardButton("1 ժամ", callback_data="time_60")], [InlineKeyboardButton("1 Օր", callback_data="time_1440")], [InlineKeyboardButton("📝 Ձեր տարբերակը", callback_data="time_custom")]]
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['about_group']}{strings[lang]['about_ask']}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
                    elif text == "/stopabout":
                        u["alert_min"] = 0
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['about_group']}{strings[lang]['stop_about']}", parse_mode='Markdown')
                    elif text == "/changecoin":
                        kb = [[InlineKeyboardButton(c.replace("USDT", ""), callback_data=f"first_{c}")] for c in COIN_LIST]
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['coin_group']}{strings[lang]['select_coin']}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
                    elif text == "/multicoin":
                        kb = [[InlineKeyboardButton(c.replace("USDT", ""), callback_data=f"add_{c}")] for c in COIN_LIST]
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['coin_group']}{strings[lang]['select_coin']}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
                    elif is_callback and text.startswith("first_"):
                        coin = text.replace("first_", "")
                        u["coins"] = [coin]
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['welcome']}{coin}{strings[lang]['help_hint']}", parse_mode='Markdown')
                    elif is_callback and text.startswith("add_"):
                        coin = text.replace("add_", "")
                        if coin not in u["coins"]: u["coins"].append(coin)
                        await bot.send_message(chat_id=chat_id, text=f"{strings[lang]['coin_group']}{strings[lang]['added_multi']}{coin}", parse_mode='Markdown')
                    elif is_callback and text.startswith("time_"):
                        val = text.replace("time_", "")
                        if val == "custom":
                            u["waiting_min"] = True
                            await bot.send_message(chat_id=chat_id, text=strings[lang]["custom_time"])
                        else:
                            u["alert_min"] = int(val)
                            u["last_alert"] = time.time()
                            await bot.send_message(chat_id=chat_id, text=strings[lang]["about_set"])
                    elif u["waiting_min"] and text.isdigit():
                        u["alert_min"] = int(text)
                        u["last_alert"] = time.time()
                        u["waiting_min"] = False
                        await bot.send_message(chat_id=chat_id, text=strings[lang]["about_set"])

            # Անալիզի հատվածը կատարվում է հրամաններից հետո
            now = time.time()
            for cid, ud in users.items():
                if ud["alert_min"] > 0 and (now - ud["last_alert"]) >= (ud["alert_min"] * 60):
                    for sym in ud["coins"]:
                        df = get_live_data(sym)
                        if df is not None:
                            p = df['Close'].iloc[-1]
                            await bot.send_message(chat_id=cid, text=strings[ud["lang"]]["price_msg"].format(sym.replace("USDT",""), p))
                    ud["last_alert"] = now

                if ud["trading"] and ud["coins"]:
                    for sym in ud["coins"]:
                        df = get_live_data(sym)
                        if df is not None and len(df) > 5:
                            curr_p = df['Close'].iloc[-1]
                            for i in range(len(df) - 4, len(df) - 15, -1):
                                m1_h, m1_l = df['High'].iloc[i], df['Low'].iloc[i]
                                m3_h, m3_l = df['High'].iloc[i+2], df['Low'].iloc[i+2]
                                m2_c = df['Close'].iloc[i+1]
                                z_id = f"{cid}_{sym}_{df['Time'].iloc[i+1]}"

                                if m3_l > m1_h and m2_c > m1_h:
                                    if curr_p <= m3_l and curr_p >= m1_h:
                                        if last_triggered_zones.get(z_id + "_b") != True:
                                            await bot.send_message(chat_id=cid, text=f"🚀 **Buy Signal**: {sym}\nPrice: {curr_p}$", parse_mode='Markdown')
                                            last_triggered_zones[z_id + "_b"] = True
                                    break
                                if m3_h < m1_l and m2_c < m1_l:
                                    if curr_p >= m3_h and curr_p <= m1_l:
                                        if last_triggered_zones.get(z_id + "_s") != True:
                                            await bot.send_message(chat_id=cid, text=f"⚠️ **Sell Signal**: {sym}\nPrice: {curr_p}$", parse_mode='Markdown')
                                            last_triggered_zones[z_id + "_s"] = True
                                    break
            await asyncio.sleep(1)
        except Exception as e:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())

import telebot
from telebot import types
import google.generativeai as genai
import time

# --- ՏՎՅԱԼՆԵՐ ---
TOKEN = "8622979310:AAFBqIQCE9Yp4uy_aZ-yX1EceUBAejshbeA"
# ԱՅՍՏԵՂ ԴԻՐ ԲՈԼՈՐՈՎԻՆ ՆՈՐ API KEY
genai.configure(api_key="AIzaSyCrhORyWAIv5ngXXM8CHCyIpEtl4P9O5UU") 
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
user_lang = {}

DATA = {
    "hy": {"about": "Ես AI բոտ եմ 🤖\nԼուծում եմ մաթեմատիկայի և ֆիզիկայի խնդիրներ:\n\nԳրեք ձեր հարցը 👇", "waiting": "Մտածում եմ..."},
    "ru": {"about": "Я AI бот 🤖\nРешаю задачи по математике и физике.\n\nНапишите задачу 👇", "waiting": "Думаю..."},
    "en": {"about": "I am an AI bot 🤖\nI solve math and physics problems.\n\nSend your question 👇", "waiting": "Thinking..."}
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data="l_hy"),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data="l_ru"),
               types.InlineKeyboardButton("🇺🇸 English", callback_data="l_en"))
    bot.send_message(message.chat.id, "Ընտրեք լեզուն / Выберите язык / Choose language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("l_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.message.chat.id] = lang
    bot.edit_message_text(DATA[lang]["about"], call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    lang = user_lang.get(message.chat.id, "hy")
    sent = bot.reply_to(message, DATA[lang]["waiting"])
    try:
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, sent.message_id)
    except Exception as e:
        bot.edit_message_text(f"Error: {str(e)[:50]}", message.chat.id, sent.message_id)

if __name__ == "__main__":
    print("Bot is starting...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)

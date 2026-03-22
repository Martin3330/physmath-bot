import telebot
from telebot import types
import google.generativeai as genai
import time

# --- ԿՈՆՖԻԳՈՒՐԱՑԻԱ ---
TOKEN = "8622979310:AAFBqIQCE9Yp4uy_aZ-yX1EceUBAejshbeA"
# ԱՅՍՏԵՂ ԴԻՐ ՔՈ ԲՈԼՈՐՈՎԻՆ ՆՈՐ API KEY-Ը
genai.configure(api_key="AIzaSyCrhORyWAIv5ngXXM8CHCyIpEtl4P9O5UU") 
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TOKEN)
user_lang = {}

DATA = {
    "hy": {
        "about": "Ես AI բոտ եմ 🤖\nԼուծում եմ մաթեմատիկայի և ֆիզիկայի խնդիրներ:\n\nԳրեք ձեր հարցը 👇",
        "change_btn": "🌐 Փոխել լեզուն",
        "waiting": "Մտածում եմ..."
    },
    "ru": {
        "about": "Я AI бот 🤖\nРешаю задачи по математике и физике.\n\nНапишите задачу 👇",
        "change_btn": "🌐 Сменить язык",
        "waiting": "Думаю..."
    },
    "en": {
        "about": "I am an AI bot 🤖\nI solve math and physics problems.\n\nSend your question 👇",
        "change_btn": "🌐 Change language",
        "waiting": "Thinking..."
    }
}

# --- ԿՈՃԱԿՆԵՐ ---
def get_lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data="l_hy"),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data="l_ru"),
               types.InlineKeyboardButton("🇺🇸 English", callback_data="l_en"))
    return markup

def get_main_keyboard(lang):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(DATA[lang]["change_btn"], callback_data="change"))
    return markup

# --- ՀՐԱՄԱՆՆԵՐ ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Ընտրեք լեզուն / Выберите язык / Choose language:", reply_markup=get_lang_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("l_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.message.chat.id] = lang
    bot.answer_callback_query(call.id)
    bot.edit_message_text(DATA[lang]["about"], call.message.chat.id, call.message.message_id, reply_markup=get_main_keyboard(lang))

@bot.callback_query_handler(func=lambda call: call.data == "change")
def change_lang(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("🌐 Choose language:", call.message.chat.id, call.message.message_id, reply_markup=get_lang_keyboard())

# --- Gemini AI ՄՇԱԿՈՒՄ ---
@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    lang = user_lang.get(message.chat.id, "hy")
    sent = bot.reply_to(message, DATA[lang]["waiting"])
    try:
        # Հարցը ուղարկում ենք Gemini-ին
        response = model.generate_content(message.text)
        # Պատասխանը ուղարկում ենք օգտատիրոջը
        bot.edit_message_text(response.text, message.chat.id, sent.message_id, reply_markup=get_main_keyboard(lang))
    except Exception as e:
        # Սխալի դեպքում ցույց ենք տալիս իրական պատճառը
        bot.edit_message_text(f"Error: {str(e)[:100]}", message.chat.id, sent.message_id)

# --- ԲՈՏԻ ՄԻԱՑՈՒՄ ---
if __name__ == "__main__":
    print("Բոտը միացավ...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception:
            time.sleep(5)

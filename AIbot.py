import telebot
from telebot import types
import google.generativeai as genai
import time

# --- ՏՎՅԱԼՆԵՐ ---
TOKEN = "8622979310:AAFBqIQCE9Yp4uy_aZ-yX1EceUBAejshbeA"
API_KEY = "AIzaSyBs50J5WHeRg_ohV4zlW01is7UySBEFmHg"  # <--- ԴԻՐ ՔՈ ԲԱՆԱԼԻՆ

genai.configure(api_key=API_KEY)
# Օգտագործում ենք ամենահուսալի մոդելը
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
user_lang = {}

DATA = {
    "hy": {"about": "Ես AI բոտ եմ 🤖\nԼուծում եմ մաթեմատիկայի և ֆիզիկայի խնդիրներ:\n\nԳրեք ձեր հարցը 👇", "change": "🌐 Փոխել լեզուն", "wait": "Մտածում եմ..."},
    "ru": {"about": "Я AI бот 🤖\nРешаю задачи по математике и физике.\n\nНапишите задачу 👇", "change": "🌐 Сменить язык", "wait": "Думаю..."},
    "en": {"about": "I am an AI bot 🤖\nI solve math and physics problems.\n\nSend your question 👇", "change": "🌐 Change language", "wait": "Thinking..."}
}

def get_keyboard(lang):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(DATA[lang]["change"], callback_data="change_lang"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data="l_hy"),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data="l_ru"),
               types.InlineKeyboardButton("🇺🇸 English", callback_data="l_en"))
    bot.send_message(message.chat.id, "Choose language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("l_") or call.data == "change_lang")
def handle_callbacks(call):
    if call.data == "change_lang":
        start(call.message)
    else:
        lang = call.data.split("_")[1]
        user_lang[call.message.chat.id] = lang
        bot.edit_message_text(DATA[lang]["about"], call.message.chat.id, call.message.message_id, reply_markup=get_keyboard(lang))

@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    lang = user_lang.get(message.chat.id, "hy")
    sent = bot.reply_to(message, DATA[lang]["wait"])
    try:
        response = model.generate_content(message.text)
        # Ստուգում ենք, որ պատասխանը դատարկ չլինի
        bot.edit_message_text(response.text, message.chat.id, sent.message_id, reply_markup=get_keyboard(lang))
    except Exception as e:
        bot.edit_message_text(f"Error: {str(e)[:50]}", message.chat.id, sent.message_id)

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

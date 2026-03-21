
import telebot
import google.generativeai as genai
from telebot import types

TOKEN = '8622979310:AAGW784TF9xn1qbIRs3-FLDDJVOulsvxoPc'
genai.configure(api_key='AIzaSyB7tU2piqmRdwsGeqmbiiOfkvlN-JMfu4Q')
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
user_languages = {}

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Հայերեն 🇦🇲", callback_data="lang_am"),
                 types.InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
                 types.InlineKeyboardButton("English 🇺🇸", callback_data="lang_en"))
    bot.send_message(message.chat.id, "Ընտրեք լեզուն / Choose language:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    user_languages[call.message.chat.id] = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, "Պատրաստ եմ: Գրիր հարցդ:")

@bot.message_handler(func=lambda m: True)
def chat(message):
    lang = user_languages.get(message.chat.id, "am")
    try:
        res = model.generate_content(f"Answer in {lang}: {message.text}")
        bot.reply_to(message, res.text)
    except:
        bot.reply_to(message, "Սխալ տեղի ունեցավ:")

bot.polling(none_stop=True)

import telebot
from telebot import types
import google.generativeai as genai

# Տվյալներ
TOKEN = "8622979310:AAFBqIQCE9Yp4uy_aZ-yX1EceUBAejshbeA"
genai.configure(api_key="AIzaSyA0hISQgvVHvzfhXi-iIczxmugi9w6c3kU")
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
user_lang = {}

DATA = {
    "hy": {
        "about": "Ես AI բոտ եմ 🤖\nԿարող եմ լուծել մաթեմատիկայի և ֆիզիկայի խնդիրներ:\n\nԳրեք ձեր խնդիրը 👇",
        "change_btn": "🌐 Փոխել լեզուն",
        "waiting": "Մտածում եմ..."
    },
    "ru": {
        "about": "Я AI бот 🤖\nЯ могу решать задачи по математике и физике.\n\nНапишите свою задачу 👇",
        "change_btn": "🌐 Сменить язык",
        "waiting": "Думаю..."
    },
    "en": {
        "about": "I am an AI bot 🤖\nI can solve math and physics problems.\n\nSend your problem 👇",
        "change_btn": "🌐 Change language",
        "waiting": "Thinking..."
    }
}

def get_lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇦🇲 Հայերեն", callback_data="lang_hy"),
               types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
               types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"))
    return markup

def get_main_keyboard(lang):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(DATA[lang]["change_btn"], callback_data="change"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌐 Choose language:", reply_markup=get_lang_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_lang(call):
    lang = call.data.split("_")[1]
    user_lang[call.message.chat.id] = lang
    bot.answer_callback_query(call.id)
    bot.edit_message_text(DATA[lang]["about"], call.message.chat.id, call.message.message_id, reply_markup=get_main_keyboard(lang))

@bot.callback_query_handler(func=lambda call: call.data == "change")
def change_lang(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("🌐 Choose language:", call.message.chat.id, call.message.message_id, reply_markup=get_lang_keyboard())

@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    lang = user_lang.get(message.chat.id, "hy")
    sent = bot.reply_to(message, DATA[lang]["waiting"])
    try:
        prompt = f"User language: {lang}. Solve and explain clearly: {message.text}"
        response = model.generate_content(prompt)
        bot.edit_message_text(response.text, message.chat.id, sent.message_id, reply_markup=get_main_keyboard(lang))
    except:
        bot.edit_message_text("Error! Please try again.", message.chat.id, sent.message_id)

if __name__ == "__main__":
    bot.infinity_polling()

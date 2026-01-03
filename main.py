import telebot
from telebot import types

# التوكن الجديد
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('قسم التطبيقات 📱')
    btn2 = types.KeyboardButton('شحن الألعاب 🎮')
    btn3 = types.KeyboardButton('حسابي 👤')
    btn4 = types.KeyboardButton('الدعم الفني 🛠️')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "أهلاً بك في Game Card Store! اختر من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == 'قسم التطبيقات 📱':
        bot.send_message(message.chat.id, "✨ جاري فتح قسم التطبيقات...")
    elif message.text == 'شحن الألعاب 🎮':
        bot.send_message(message.chat.id, "🚀 جاري فتح قسم شحن الألعاب...")
    elif message.text == 'حسابي 👤':
        bot.send_message(message.chat.id, f"👤 اسمك: {message.from_user.first_name}")
    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ تواصل مع الدعم: @Support_Admin")

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)

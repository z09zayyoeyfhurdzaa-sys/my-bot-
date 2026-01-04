import telebot
from telebot import types

# توكن البوت
API_TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('قسم التطبيقات 📱', 'شحن الألعاب 🎮')
    markup.add('حسابي 👤', 'الدعم الفني 🛠️')
    bot.send_message(message.chat.id, "✨ تم التحديث! اختر من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == 'قسم التطبيقات 📱':
        bot.send_message(message.chat.id, "📱 **قائمة التطبيقات:**\n1- تطبيق X\n2- تطبيق Y")
    elif message.text == 'شحن الألعاب 🎮':
        bot.send_message(message.chat.id, "🎮 **شحن الألعاب:**\n- ببجي\n- فري فاير")
    elif message.text == 'حسابي 👤':
        bot.send_message(message.chat.id, f"👤 اسمك: {message.from_user.first_name}")
    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ الدعم: @Support_Admin")

# أهم سطرين لحل مشكلة التعليق والتكرار
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

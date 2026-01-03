import telebot
from telebot import types

# التوكن الخاص بك (الموجود في صورك السابقة)
API_TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
bot = telebot.TeleBot(API_TOKEN)

# كود زر البداية وتجهيز الأزرار الأربعة
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('قسم التطبيقات 📱')
    item2 = types.KeyboardButton('شحن الألعاب 🎮')
    item3 = types.KeyboardButton('حسابي 👤')
    item4 = types.KeyboardButton('الدعم الفني 🛠️')
    markup.add(item1, item2)
    markup.add(item3, item4)
    bot.send_message(message.chat.id, "أهلاً بك في متجرك الخاص! اختر من الأسفل:", reply_markup=markup)

# كود الرد على كل زر عند الضغط عليه
@bot.message_handler(func=lambda message: True)
def callback_worker(message):
    if message.text == 'قسم التطبيقات 📱':
        bot.send_message(message.chat.id, "🚀 جاري تجهيز قائمة التطبيقات لك...")
    elif message.text == 'شحن الألعاب 🎮':
        bot.send_message(message.chat.id, "🎮 اختر اللعبة التي تود شحنها...")
    elif message.text == 'حسابي 👤':
        bot.send_message(message.chat.id, f"👤 اسمك: {message.from_user.first_name}\n🆔 آيديك: {message.from_user.id}")
    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ تواصل مع الإدارة: @Support_Admin")

# تشغيل البوت باستمرار
bot.infinity_polling(skip_pending=True)

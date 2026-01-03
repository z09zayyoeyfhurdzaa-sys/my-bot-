import telebot
from telebot import types

# توكن البوت الخاص بك
API_TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('قسم التطبيقات 📱', 'شحن الألعاب 🎮')
    markup.add('حسابي 👤', 'الدعم الفني 🛠️')
    bot.send_message(message.chat.id, "أهلاً بك في متجرك! اختر من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == 'قسم التطبيقات 📱':
        apps_info = """
📱 **قائمة التطبيقات الخاصة بك:**
✅ تطبيق (الاسم الذي حددته)
✅ تطبيق (الاسم الذي حددته)
✅ تطبيق (الاسم الذي حددته)

💡 اطلب الآن عبر الدعم الفني.
        """
        bot.send_message(message.chat.id, apps_info)

    elif message.text == 'شحن الألعاب 🎮':
        games_info = """
🎮 **قسم شحن الألعاب:**
🔥 شحن شدات ببجي
🔥 شحن جواهر فري فاير

💡 أرسل الآيدي الخاص بك للدعم لإتمام الشحن.
        """
        bot.send_message(message.chat.id, games_info)

    elif message.text == 'حسابي 👤':
        user_info = f"👤 اسمك: {message.from_user.first_name}\n🆔 آيديك: {message.from_user.id}"
        bot.send_message(message.chat.id, user_info)

    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ تواصل مع الدعم الفني: @Support_Admin")

bot.infinity_polling(skip_pending=True)

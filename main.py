import telebot
from telebot import types

# التوكن الخاص بك
API_TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('قسم التطبيقات 📱', 'شحن الألعاب 🎮')
    markup.add('حسابي 👤', 'الدعم الفني 🛠️')
    bot.send_message(message.chat.id, "مرحباً بك في Game Card Store 💳\nاختر القسم المطلوب من القائمة:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == 'قسم التطبيقات 📱':
        # المعلومات تظهر هنا مباشرة بدون رسالة "جاري فتح"
        apps_info = "📱 **قائمة التطبيقات:**\n✅ تطبيق (1)\n✅ تطبيق (2)\n✅ تطبيق (3)\n\n💡 للطلب تواصل مع الدعم."
        bot.send_message(message.chat.id, apps_info)

    elif message.text == 'شحن الألعاب 🎮':
        games_info = "🎮 **قسم الشحن:**\n🔥 شدات ببجي\n🔥 جواهر فري فاير\n\n💡 أرسل الآيدي للدعم لإتمام العملية."
        bot.send_message(message.chat.id, games_info)

    elif message.text == 'حسابي 👤':
        bot.send_message(message.chat.id, f"👤 اسمك: {message.from_user.first_name}\n🆔 آيديك: {message.from_user.id}")

    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ تواصل مع الإدارة: @Support_Admin")

# حذف الويب هوك القديم وبدء استقبال الرسائل الجديدة فقط
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)


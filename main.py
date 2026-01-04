import telebot
from telebot import types

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
    # الردود تظهر هنا مباشرة كما طلبت
    if message.text == 'قسم التطبيقات 📱':
        bot.send_message(message.chat.id, "📱 **قائمة التطبيقات:**\n✅ تطبيق (1)\n✅ تطبيق (2)\n✅ تطبيق (3)")
    elif message.text == 'شحن الألعاب 🎮':
        bot.send_message(message.chat.id, "🎮 **قسم الشحن:**\n🔥 شدات ببجي\n🔥 جواهر فري فاير")
    elif message.text == 'حسابي 👤':
        bot.send_message(message.chat.id, f"👤 اسمك: {message.from_user.first_name}\n🆔 آيديك: `{message.from_user.id}`")
    elif message.text == 'الدعم الفني 🛠️':
        bot.send_message(message.chat.id, "🛠️ تواصل مع الإدارة: @Support_Admin")

# مسح الويب هوك وتجاهل الرسائل القديمة
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)


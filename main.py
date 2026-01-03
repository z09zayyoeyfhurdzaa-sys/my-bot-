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
    bot.send_message(message.chat.id, "أهلاً بك في Game Card Store! اختر من القائمة أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == 'قسم التطبيقات 📱':
        apps_text = """
📱 **قسم التطبيقات المتوفرة:**
✅ اشتراك شاهد VIP (شهر)
✅ اشتراك نتفليكس (شاشة واحدة)
✅ برامج بلس للايفون
✅ تفعيل ويندوز 10/11 أصلي

💡 للطلب، تواصل مع الدعم الفني.
        """
        bot.send_message(message.chat.id, apps_text)

    elif message.text == 'شحن الألعاب 🎮':
        games_text = """
🎮 **قسم شحن الألعاب:**
🔥 شحن شدات ببجي (PUBG)
🔥 شحن جواهر فري فاير (Free Fire)
🔥 شحن كول اوف ديوتي (CP)
🔥 بطاقات جوجل بلاي وآيتونز

💡 اختر اللعبة وتواصل مع الدعم للتحويل.
        """
        bot.send_message(message.chat.id, games_text)

    elif message.text == 'حسابي 👤':
        user_info = f"👤 اسمك: {message.from_user.first_name}\n🆔 آيديك: {message.from_user.id}"
        bot.send_message(message.chat.id, user_info)

    elif message.text == 'الدعم الفني 🛠️':
        support_text = "🛠️ للتواصل مع الدعم الفني والاستفسارات:\n@Support_Admin"
        bot.send_message(message.chat.id, support_text)

bot.infinity_polling(skip_pending=True)

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
    bot.send_message(message.chat.id, "مرحباً بك في Game Card Store 💳\nسعر الصرف الحالي: 1$ = 12,000 ليرة", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # سعر الصرف الحالي (سهل التعديل)
    exchange_rate = 12000

    if message.text == 'قسم التطبيقات 📱':
        apps_info = f"""
📱 **قسم التطبيقات المتوفرة:**
━━━━━━━━━━━━━
✅ اشتراك شاهد VIP
✅ اشتراك نتفليكس
✅ تطبيقات بلس
━━━━━━━━━━━━━
💰 الحساب يعتمد على سعر صرف: {exchange_rate:,} ليرة.
💡 للطلب، تواصل مع الدعم الفني.
        """
        bot.send_message(message.chat.id, apps_info)

    elif message.text == 'شحن الألعاب 🎮':
        games_info = """
🎮 **قسم شحن الألعاب:**
━━━━━━━━━━━━━
🔥 شدات ببجي (UC)
🔥 جواهر فري فاير
━━━━━━━━━━━━━
💡 أرسل الآيدي الخاص بك للدعم لإتمام الشحن.
        """
        bot.send_message(message.chat.id, games_info)

    elif message.text == 'حسابي 👤':
        user_info = f"👤 **معلومات حسابك:**\n\nالاسم: {message.from_user.first_name}\nالآيدي: `{message.from_user.id}`"
        bot.send_message(message.chat.id, user_info, parse_mode="Markdown")

    elif message.text == 'الدعم الفني 🛠️':
        support_text = f"""
🛠️ **للتواصل والتحويل المالي:**
━━━━━━━━━━━━━
📞 رقم التحويل: `62154433`
💬 تلجرام: @Support_Admin
━━━━━━━━━━━━━
💡 يمكنك إرسال إشعار التحويل عبر التلجرام مباشرة.
        """
        bot.send_message(message.chat.id, support_text, parse_mode="Markdown")

# تنظيف الرسائل القديمة وتشغيل البوت
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

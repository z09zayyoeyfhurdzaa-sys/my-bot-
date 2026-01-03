import telebot
from telebot import types

# التوكن الخاص بك
bot = telebot.TeleBot('8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # إنشاء لوحة الأزرار القديمة
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('قسم التطبيقات 📱')
    itembtn2 = types.KeyboardButton('شحن الألعاب 🎮')
    itembtn3 = types.KeyboardButton('حسابي 👤')
    itembtn4 = types.KeyboardButton('الدعم الفني 🛠️')
    
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    
    bot.reply_to(message, "أهلاً بك في Game Card Store! اختر من القائمة أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == 'قسم التطبيقات 📱':
        bot.reply_to(message, "جاري فتح قسم التطبيقات...")
    elif message.text == 'شحن الألعاب 🎮':
        bot.reply_to(message, "جاري فتح قسم شحن الألعاب...")
    else:
        bot.reply_to(message, f"لقد اخترت: {message.text}")

# بدء التشغيل
print("Starting your bot...")
bot.polling(non_stop=True)

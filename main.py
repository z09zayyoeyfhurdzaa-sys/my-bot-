import telebot
from telebot import types

# التوكن الخاص بك
bot = telebot.TeleBot('8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # إنشاء لوحة الأزرار
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('قسم التطبيقات 📱')
    btn2 = types.KeyboardButton('شحن الألعاب 🎮')
    btn3 = types.KeyboardButton('حسابي 👤')
    btn4 = types.KeyboardButton('الدعم الفني 🛠️')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, "أهلاً بك في Game Card Store! اختر من القائمة أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.

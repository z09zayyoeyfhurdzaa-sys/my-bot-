import telebot

# التوكن الجديد الذي أرسلته
bot = telebot.TeleBot('8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "تم التشغيل بنجاح على Koyeb! أنا أعمل الآن 24/7.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# بدء التشغيل
print("Starting your bot...")
bot.polling(non_stop=True)

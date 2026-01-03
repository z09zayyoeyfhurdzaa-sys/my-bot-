import telebot
TOKEN = '7611681283:AAHVfS9_wVzM5-7T795u7zL2X97C3K5G7H0'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "تم التشغيل بنجاح على Koyeb!")
bot.infinity_polling()

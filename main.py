import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  

bot = telebot.TeleBot(TOKEN)
user_balances = {} 

# --- القوائم ---
APPS_DATA = {
    "Cocco live": 1.5, "بيغو لايف": 2, "Hiya chat": 1.2, "سوجو لايف": 1,
    "Likee": 2, "Ligo live": 1.5, "4 Fun chat": 1.8, "اوهلا شات": 2.5,
    "Yoyo chat": 1.5, "Yigo chat": 1.2, "salam chat": 2, "Tada chat": 1.5,
    "HAWA CHAT": 2.2, "BINMO CHAT": 1.8, "LAYLA CHAT": 1.5, "MIGO LIVE": 2,
    "kwai": 1.2, "SUPER LIVE": 3, "Ayome chat": 1.5, "يوهو شات": 2,
    "Pota live": 1.8, "DITTO LIVE": 2.5
}

GAMES_DATA = ["شدات ببجي 🔫", "جواهر فري فاير 💎", "كول اوف ديوتي 🎖"]

@bot.message_handler(commands=['start'])
def start(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("🎮 قسم الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن رصيدي", "👤 حسابي")
    bot.send_message(message.chat.id, f"✅ تم التحديث! الصرف الحالي: {RATE:,}", reply_markup=mk)

# --- حل مشكلة "رسالة جاري الفتح" عبر عرض الأزرار مباشرة ---
@bot.message_handler(func=lambda m: m.text == "📱 قسم التطبيقات")
def apps(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(app) for app in APPS_DATA.keys()]
    mk.add(*buttons)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, "اختر التطبيق المطلوب:", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🎮 قسم الألعاب")
def games(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(game) for game in GAMES_DATA]
    mk.add(*buttons)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, "اختر اللعبة المطلوبة:", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🔙 الرجوع")
def back(message):
    start(message)

# --- معالجة الطلبات ---
@bot.message_handler(func=lambda m: m.text in APPS_DATA or m.text in GAMES_DATA)
def order(message):
    item = message.text
    if item in APPS_DATA:
        price = int(APPS_DATA[item] * RATE)
        text = f"📌 {item}\n💰 السعر: {price:,} ل.س\n\nأرسل الآيدي الخاص بك للطلب:"
    else:
        text = f"📌 {item}\nيرجى إرسال الآيدي والكمية المطلوبة للدعم."
    bot.send_message(message.chat.id, text)

# --- بقية نظام الشحن ---
@bot.message_handler(func=lambda m: m.text == "💰 شحن رصيدي")
def recharge(message):
    msg = bot.send_message(message.chat.id, f"🚀 حول للرقم `{CASH_NUMBER}`\nثم أرسل (المبلغ - رقم العملية) هنا:")
    bot.register_next_step_handler(msg, to_admin)

def to_admin(message):
    bot.send_message(MY_ID, f"🔔 طلب جديد:\n👤 {message.from_user.first_name}\n📝 {message.text}")
    bot.send_message(message.chat.id, "⏳ تم الإرسال للمراجعة.")

@bot.message_handler(func=lambda m: m.text == "👤 حسابي")
def info(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"🆔 حسابك: `{message.chat.id}`\n💳 الرصيد: {bal:,} ل.س")

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)


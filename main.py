import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  # سعر الدولار

bot = telebot.TeleBot(TOKEN)
user_balances = {} 

# --- بيانات التطبيقات (السعر بالدولار) ---
APPS_DATA = {
    "Cocco live": 1.5, "بيغو لايف": 2, "Hiya chat": 1.2, "سوجو لايف": 1,
    "Likee": 2, "Ligo live": 1.5, "4 Fun chat": 1.8, "اوهلا شات": 2.5,
    "Yoyo chat": 1.5, "Yigo chat": 1.2, "salam chat": 2, "Tada chat": 1.5,
    "HAWA CHAT": 2.2, "BINMO CHAT": 1.8, "LAYLA CHAT": 1.5, "MIGO LIVE": 2,
    "kwai": 1.2, "SUPER LIVE": 3, "Ayome chat": 1.5, "يوهو شات": 2,
    "Pota live": 1.8, "DITTO LIVE": 2.5
}

@bot.message_handler(commands=['start'])
def start(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("🎮 قسم الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن رصيدي", "👤 حسابي")
    bot.send_message(message.chat.id, f"✅ أهلاً بك في VANTOM CARD 🇸🇾\nسعر الصرف: 1$ = {RATE:,} ل.س", reply_markup=mk)

# --- قسم التطبيقات (تحويل الأسماء لأزرار) ---
@bot.message_handler(func=lambda m: m.text == "📱 قسم التطبيقات")
def show_apps(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [types.KeyboardButton(app) for app in APPS_DATA.keys()]
    mk.add(*buttons)
    mk.add("🔙 الرجوع للقائمة الرئيسية")
    bot.send_message(message.chat.id, "اختر التطبيق الذي تريد شحنه:", reply_markup=mk)

# --- معالجة الضغط على أي تطبيق ---
@bot.message_handler(func=lambda m: m.text in APPS_DATA)
def app_details(message):
    app_name = message.text
    price_usd = APPS_DATA[app_name]
    price_sp = int(price_usd * RATE)
    
    msg = f"📌 التطبيق: {app_name}\n"
    msg += f"💵 السعر بالدولار: {price_usd}$\n"
    msg += f"💰 السعر بالليرة: {price_sp:,} ل.س\n\n"
    msg += "إرسال الآيدي (ID) الخاص بك لإتمام الطلب:"
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "🔙 الرجوع للقائمة الرئيسية")
def back_home(message):
    start(message)

# --- نظام شحن الرصيد ---
@bot.message_handler(func=lambda m: m.text == "💰 شحن رصيدي")
def recharge_req(message):
    msg = bot.send_message(message.chat.id, f"🚀 **للشحن:** حول للرقم `{CASH_NUMBER}`\nثم أرسل (المبلغ - رقم العملية) هنا:")
    bot.register_next_step_handler(msg, to_admin)

def to_admin(message):
    u_id = message.chat.id
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"ok_{u_id}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"no_{u_id}"))
    bot.send_message(MY_ID, f"🔔 طلب شحن جديد:\n👤 {message.from_user.first_name}\n🆔 `{u_id}`\n📝 {message.text}", reply_markup=mk)
    bot.send_message(u_id, "⏳ تم إرسال طلبك للإدارة للمراجعة..")

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def admin_res(call):
    uid = int(call.data.split("_")[1])
    if "ok" in call.data:
        msg = bot.send_message(MY_ID, f"🔢 أدخل المبلغ الذي تريد إضافته للحساب {uid}:")
        bot.register_next_step_handler(msg, done, uid)
    else:
        bot.send_message(uid, "❌ نعتذر، تم رفض طلب الشحن.")

def done(message, uid):
    try:
        amt = int(message.text)
        user_balances[uid] = user_balances.get(uid, 0) + amt
        bot.send_message(uid, f"✅ تم إضافة {amt:,} ل.س لرصيدك!")
        bot.send_message(MY_ID, f"✅ تم الشحن بنجاح للحساب {uid}")
    except:
        bot.send_message(MY_ID, "⚠️ خطأ! يرجى إرسال أرقام فقط.")

@bot.message_handler(func=lambda m: m.text == "👤 حسابي")
def info(message):
    bal = "∞" if message.chat.id == MY_ID else f"{user_balances.get(message.chat.id, 0):,} ل.س"
    bot.send_message(message.chat.id, f"👤 معلومات الحساب:\n🆔 `{message.chat.id}`\n💳 الرصيد الحالي: {bal}")

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

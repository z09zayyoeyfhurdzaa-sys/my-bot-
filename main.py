import telebot
from telebot import types
from datetime import datetime

# --- الإعدادات الأساسية ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

# ذاكرة الأرصدة والسجلات
user_balances = {} 
user_orders = {} 

# --- القوائم والبيانات ---
GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0},
    "كلاش أوف كلانس 🏰": {"88 جوهرة": 1.2, "550 جوهرة": 6.0, "1200 جوهرة": 11.0}
}

APPS_DATA = {
    "Cocco live": 1.5, "بيغو لايف": 2, "Hiya chat": 1.2, "سوجو لايف": 1,
    "Likee": 2, "Ligo live": 1.5, "نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5
}

# --- لوحة المفاتيح الرئيسية ---
def main_menu():
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن الرصيد", "👤 ملفي الشخصي")
    mk.add("📜 سجل طلباتي")
    return mk

@bot.message_handler(commands=['start'])
def start(message):
    welcome = f"يا أهلاً بك يا {message.from_user.first_name} في VANTOM CARD! ✨\nأسرع خدمة شحن في سوريا بخدمتك.. تفضل بالاختيار:"
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu())

# --- قسم الألعاب ---
@bot.message_handler(func=lambda m: m.text == "🎮 تسوق الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for game in GAMES_DATA.keys(): mk.add(game)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر اللعبة المطلوبة: 🕹️", reply_markup=mk)

# --- قسم التطبيقات ---
@bot.message_handler(func=lambda m: m.text == "📱 قسم التطبيقات")
def apps_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for app in APPS_DATA.keys(): mk.add(app)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر التطبيق المطلوب شحنه: 📱", reply_markup=mk)

# --- شحن الرصيد (إصلاح التعليق) ---
@bot.message_handler(func=lambda m: m.text == "💰 شحن الرصيد")
def recharge_start(message):
    msg = bot.send_message(message.chat.id, f"🚀 للتحويل: استخدم الرقم `{CASH_NUMBER}`\nبعد التحويل، أرسل (المبلغ + اسم المحول) هنا 👇")
    bot.register_next_step_handler(msg, notify_admin_payment)

def notify_admin_payment(message):
    if message.text == "🔙 العودة للرئيسية": return start(message)
    uid = message.chat.id
    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"re_ok_{uid}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"re_no_{uid}")
    )
    bot.send_message(MY_ID, f"🔔 طلب شحن رصيد:\n👤 {message.from_user.first_name}\n🆔 `{uid}`\n📝 {message.text}", reply_markup=mk)
    bot.send_message(uid, "⏳ تم إرسال طلبك للمراجعة، انتظر التأكيد.")

# --- معالجة الضغط على المنتجات ---
@bot.message_handler(func=lambda m: m.text in GAMES_DATA)
def show_game_packs(message):
    game = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for pack, p_usd in GAMES_DATA[game].items():
        mk.add(f"{pack} | {int(p_usd*RATE):,} SYP")
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, f"عروض {game}: ✨", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text in APPS_DATA)
def show_app_price(message):
    app = message.text
    price = int(APPS_DATA[app] * RATE)
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True).add(f"شراء {app} | {price:,} SYP", "🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, f"📌 {app}\n💰 السعر: {price:,} SYP", reply_markup=mk)

# --- معالجة الشراء (إصلاح الخصم والرفض) ---
@bot.message_handler(func=lambda m: " | " in m.text and "SYP" in m.text)
def handle_buy(message):
    try:
        data = message.text.split(" | ")
        item_name = data[0].replace("شراء ", "")
        price = int(data[1].replace(",", "").replace(" SYP", ""))
        uid = message.chat.id
        
        if user_balances.get(uid, 0) < price:
            bot.send_message(uid, "❌ رصيدك لا يكفي! اشحن رصيدك أولاً.")
            return

        user_balances[uid] -= price
        msg = bot.send_message(uid, f"✅ تم حجز {price:,} SYP.\nأرسل الآن **الآيدي (ID)** المطلوب شحنه:")
        bot.register_next_step_handler(msg, send_to_admin_order, item_name, price)
    except: pass

def send_to_admin_order(message, item, price):
    p_id = message.text
    uid = message.chat.id
    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ تم الشحن", callback_data=f"ord_ok_{uid}"),
        types.InlineKeyboardButton("❌ رفض وإرجاع", callback_data=f"ord_no_{uid}_{price}")
    )
    bot.send_message(MY_ID, f"🛒 طلب جديد:\n👤 {message.from_user.first_name}\n📦 {item}\n🆔 `{p_id}`\n💰 {price:,} SYP", reply_markup=mk)
    bot.send_message(uid, "🚀 وصل طلبك للإدارة! سيتم التنفيذ فوراً.")

# --- معالجة أزرار الإدارة ---
@bot.callback_query_handler(func=lambda c: True)
def admin_callbacks(call):
    d = call.data.split("_")
    uid = int(d[2])

    if d[0] == "re": # شحن رصيد
        if d[1] == "ok":
            msg = bot.send_message(MY_ID, f"كم المبلغ الذي استلمته من {uid}؟")
            bot.register_next_step_handler(msg, finalize_cash, uid)
        else: bot.send_message(uid, "❌ تم رفض طلب شحن الرصيد.")
    
    elif d[0] == "ord": # طلبات شراء
        if d[1] == "ok":
            bot.send_message(uid, "✅ تم تنفيذ طلبك بنجاح! استمتع 🎉")
            bot.edit_message_text(f"{call.message.text}\n\n✅ تم التنفيذ", MY_ID, call.message.message_id)
        else:
            price = int(d[3])
            user_balances[uid] += price
            bot.send_message(uid, f"❌ تم رفض الطلب وإعادة {price:,} SYP لرصيدك.")
            bot.edit_message_text(f"{call.message.text}\n\n❌ تم الرفض والإعادة", MY_ID, call.message.message_id)

def finalize_cash(message, uid):
    try:
        amt = int(message.text)
        user_balances[uid] = user_balances.get(uid, 0) + amt
        bot.send_message(uid, f"✅ تم إضافة {amt:,} SYP لرصيدك! شكراً لك.")
        bot.send_message(MY_ID, "✅ تم الشحن.")
    except: bot.send_message(MY_ID, "❌ أرسل أرقام فقط!")

@bot.message_handler(func=lambda m: m.text == "🔙 العودة للرئيسية")
def back(message): start(message)

@bot.message_handler(func=lambda m: m.text == "👤 ملفي الشخصي")
def profile(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 **ملفك الشخصي:**\n🆔 `{message.chat.id}`\n💳 الرصيد: {bal:,} SYP")

bot.infinity_polling(skip_pending=True)

import telebot
from telebot import types
from datetime import datetime

# --- الإعدادات النهائية المعتمدة ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 7557584016  # آيدي المطور أحمد عيسى الخاص بك
CHANNEL_ID = "@Game1stor"  # يوزر قناتك الرسمية
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

# دالة فحص الاشتراك في القناة
def check_sub(uid):
    try:
        member = bot.get_chat_member(CHANNEL_ID, uid)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True 

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    if not check_sub(uid):
        mk = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📢 انضم للقناة الرسمية", url=f"https://t.me/Game1stor"))
        bot.send_message(uid, "يا أهلاً بك! لضمان عمل الخدمة، يرجى الاشتراك في قناة المتجر أولاً، ثم أرسل /start مجدداً! ✨", reply_markup=mk)
        return

    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات", "💰 شحن الرصيد", "👤 ملفي الشخصي", "📜 سجل طلباتي")
    
    welcome = f"مرحباً بك في **Game Card Store**! 🚀\nيسعدنا خدمتك يا {message.from_user.first_name}. تفضل بالاختيار:"
    bot.send_message(uid, welcome, reply_markup=mk, parse_mode="Markdown")

# --- الأقسام ---
@bot.message_handler(func=lambda m: m.text == "🎮 تسوق الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for game in GAMES_DATA.keys(): mk.add(game)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر اللعبة المطلوبة: 🕹️", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "📱 قسم التطبيقات")
def apps_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for app in APPS_DATA.keys(): mk.add(app)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر التطبيق المطلوب: 📱", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "💰 شحن الرصيد")
def recharge_start(message):
    msg = bot.send_message(message.chat.id, f"🚀 للتحويل: استخدم الرقم `{CASH_NUMBER}`\nبعد التحويل، أرسل (المبلغ + اسم المحول) هنا 👇")
    bot.register_next_step_handler(msg, notify_admin_payment)

def notify_admin_payment(message):
    uid = message.chat.id
    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"re_ok_{uid}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"re_no_{uid}")
    )
    bot.send_message(MY_ID, f"🔔 طلب شحن رصيد:\n👤 {message.from_user.first_name}\n🆔 `{uid}`\n📝 {message.text}", reply_markup=mk)
    bot.send_message(uid, "⏳ تم إرسال طلبك للمراجعة.")

@bot.message_handler(func=lambda m: m.text in GAMES_DATA)
def show_game_packs(message):
    game = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for pack, p_usd in GAMES_DATA[game].items():
        mk.add(f"{pack} | {int(p_usd*RATE):,} SYP")
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, f"عروض {game}: ✨", reply_markup=mk)

@bot.message_handler(func=lambda m: " | " in m.text and "SYP" in m.text)
def handle_buy(message):
    data = message.text.split(" | ")
    item = data[0]
    price = int(data[1].replace(",", "").replace(" SYP", ""))
    uid = message.chat.id
    
    if user_balances.get(uid, 0) < price:
        bot.send_message(uid, "❌ رصيدك لا يكفي! اشحن رصيدك أولاً.")
        return

    user_balances[uid] -= price
    msg = bot.send_message(uid, f"✅ تم حجز {price:,} SYP. أرسل الآن الآيدي (ID) المطلوب شحنه:")
    bot.register_next_step_handler(msg, send_to_admin_order, item, price)

def send_to_admin_order(message, item, price):
    p_id, uid = message.text, message.chat.id
    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ تم الشحن", callback_data=f"ord_ok_{uid}"),
        types.InlineKeyboardButton("❌ رفض وإرجاع", callback_data=f"ord_no_{uid}_{price}")
    )
    bot.send_message(MY_ID, f"🛒 طلب جديد:\n👤 {message.from_user.first_name}\n📦 {item}\n🆔 `{p_id}`", reply_markup=mk)
    bot.send_message(uid, "🚀 وصل طلبك! سيتم التنفيذ فوراً.")

@bot.callback_query_handler(func=lambda c: True)
def admin_callbacks(call):
    d = call.data.split("_")
    uid = int(d[2])
    if d[0] == "re" and d[1] == "ok":
        msg = bot.send_message(MY_ID, f"أدخل المبلغ المضاف لـ {uid}:")
        bot.register_next_step_handler(msg, finalize_cash, uid)
    elif d[0] == "ord" and d[1] == "ok":
        bot.send_message(uid, "✅ تم الشحن بنجاح! 🎉")
        bot.edit_message_text(f"{call.message.text}\n\n✅ تم", MY_ID, call.message.message_id)

def finalize_cash(message, uid):
    amt = int(message.text)
    user_balances[uid] = user_balances.get(uid, 0) + amt
    bot.send_message(uid, f"✅ تم إضافة {amt:,} SYP لرصيدك!")
    bot.send_message(MY_ID, "✅ تم.")

@bot.message_handler(func=lambda m: m.text == "👤 ملفي الشخصي")
def profile(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 **ملفك الشخصي:**\n🆔 `{message.chat.id}`\n💳 الرصيد: {bal:,} SYP", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 العودة للرئيسية")
def back(message): start(message)

bot.infinity_polling(skip_pending=True)


import telebot
from telebot import types
import json, os

# --- الإعدادات الصحيحة من صورك ---
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
DATA_FILE = "bot_database.json"

bot = telebot.TeleBot(TOKEN)

# --- الأسعار التقريبية (ليرة سورية) ---
PRICES = {
    "pubg_60": 13500,
    "pubg_325": 66000,
    "ff_100": 12900,
    "ff_310": 38550
}

# --- إدارة قاعدة البيانات ---
def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": {}}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- الأوامر الأساسية ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    db = load_data()
    uid = str(message.chat.id)
    
    # تسجيل المستخدم إذا كان جديداً
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": message.from_user.first_name,
            "bal": 0
        }
        save_data(db)

    user_bal = db["users"][uid]["bal"]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games")
    btn2 = types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="recharge")
    btn3 = types.InlineKeyboardButton("👤 حسابي", callback_data="profile")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(message, f"💎 أهلاً بك في متجر Game Card\n💰 رصيدك الحالي: {user_bal:,} ل.س", reply_markup=markup)

# --- معالجة الضغط على الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    uid = str(call.message.chat.id)
    db = load_data()

    if call.data == "games":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"ببجي 60 شدة - {PRICES['pubg_60']:,} ل.س", callback_data="buy_pubg_60"))
        markup.add(types.InlineKeyboardButton(f"فري فاير 100 جوهرة - {PRICES['ff_100']:,} ل.س", callback_data="buy_ff_100"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("🎮 اختر الخدمة المطلوبة:", uid, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        # إعادة عرض القائمة الرئيسية
        user_bal = db["users"][uid]["bal"]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="games"),
                   types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="recharge"),
                   types.InlineKeyboardButton("👤 حسابي", callback_data="profile"))
        bot.edit_message_text(f"💎 القائمة الرئيسية\n💰 رصيدك: {user_bal:,} ل.س", uid, call.message.message_id, reply_markup=markup)

    elif call.data == "profile":
        user_bal = db["users"][uid]["bal"]
        bot.answer_callback_query(call.id, f"👤 الحساب: {uid}\n💰 الرصيد: {user_bal:,} ل.س", show_alert=True)

    elif call.data == "recharge":
        bot.send_message(uid, "📥 من فضلك أرسل رقم العملية أو صورة الإيصال ليتم مراجعتها من قبل الإدارة.")

# تشغيل البوت
print("البوت يعمل الآن...")
bot.infinity_polling()

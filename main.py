import telebot
from telebot import types
import json
import os

# --- الإعدادات ---
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
DATA_FILE = "bot_data.json"

bot = telebot.TeleBot(TOKEN)

# --- إدارة البيانات ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"users": {}, "rate": 15000, "cash_num": "0994601295"}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

db = load_data()

def init_user(uid):
    uid = str(uid)
    if uid not in db["users"]:
        db["users"][uid] = {"bal": 0, "exp": 0}
        save_data(db)

# --- الأزرار ---
def main_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="games"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="profile")
    )
    return kb

# --- المعالجات ---
@bot.message_handler(commands=["start"])
def start(message):
    init_user(message.chat.id)
    bot.send_message(message.chat.id, "Welcome!", reply_markup=main_kb())

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    
    if call.data == "profile":
        user = db["users"][uid]
        bot.send_message(uid, f"💰 رصيدك: {user['bal']:,}\n💸 مصروفاتك: {user['exp']:,}")

    elif call.data == "recharge":
        bot.send_message(uid, f"أرسل صورة التحويل لرقم الكاش: {db['cash_num']}")
        bot.register_next_step_handler(call.message, process_recharge)

    elif call.data == "games":
        # مثال لمنتج (60 شدة بـ 15,000 ليرة)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("ببجي 60 شدة - 15,000 ل.س", callback_data="buy_pubg_15000"))
        bot.send_message(uid, "اختر المنتج:", reply_markup=kb)

    elif call.data.startswith("buy_"):
        price = int(call.data.split("_")[-1])
        if db["users"][uid]["bal"] >= price:
            db["users"][uid]["bal"] -= price
            save_data(db)
            # إرسال طلب للمدير
            kb = types.InlineKeyboardMarkup()
            kb.add(
                types.InlineKeyboardButton("✅ تنفيذ", callback_data=f"adm_ok_{uid}_{price}"),
                types.InlineKeyboardButton("❌ رفض وإرجاع المال", callback_data=f"adm_no_{uid}_{price}")
            )
            bot.send_message(ADMIN_ID, f"طلب شراء من: {uid}\nالمبلغ: {price}", reply_markup=kb)
            bot.send_message(uid, "تم خصم المبلغ وطلبك قيد المراجعة...")
        else:
            bot.send_message(uid, "رصيدك غير كافٍ!")

    # تحكم المدير
    elif call.data.startswith("adm_"):
        _, action, target_uid, amount = call.data.split("_")
        amount = int(amount)
        if action == "ok":
            db["users"][target_uid]["exp"] += amount
            bot.send_message(target_uid, "✅ تم تنفيذ طلبك بنجاح!")
        else:
            db["users"][target_uid]["bal"] += amount # إرجاع المال
            bot.send_message(target_uid, "❌ تم رفض طلبك وإرجاع الرصيد لحسابك.")
        save_data(db)
        bot.edit_message_text("تمت المعالجة", ADMIN_ID, call.message.message_id)

def process_recharge(message):
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"طلب شحن من الآيدي: `{message.chat.id}`\nلإضافة رصيد استخدم: /add {message.chat.id} المبلغ")
        bot.send_message(message.chat.id, "تم إرسال الصورة للإدارة.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة فقط.")

@bot.message_handler(commands=["add"])
def add_bal(message):
    if message.chat.id == ADMIN_ID:
        parts = message.text.split()
        target, amount = parts[1], int(parts[2])
        db["users"][target]["bal"] += amount
        save_data(db)
        bot.send_message(target, f"✅ تم إضافة {amount:,} ل.س إلى رصيدك.")

bot.infinity_polling()

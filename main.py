import telebot
from telebot import types
import json, os
from datetime import datetime

# --- الإعدادات ---
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
DATA_FILE = "bot_database.json"

bot = telebot.TeleBot(TOKEN)

# ---------- قاعدة البيانات ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"users": {}}
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

def init_user(message):
    uid = str(message.chat.id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": message.from_user.first_name or "مستخدم",
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "bal": 0, "exp": 0, "vip": "0%"
        }
        save_data(db)

# ---------- القوائم ----------
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="cat_games"),
        types.InlineKeyboardButton("💬 تطبيقات الشات", callback_data="cat_apps"),
        types.InlineKeyboardButton("💳 بطاقات بليستيشن", callback_data="cat_cards"),
        types.InlineKeyboardButton("📈 رشق إنستغرام", callback_data="cat_social"),
        types.InlineKeyboardButton("📞 رصيد سيرتل", callback_data="cat_syriatel"),
        types.InlineKeyboardButton("💸 تحويل (للمسؤول)", callback_data="transfer_id"),
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="recharge_bal"),
        types.InlineKeyboardButton("👤 معلوماتي", callback_data="my_info")
    )
    return kb

# ---------- الأوامر ----------
@bot.message_handler(commands=["start"])
def start(message):
    init_user(message)
    bot.send_message(message.chat.id, "💎 أهلاً بك في متجر الخدمات\nاختر القسم المطلوب:", reply_markup=main_menu())

# ---------- معالجة الأزرار ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    mid = call.message.message_id

    if call.data == "back_main":
        bot.edit_message_text("💎 أهلاً بك في متجر الخدمات", uid, mid, reply_markup=main_menu())

    elif call.data == "my_info":
        u = db["users"].get(uid, {})
        info = f"👤 اسمك: {u.get('name')}\n🆔 آيديك: {uid}\n💰 رصيدك: {u.get('bal', 0):,}\n📆 انضمام: {u.get('join_date')}"
        bot.send_message(uid, info)

    elif call.data == "transfer_id":
        if int(uid) == ADMIN_ID:
            msg = bot.send_message(uid, "💸 أرسل ID الشخص الذي تريد التحويل له:")
            bot.register_next_step_handler(msg, process_transfer_id)
        else:
            bot.answer_callback_query(call.id, "⚠️ للمسؤول فقط", show_alert=True)

    elif call.data == "recharge_bal":
        msg = bot.send_message(uid, "📥 أرسل صورة الإيصال أو رقم العملية الآن:")
        bot.register_next_step_handler(msg, handle_recharge_data)

    elif call.data.startswith("adm_ok_"):
        if int(uid) == ADMIN_ID:
            _, _, target_uid, amount = call.data.split("_")
            db["users"][target_uid]["bal"] += int(amount)
            save_data(db)
            bot.send_message(target_uid, f"✅ تم قبول طلبك وشحن {amount} في رصيدك.")
            bot.edit_message_text(f"✅ تم الشحن لـ {target_uid} بمبلغ {amount}", ADMIN_ID, mid)

    elif call.data.startswith("adm_reject_"):
        if int(uid) == ADMIN_ID:
            _, _, target_uid, _ = call.data.split("_")
            bot.send_message(target_uid, "❌ تم رفض طلب الإيداع الخاص بك.")
            bot.edit_message_text(f"❌ تم الرفض لـ {target_uid}", ADMIN_ID, mid)

    bot.answer_callback_query(call.id)

# ---------- الوظائف ----------
def handle_recharge_data(message):
    uid = str(message.chat.id)
    bot.send_message(uid, "✅ تم إرسال بياناتك للإدارة، انتظر التأكيد.")
    
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ قبول (1000)", callback_data=f"adm_ok_{uid}_1000"))
    kb.add(types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_0"))
    
    bot.forward_message(ADMIN_ID, uid, message.message_id)
    bot.send_message(ADMIN_ID, f"📥 طلب إيداع من: {uid}", reply_markup=kb)

def process_transfer_id(message):
    target = message.text
    if target in db["users"]:
        msg = bot.send_message(message.chat.id, f"كم المبلغ لـ {target}؟")
        bot.register_next_step_handler(msg, finish_transfer, target)
    else:
        bot.send_message(message.chat.id, "❌ ID غير موجود.")

def finish_transfer(message, target):
    try:
        amt = int(message.text)
        db["users"][target]["bal"] += amt
        save_data(db)
        bot.send_message(message.chat.id, f"✅ تم إضافة {amt} لـ {target}")
        bot.send_message(target, f"🎁 أضاف المسؤول {amt} لرصيدك.")
    except:
        bot.send_message(message.chat.id, "❌ خطأ في الرقم.")

bot.infinity_polling()


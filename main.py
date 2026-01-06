import telebot
from telebot import types
import json
import os
from datetime import datetime

# --- الإعدادات ---
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
DATA_FILE = "bot_database.json"

bot = telebot.TeleBot(TOKEN)

# --- إدارة البيانات ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

db = load_data()

def init_user(message):
    uid = str(message.chat.id)
    if uid not in db["users"]:
        db["users"][uid] = {
            "name": message.from_user.first_name,
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "bal": 0, "exp": 0, "vip": "0%"
        }
        save_data(db)

# --- لوحة المفاتيح الرئيسية ---
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 قسم الألعاب", callback_data="cat_games"),
        types.InlineKeyboardButton("💬 تطبيقات الشات", callback_data="cat_apps"),
        types.InlineKeyboardButton("💳 بطاقات بليستيشن", callback_data="cat_cards"),
        types.InlineKeyboardButton("📈 رشق إنستغرام", callback_data="cat_social"),
        types.InlineKeyboardButton("📞 رصيد سيرتل", callback_data="cat_syriatel"),
        types.InlineKeyboardButton("💸 تحويل رصيد (ID)", callback_data="transfer_id"),
        types.InlineKeyboardButton("📥 إيداع رصيد", callback_data="recharge_bal"),
        types.InlineKeyboardButton("👤 معلوماتي", callback_data="my_info")
    )
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    init_user(message)
    bot.send_message(message.chat.id, "💎 أهلاً بك في متجر الخدمات\nاختر القسم المطلوب:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    
    if call.data == "my_info":
        u = db["users"][uid]
        msg = f"👤 اسمك: {u['name']}\n🆔 آيديك: `{uid}`\n💰 رصيدك: {u['bal']:,}\n💸 مستهلك: {u['exp']:,}\n📅 انضمام: {u['join_date']}\n🌟 VIP: {u['vip']}"
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif call.data == "recharge_bal":
        bot.send_message(uid, "📥 أرسل صورة الإيصال أو رقم العملية (سيرتل كاش) الآن:")
        bot.register_next_step_handler(call.message, handle_recharge_data)

    elif call.data == "transfer_id":
        msg = bot.send_message(uid, "💸 أرسل ID الشخص الذي تريد التحويل له:")
        bot.register_next_step_handler(msg, process_transfer_id)

    elif call.data.startswith("buy_"):
        _, item, price = call.data.split("_")
        price = int(price)
        if db["users"][uid]["bal"] >= price:
            msg = bot.send_message(uid, f"طلب: {item}\nالسعر: {price:,}\n\n**أدخل البيانات المطلوبة (ID أو رقم):**")
            bot.register_next_step_handler(msg, process_order, item, price)
        else: bot.send_message(uid, "❌ رصيدك غير كافٍ.")

    # --- إدارة الآدمن ---
    elif call.data.startswith("adm_"):
        _, action, target_uid, price = call.data.split("_")
        if action == "ok":
            db["users"][target_uid]["exp"] += int(price)
            bot.send_message(target_uid, "✅ تم تنفيذ طلبك بنجاح!")
            bot.edit_message_text(f"✅ تم قبول الطلب لـ {target_uid}", ADMIN_ID, call.message.message_id)
        elif action == "reject":
            msg = bot.send_message(ADMIN_ID, "أدخل سبب الرفض:")
            bot.register_next_step_handler(msg, reason_reject, target_uid, int(price), call.message.message_id)
        elif action == "addbal":
            msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ المراد إضافته لـ `{target_uid}`:")
            bot.register_next_step_handler(msg, quick_add_balance, target_uid)
        save_data(db)

# --- الوظائف التنفيذية ---
def handle_recharge_data(message):
    uid = str(message.chat.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💰 إضافة رصيد", callback_data=f"adm_addbal_{uid}_0"))
    
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, uid, message.message_id)
        bot.send_message(ADMIN_ID, f"📥 طلب شحن جديد من: `{uid}`", reply_markup=kb)
    else:
        bot.send_message(ADMIN_ID, f"📥 رقم عملية من `{uid}`:\n`{message.text}`", reply_markup=kb)
    bot.send_message(uid, "✅ تم إرسال بياناتك للإدارة.")

def quick_add_balance(message, target_uid):
    try:
        amount = int(message.text)
        db["users"][target_uid]["bal"] += amount
        save_data(db)
        bot.send_message(ADMIN_ID, f"✅ تم إضافة {amount:,} ل.س بنجاح.")
        bot.send_message(target_uid, f"💰 تم إضافة رصيد بقيمة {amount:,} ل.س إلى حسابك!")
    except: bot.send_message(ADMIN_ID, "❌ خطأ! أدخل أرقام فقط.")

def process_order(message, item, price):
    uid = str(message.chat.id)
    db["users"][uid]["bal"] -= price
    save_data(db)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok_{uid}_{price}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_{price}"))
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد: {item}\nمن: `{uid}`\nبيانات: `{message.text}`", reply_markup=kb)
    bot.send_message(uid, "⏳ طلبك قيد المراجعة.")

def reason_reject(message, target_uid, price, admin_msg_id):
    db["users"][target_uid]["bal"] += price
    save_data(db)
    bot.send_message(target_uid, f"❌ تم رفض طلبك.\nالسبب: {message.text}\n💰 تم استعادة رصيدك.")
    bot.edit_message_text(f"❌ تم الرفض وإرجاع المبلغ لـ {target_uid}", ADMIN_ID, admin_msg_id)

def process_transfer_id(message):
    target = message.text
    if target in db["users"] and target != str(message.chat.id):
        msg = bot.send_message(message.chat.id, f"المستلم: {db['users'][target]['name']}\nأدخل المبلغ:")
        bot.register_next_step_handler(msg, finish_transfer, target)
    else: bot.send_message(message.chat.id, "❌ الآيدي غير صحيح.")

def finish_transfer(message, target):
    uid = str(message.chat.id)
    try:
        amt = int(message.text)
        if db["users"][uid]["bal"] >= amt:
            db["users"][uid]["bal"] -= amt
            db["users"][target]["bal"] += amt
            save_data(db)
            bot.send_message(uid, f"✅ تم تحويل {amt:,} لـ {target}")
            bot.send_message(target, f"💰 وصلك {amt:,} من {uid}")
        else: bot.send_message(uid, "❌ رصيدك ناقص.")
    except: bot.send_message(uid, "❌ أدخل رقماً صحيحاً.")

@bot.message_handler(commands=["check"])
def admin_check(message):
    if message.chat.id == ADMIN_ID:
        res = "📋 كشف الأرصدة:\n"
        for k, v in db["users"].items(): res += f"- {v['name']} ({k}): {v['bal']:,}\n"
        bot.send_message(ADMIN_ID, res)

bot.infinity_polling()

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
            "bal": 0,
            "exp": 0,
            "vip": "0%"
        }
        save_data(db)

# --- لوحات المفاتيح ---
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

# --- المعالجات الرئيسية ---
@bot.message_handler(commands=["start"])
def start(message):
    init_user(message)
    bot.send_message(message.chat.id, "💎 أهلاً بك في بوت الخدمات المتكاملة\nاختر من القائمة أدناه:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    
    if call.data == "my_info":
        user = db["users"][uid]
        msg = (f"👤 **معلومات حسابك:**\n\n🆔 الآيدي: `{uid}`\n👤 الاسم: {user['name']}\n📅 الانضمام: {user['join_date']}\n💰 الرصيد الحالي: {user['bal']:,} ل.س\n💸 المستهلك: {user['exp']:,} ل.س\n🌟 حسم VIP: {user['vip']}")
        bot.send_message(uid, msg, parse_mode="Markdown")

    elif call.data == "cat_games":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("PUBG Mobile", callback_data="buy_أشحن ببجي_50000"),
               types.InlineKeyboardButton("Free Fire", callback_data="buy_جواهر فري فاير_45000"))
        kb.add(types.InlineKeyboardButton("Call of Duty", callback_data="buy_كول أوف ديوتي_60000"),
               types.InlineKeyboardButton("Delta Force", callback_data="buy_ديلتا فورس_70000"))
        kb.add(types.InlineKeyboardButton("Clash of Clans الأكواد", callback_data="buy_أكواد كلاش_30000"))
        kb.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("🎮 اختر اللعبة المطلوبة:", uid, call.message.message_id, reply_markup=kb)

    elif call.data == "cat_apps":
        kb = types.InlineKeyboardMarkup(row_width=2)
        apps = ["Bigo", "Sugo", "YoHo", "Salam", "Laila", "Buta", "Binmo", "Likee"]
        buttons = [types.InlineKeyboardButton(app, callback_data=f"buy_شحن {app}_25000") for app in apps]
        kb.add(*buttons)
        kb.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("💬 اختر تطبيق الشات:", uid, call.message.message_id, reply_markup=kb)

    elif call.data == "transfer_id":
        msg = bot.send_message(uid, "💸 أرسل ID الشخص الذي تريد التحويل له:")
        bot.register_next_step_handler(msg, process_transfer_id)

    elif call.data == "recharge_bal":
        bot.send_message(uid, "📥 للإيداع: أرسل الآن (صورة الإيصال) أو (رقم عملية التحويل) سيرتل كاش:")
        bot.register_next_step_handler(call.message, handle_recharge_data)

    elif data := call.data:
        if data.startswith("buy_"):
            _, item, price = data.split("_")
            price = int(price)
            if db["users"][uid]["bal"] >= price:
                msg = bot.send_message(uid, f"طلب: {item}\nالسعر: {price:,}\n\n**أرسل الآيدي (ID) المطلوب الشحن له:**")
                bot.register_next_step_handler(msg, process_order, item, price)
            else:
                bot.send_message(uid, "❌ رصيدك غير كافٍ.")

    # تحكم الآدمن
    if call.data.startswith("adm_"):
        _, action, target_uid, price = call.data.split("_")
        price = int(price)
        if action == "ok":
            db["users"][target_uid]["exp"] += price
            bot.send_message(target_uid, "✅ تم تنفيذ طلبك بنجاح!")
            bot.edit_message_text(f"✅ تم القبول لـ {target_uid}", ADMIN_ID, call.message.message_id)
        elif action == "reject":
            msg = bot.send_message(ADMIN_ID, "أدخل سبب الرفض:")
            bot.register_next_step_handler(msg, reason_reject, target_uid, price, call.message.message_id)
        save_data(db)

# --- وظائف التحويل والطلب ---
def process_transfer_id(message):
    uid = str(message.chat.id)
    target = message.text
    if target in db["users"] and target != uid:
        msg = bot.send_message(uid, f"الاسم: {db['users'][target]['name']}\nأدخل المبلغ المراد تحويله:")
        bot.register_next_step_handler(msg, finish_transfer, target)
    else:
        bot.send_message(uid, "❌ الآيدي غير صحيح أو غير مسجل.")

def finish_transfer(message, target):
    uid = str(message.chat.id)
    try:
        amount = int(message.text)
        if db["users"][uid]["bal"] >= amount:
            db["users"][uid]["bal"] -= amount
            db["users"][target]["bal"] += amount
            save_data(db)
            bot.send_message(uid, f"✅ تم تحويل {amount:,} ل.س بنجاح إلى {target}")
            bot.send_message(target, f"💰 وصلك تحويل رصيد بقيمة {amount:,} ل.س من {uid}")
        else:
            bot.send_message(uid, "❌ رصيدك غير كافٍ.")
    except:
        bot.send_message(uid, "❌ خطأ في إدخال المبلغ.")

def handle_recharge_data(message):
    uid = str(message.chat.id)
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, uid, message.message_id)
        bot.send_message(ADMIN_ID, f"💰 طلب إيداع (صورة) من: `{uid}`\nللإضافة: `/add {uid} المبلغ`")
    else:
        bot.send_message(ADMIN_ID, f"💰 طلب إيداع (رقم عملية) من: `{uid}`\nالبيانات: `{message.text}`\nللإضافة: `/add {uid} المبلغ`")
    bot.send_message(uid, "✅ تم إرسال البيانات للإدارة للتحقق.")

def process_order(message, item, price):
    uid = str(message.chat.id)
    db["users"][uid]["bal"] -= price
    save_data(db)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok_{uid}_{price}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_{price}"))
    bot.send_message(ADMIN_ID, f"🔔 طلب جديد: {item}\nمن: `{uid}`\nبيانات: `{message.text}`", reply_markup=kb)
    bot.send_message(uid, "⏳ تم استلام طلبك وخصم الرصيد مؤقتاً.")

def reason_reject(message, target_uid, price, admin_msg_id):
    db["users"][target_uid]["bal"] += price
    save_data(db)
    bot.send_message(target_uid, f"❌ تم رفض طلبك.\nالسبب: {message.text}\n💰 تم استعادة رصيدك.")
    bot.edit_message_text(f"❌ تم الرفض لـ {target_uid}", ADMIN_ID, admin_msg_id)

@bot.message_handler(commands=["add"])
def admin_add(message):
    if message.chat.id == ADMIN_ID:
        parts = message.text.split()
        db["users"][parts[1]]["bal"] += int(parts[2])
        save_data(db)
        bot.send_message(parts[1], f"💰 تم إضافة {parts[2]} ل.س لرصيدك!")

@bot.message_handler(commands=["check"])
def admin_check(message):
    if message.chat.id == ADMIN_ID:
        report = "📋 قائمة المستخدمين:\n"
        for k, v in db["users"].items():
            report += f"- {v['name']} ({k}): {v['bal']:,} ل.س\n"
        bot.send_message(ADMIN_ID, report)

bot.infinity_polling()

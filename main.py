import telebot
from telebot import types
import json, os
from datetime import datetime

TOKEN = "PUT_YOUR_TOKEN"
ADMIN_ID = 7557584016
DATA_FILE = "bot_database.json"

bot = telebot.TeleBot(TOKEN)

# ---------- DATABASE ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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

# ---------- MENUS ----------
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

def back_btn():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

def games_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🎮 PUBG - 10,000", callback_data="buy_PUBG_10000"),
        types.InlineKeyboardButton("🎮 FreeFire - 5,000", callback_data="buy_FreeFire_5000"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def apps_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("💬 Telegram Premium - 15,000", callback_data="buy_TGPremium_15000"),
        types.InlineKeyboardButton("💬 WhatsApp رقم افتراضي - 7,000", callback_data="buy_WhatsApp_7000"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def cards_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("💳 PSN 10$ - 40,000", callback_data="buy_PSN10_40000"),
        types.InlineKeyboardButton("💳 PSN 20$ - 75,000", callback_data="buy_PSN20_75000"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def social_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📈 1K متابع - 10,000", callback_data="buy_Insta1K_10000"),
        types.InlineKeyboardButton("📈 5K متابع - 45,000", callback_data="buy_Insta5K_45000"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

def syriatel_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📞 رصيد 10,000", callback_data="buy_Syriatel10_10000"),
        types.InlineKeyboardButton("📞 رصيد 25,000", callback_data="buy_Syriatel25_25000"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")
    )
    return kb

# ---------- START ----------
@bot.message_handler(commands=["start"])
def start(message):
    init_user(message)
    bot.send_message(message.chat.id, "💎 أهلاً بك في متجر الخدمات", reply_markup=main_menu())

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)

    if call.data == "cat_games":
        bot.edit_message_text("🎮 قسم الألعاب", uid, call.message.message_id, reply_markup=games_menu())

    elif call.data == "cat_apps":
        bot.edit_message_text("💬 تطبيقات الشات", uid, call.message.message_id, reply_markup=apps_menu())

    elif call.data == "cat_cards":
        bot.edit_message_text("💳 بطاقات بليستيشن", uid, call.message.message_id, reply_markup=cards_menu())

    elif call.data == "cat_social":
        bot.edit_message_text("📈 رشق إنستغرام", uid, call.message.message_id, reply_markup=social_menu())

    elif call.data == "cat_syriatel":
        bot.edit_message_text("📞 رصيد سيرتل", uid, call.message.message_id, reply_markup=syriatel_menu())

    elif call.data == "back_main":
        bot.edit_message_text("💎 أهلاً بك في متجر الخدمات", uid, call.message.message_id, reply_markup=main_menu())

    elif call.data.startswith("buy_"):
        data = call.data.split("_")
        item = data[1]
        price = int(data[2])

        if db["users"][uid]["bal"] >= price:
            msg = bot.send_message(uid, f"🛒 المنتج: {item}\n💰 السعر: {price:,}\n\nأدخل البيانات المطلوبة:")
            bot.register_next_step_handler(msg, process_order, item, price)
        else:
            bot.send_message(uid, "❌ رصيدك غير كافٍ")

    elif call.data == "my_info":
        u = db["users"][uid]
        bot.send_message(uid, f"👤 {u['name']}\n💰 رصيدك: {u['bal']:,}")

    elif call.data == "recharge_bal":
        msg = bot.send_message(uid, "📥 أرسل صورة الإيصال أو رقم العملية:")
        bot.register_next_step_handler(msg, handle_recharge_data)

    elif call.data == "transfer_id":
        msg = bot.send_message(uid, "💸 أرسل ID المستلم:")
        bot.register_next_step_handler(msg, process_transfer_id)

# ---------- ORDERS ----------
def process_order(message, item, price):
    uid = str(message.chat.id)
    db["users"][uid]["bal"] -= price
    save_data(db)

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok_{uid}_{price}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_{price}")
    )

    bot.send_message(ADMIN_ID, f"🔔 طلب جديد\n📦 {item}\n👤 {uid}\n📄 {message.text}", reply_markup=kb)
    bot.send_message(uid, "⏳ طلبك قيد المراجعة")

def handle_recharge_data(message):
    uid = str(message.chat.id)
    bot.forward_message(ADMIN_ID, uid, message.message_id)
    bot.send_message(uid, "✅ تم إرسال الطلب للإدارة")

def process_transfer_id(message):
    target = message.text
    uid = str(message.chat.id)

    if target in db["users"] and target != uid:
        msg = bot.send_message(uid, "أدخل المبلغ:")
        bot.register_next_step_handler(msg, finish_transfer, target)
    else:
        bot.send_message(uid, "❌ ID غير صالح")

def finish_transfer(message, target):
    uid = str(message.chat.id)
    try:
        amt = int(message.text)
        if db["users"][uid]["bal"] >= amt:
            db["users"][uid]["bal"] -= amt
            db["users"][target]["bal"] += amt
            save_data(db)
            bot.send_message(uid, "✅ تم التحويل")
        else:
            bot.send_message(uid, "❌ رصيدك غير كافٍ")
    except:
        bot.send_message(uid, "❌ رقم غير صحيح")

bot.infinity_polling()

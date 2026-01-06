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
        types.InlineKeyboardButton("💰 شحن حسابي", callback_data="recharge_bal"),
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
    data = call.data

    # --- قسم معلوماتي ---
    if data == "my_info":
        user = db["users"][uid]
        msg = (f"👤 **معلومات حسابك:**\n\n"
               f"🆔 الآيدي: `{uid}`\n"
               f"👤 الاسم: {user['name']}\n"
               f"📅 الانضمام: {user['join_date']}\n"
               f"💰 الرصيد الحالي: {user['bal']:,} ل.س\n"
               f"💸 المستهلك: {user['exp']:,} ل.س\n"
               f"🌟 حسم VIP: {user['vip']}")
        bot.send_message(uid, msg, parse_mode="Markdown")

    # --- أقسام المتجر ---
    elif data == "cat_games":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("PUBG Mobile", callback_data="buy_أشحن ببجي_50000"),
               types.InlineKeyboardButton("Free Fire", callback_data="buy_جواهر فري فاير_45000"))
        kb.add(types.InlineKeyboardButton("Call of Duty", callback_data="buy_كول أوف ديوتي_60000"),
               types.InlineKeyboardButton("Delta Force", callback_data="buy_ديلتا فورس_70000"))
        kb.add(types.InlineKeyboardButton("Clash of Clans الأكواد", callback_data="buy_أكواد كلاش_30000"))
        kb.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("🎮 اختر اللعبة المطلوبة:", uid, call.message.message_id, reply_markup=kb)

    elif data == "cat_apps":
        kb = types.InlineKeyboardMarkup(row_width=2)
        apps = ["Bigo", "Sugo", "YoHo", "Salam", "Laila", "Buta", "Binmo", "Likee"]
        buttons = [types.InlineKeyboardButton(app, callback_data=f"buy_شحن {app}_25000") for app in apps]
        kb.add(*buttons)
        kb.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("💬 اختر تطبيق الشات:", uid, call.message.message_id, reply_markup=kb)

    elif data == "cat_cards":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("بليستيشن ألماني 🇩🇪", callback_data="buy_PS_German_100000"),
               types.InlineKeyboardButton("بليستيشن أمريكي 🇺🇸", callback_data="buy_PS_USA_100000"))
        kb.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("💳 اختر نوع البطاقة:", uid, call.message.message_id, reply_markup=kb)

    elif data == "cat_social":
        bot.answer_callback_query(call.id, "⚠️ تنبيه: يجب تفعيل خاصية قبول المتابعين التلقائي وإلغاء Private", show_alert=True)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("رشق 1000 متابع (ضمان)", callback_data="buy_رشق إنستا_15000"))
        bot.send_message(uid, "تأكد من إعدادات حسابك ثم اطلب:", reply_markup=kb)

    # --- منطق الشراء ---
    elif data.startswith("buy_"):
        _, item, price = data.split("_")
        price = int(price)
        if db["users"][uid]["bal"] >= price:
            msg = bot.send_message(uid, f"طلب: {item}\nالسعر: {price:,}\n\n**أرسل الآن الآيدي (ID) أو البيانات المطلوبة:**")
            bot.register_next_step_handler(msg, process_order, item, price)
        else:
            bot.send_message(uid, "❌ رصيدك غير كافٍ، يرجى شحن حسابك أولاً.")

    # --- إدارة الآدمن (قبول/رفض) ---
    elif data.startswith("adm_"):
        _, action, target_uid, price = data.split("_")
        price = int(price)
        
        if action == "ok":
            db["users"][target_uid]["exp"] += price
            bot.send_message(target_uid, f"✅ تم تنفيذ طلبك بنجاح! شكراً لثقتك.")
            bot.edit_message_text(f"✅ تم قبول الطلب لـ {target_uid}", ADMIN_ID, call.message.message_id)
        
        elif action == "reject":
            msg = bot.send_message(ADMIN_ID, "أدخل سبب الرفض لإرساله للمستخدم:")
            bot.register_next_step_handler(msg, reason_reject, target_uid, price, call.message.message_id)
        
        save_data(db)

    elif data == "back_main":
        bot.edit_message_text("💎 قائمة الخدمات:", uid, call.message.message_id, reply_markup=main_menu())

    elif data == "recharge_bal":
        bot.send_message(uid, "أرسل صورة إيصال التحويل (سيرتل كاش) ليتم إضافة الرصيد لك:")
        bot.register_next_step_handler(call.message, handle_recharge_photo)

# --- وظائف إضافية ---
def process_order(message, item, price):
    uid = str(message.chat.id)
    user_input = message.text
    # خصم الرصيد مؤقتاً
    db["users"][uid]["bal"] -= price
    save_data(db)
    
    # إرسال للآدمن
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok_{uid}_{price}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_{price}"))
    
    bot.send_message(ADMIN_ID, f"🔔 **طلب جديد:**\nمن: `{uid}`\nالخدمة: {item}\nالبيانات: `{user_input}`", reply_markup=kb)
    bot.send_message(uid, "⏳ تم استلام طلبك وخصم الرصيد. بانتظار موافقة الإدارة.")

def reason_reject(message, target_uid, price, admin_msg_id):
    reason = message.text
    db["users"][target_uid]["bal"] += price # إعادة المال
    save_data(db)
    bot.send_message(target_uid, f"❌ نعتذر، تم رفض طلبك.\nالسبب: {reason}\n💰 تم إعادة الرصيد لحسابك.")
    bot.edit_message_text(f"❌ تم الرفض وإرجاع المال لـ {target_uid}\nالسبب: {reason}", ADMIN_ID, admin_msg_id)

def handle_recharge_photo(message):
    if message.content_type == 'photo':
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"💰 طلب شحن رصيد من: `{message.chat.id}`\nلإضافة الرصيد استخدم:\n`/add {message.chat.id} المبلغ`")
        bot.send_message(message.chat.id, "✅ تم إرسال الإيصال، سيتم التحقق وإضافة الرصيد قريباً.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة الإيصال حصراً.")

# --- أوامر الآدمن (إضافة رصيد وفحص) ---
@bot.message_handler(commands=["add"])
def admin_add_bal(message):
    if message.chat.id == ADMIN_ID:
        try:
            _, target, amount = message.text.split()
            db["users"][target]["bal"] += int(amount)
            save_data(db)
            bot.send_message(ADMIN_ID, f"✅ تم إضافة {amount} لـ {target}")
            bot.send_message(target, f"💰 تم إضافة رصيد بقيمة {amount} ل.س إلى حسابك!")
        except:
            bot.reply_to(message, "الاستخدام: /add ID Amount")

@bot.message_handler(commands=["check"])
def admin_check_users(message):
    if message.chat.id == ADMIN_ID:
        report = "📋 **كشف حسابات المستخدمين:**\n\n"
        for uid, info in db["users"].items():
            report += f"👤 {info['name']} | ID: `{uid}` | رصيد: {info['bal']:,}\n"
        bot.send_message(ADMIN_ID, report, parse_mode="Markdown")

bot.infinity_polling()

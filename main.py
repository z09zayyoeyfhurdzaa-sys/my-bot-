import telebot
from telebot import types
import json, os
from datetime import datetime

# --- الإعدادات ---
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU" # التوكن المستخرج من الصورة
ADMIN_ID = 7557584016
DATA_FILE = "bot_database.json"

bot = telebot.TeleBot(TOKEN)

# --- قاعدة البيانات ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"users": {}}
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
            "bal": 0
        }
        save_data(db)

# --- القوائم ---
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="cat_games"),
        types.InlineKeyboardButton("💬 التطبيقات", callback_data="cat_apps"),
        types.InlineKeyboardButton("💸 تحويل (أدمن)", callback_data="transfer_id"),
        types.InlineKeyboardButton("📥 إيداع", callback_data="recharge_bal"),
        types.InlineKeyboardButton("👤 معلوماتي", callback_data="my_info")
    )
    return kb

# --- الأوامر ---
@bot.message_handler(commands=["start"])
def start(message):
    init_user(message)
    bot.send_message(message.chat.id, "💎 متجر الخدمات جاهز:", reply_markup=main_menu())

# --- المعالجة ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    mid = call.message.message_id

    if call.data == "my_info":
        u = db["users"].get(uid, {})
        bot.send_message(uid, f"🆔 آيديك: {uid}\n💰 رصيدك: {u.get('bal', 0)}")

    elif call.data == "recharge_bal":
        msg = bot.send_message(uid, "📥 أرسل رقم العملية أو صورة الإيصال:")
        bot.register_next_step_handler(msg, handle_recharge_data)

    elif "adm_ok_" in call.data:
        data = call.data.split("_")
        target_uid, amount = data[2], data[3]
        if target_uid in db["users"]:
            db["users"][target_uid]["bal"] += int(amount)
            save_data(db)
            bot.send_message(target_uid, f"✅ تم شحن {amount} لرصيدك.")
            bot.edit_message_text(f"✅ تم الشحن لـ {target_uid}", ADMIN_ID, mid)

    elif "adm_reject_" in call.data:
        target_uid = call.data.split("_")[2]
        bot.send_message(target_uid, "❌ تم رفض طلبك.")
        bot.edit_message_text(f"❌ تم الرفض لـ {target_uid}", ADMIN_ID, mid)

    bot.answer_callback_query(call.id)

def handle_recharge_data(message):
    uid = str(message.chat.id)
    bot.send_message(uid, "⏳ تم الإرسال للمراجعة.")
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ قبول 1000", callback_data=f"adm_ok_{uid}_1000"))
    kb.add(types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_reject_{uid}_0"))
    bot.forward_message(ADMIN_ID, uid, message.message_id)
    bot.send_message(ADMIN_ID, f"طلب من: {uid}", reply_markup=kb)

bot.infinity_polling()

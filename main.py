import telebot
from telebot import types
import json
import os

# --- الإعدادات ---
TOKEN = "YOUR_NEW_TOKEN_HERE" # استبدل التوكن فوراً!
ADMIN_ID = 7557584016
DB_FILE = "users_data.json"

bot = telebot.TeleBot(TOKEN)

# --- وظائف قاعدة البيانات ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"balances": {}, "expenses": {}, "join_dates": {}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()
settings = {"rate": 15000, "cash_num": "0994601295"}

# --- القوائم (الأزرار) ---
def main_inline(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="open_games"),
        types.InlineKeyboardButton("📱 التطبيقات", callback_data="open_apps"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="open_recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="open_profile")
    )
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ لوحة الإدارة", callback_data="admin_panel"))
    return kb

# --- المعالجات ---
@bot.message_handler(commands=["start"])
def start(message):
    uid = str(message.chat.id)
    if uid not in data["balances"]:
        data["balances"][uid] = 0
        data["expenses"][uid] = 0
        data["join_dates"][uid] = message.date
        save_data(data)
    
    bot.send_message(uid, f"✨ أهلاً بك في بوت المطور\nسعر الصرف: {settings['rate']:,} ل.س", 
                     reply_markup=main_inline(int(uid)))

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = str(call.message.chat.id)
    
    if call.data == "open_profile":
        bal = data["balances"].get(uid, 0)
        exp = data["expenses"].get(uid, 0)
        text = f"👤 حسابك:\n💰 الرصيد: {bal:,} ل.س\n💸 المصروفات: {exp:,} ل.س"
        bot.send_message(uid, text)

    elif call.data == "open_recharge":
        bot.send_message(uid, f"📥 للشحن أرسل للمسؤول:\n`{settings['cash_num']}`")

    elif call.data == "open_games":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("PUBG Mobile 🔫", callback_data="buy_pubg"))
        bot.send_message(uid, "اختر اللعبة:", reply_markup=kb)

# تشغيل
print("البوت يعمل بنجاح...")
bot.infinity_polling()

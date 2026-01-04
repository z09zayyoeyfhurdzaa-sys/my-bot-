import telebot
from telebot import types
import sqlite3

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 7557584016
CHANNEL_ID = "@Game1stor"
RATE = 15000
CASH_NUMBER = "0994601295"

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=40)

# --- نظام قاعدة البيانات (لضمان الدقة المطلقة) ---
def init_db():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

def get_bal(uid):
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE uid = ?', (uid,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else 0

def update_bal(uid, amt):
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (uid, balance) VALUES (?, 0)', (uid,))
    c.execute('UPDATE users SET balance = balance + ? WHERE uid = ?', (amt, uid))
    conn.commit()
    conn.close()

# --- القوائم الحيوية (Markups) ---
def main_menu():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="cat_games"),
        types.InlineKeyboardButton("📱 التطبيقات", callback_data="cat_apps"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="profile"),
        types.InlineKeyboardButton("📜 الدعم والقناة", url=f"https://t.me/{CHANNEL_ID[1:]}")
    )
    return mk

# --- المعالجات ---
@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    bot.send_message(message.chat.id, "💎 **مرحباً بك في متجرنا المتطور**\nاستخدم الأزرار للتنقل السريع:", 
                     reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = call.message.chat.id
    
    if call.data == "profile":
        bal = get_bal(uid)
        bot.answer_callback_query(call.id, f"رصيدك الحالي: {bal:,} SYP", show_alert=True)

    elif call.data == "cat_games":
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("🔫 PUBG UC", callback_data="prod_pubg"))
        mk.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_main"))
        bot.edit_message_text("اختر القسم المطلوب:", uid, call.message.message_id, reply_markup=mk)

    elif call.data == "prod_pubg":
        mk = types.InlineKeyboardMarkup()
        packs = {"60 UC": 1, "325 UC": 5} # USD
        for name, usd in packs.items():
            price = int(usd * RATE)
            mk.add(types.InlineKeyboardButton(f"{name} - {price:,} SYP", callback_data=f"buy_{price}_PUBG"))
        bot.edit_message_text("اختر الكمية:", uid, call.message.message_id, reply_markup=mk)

    elif call.data.startswith("buy_"):
        price = int(call.data.split("_")[1])
        if get_bal(uid) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ!", show_alert=True)
        else:
            msg = bot.send_message(uid, "📝 أرسل الآن الـ ID الخاص بك:")
            bot.register_next_step_handler(msg, finalize_order, price)

    elif call.data == "recharge":
        bot.send_message(uid, f"💳 رقم التحويل: `{CASH_NUMBER}`\nأرسل قيمة المبلغ واسمك.")
        bot.register_next_step_handler(call.message, notify_admin)

    elif call.data == "back_main":
        bot.edit_message_text("القائمة الرئيسية:", uid, call.message.message_id, reply_markup=main_menu())

# --- وظائف الإدارة والتنفيذ ---
def finalize_order(message, price):
    uid = message.chat.id
    player_id = message.text
    update_bal(uid, -price) # خصم فوري
    bot.send_message(MY_ID, f"🛒 **طلب جديد**\nID: `{player_id}`\nالسعر: {price}\nالمستخدم: {uid}")
    bot.send_message(uid, "✅ تم استلام طلبك! سيتم الشحن خلال دقائق.")

def notify_admin(message):
    bot.forward_message(MY_ID, message.chat.id, message.message_id)
    bot.send_message(MY_ID, f"🔔 طلب شحن من `{message.chat.id}`\nللإضافة أرسل: `/add {message.chat.id} المبلغ`")
    bot.send_message(message.chat.id, "⏳ طلبك قيد المراجعة.")

@bot.message_handler(commands=['add'], func=lambda m: m.from_user.id == MY_ID)
def add_balance_admin(message):
    try:
        parts = message.text.split()
        target_uid, amount = int(parts[1]), int(parts[2])
        update_bal(target_uid, amount)
        bot.send_message(target_uid, f"✅ تم إضافة {amount:,} SYP لرصيدك!")
        bot.reply_to(message, "تمت الإضافة بنجاح.")
    except:
        bot.reply_to(message, "خطأ! الصيغة: /add [ID] [المبلغ]")

init_db()
bot.infinity_polling()

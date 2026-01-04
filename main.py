import telebot
from telebot import types

# --- الإعدادات الأساسية (التي حددتها أنت) ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 7557584016
CHANNEL_ID = "@Game1stor"
CASH_NUMBER = "0994601295"
RATE = 15000

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=30)

# بياناتك الكاملة كما هي
GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0},
    "كلاش أوف كلانس 🏰": {"88 جوهرة": 1.2, "550 جوهرة": 6.0, "1200 جوهرة": 11.0}
}
APPS_DATA = {
    "Cocco live": 1.5, "بيغو لايف": 2, "Hiya chat": 1.2, "سوجو لايف": 1,
    "Likee": 2, "Ligo live": 1.5, "نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5
}

user_balances = {}

# --- الدوال الحيوية (الأزرار الشمعية) ---
def main_markup():
    mk = types.InlineKeyboardMarkup(row_width=2)
    mk.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="main_games"),
        types.InlineKeyboardButton("📱 التطبيقات", callback_data="main_apps"),
        types.InlineKeyboardButton("💰 شحن الرصيد", callback_data="recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="profile"),
        types.InlineKeyboardButton("📜 سجل طلباتي", callback_data="history")
    )
    return mk

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"🚀 أهلاً بك في **Game Card Store**\nاستخدم الأزرار أدناه للتنقل السريع:", 
                     reply_markup=main_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = call.message.chat.id
    
    if call.data == "main_games":
        mk = types.InlineKeyboardMarkup(row_width=2)
        for game in GAMES_DATA.keys():
            mk.add(types.InlineKeyboardButton(game, callback_data=f"g_{game}"))
        mk.add(types.InlineKeyboardButton("🔙 عودة", callback_data="back_home"))
        bot.edit_message_text("🕹️ اختر اللعبة المطلوبة:", uid, call.message.message_id, reply_markup=mk)

    elif call.data.startswith("g_"):
        game_name = call.data.replace("g_", "")
        mk = types.InlineKeyboardMarkup(row_width=1)
        for pack, usd in GAMES_DATA[game_name].items():
            price = int(usd * RATE)
            mk.add(types.InlineKeyboardButton(f"{pack} | {price:,} SYP", callback_data=f"buy_{price}_{pack}"))
        mk.add(types.InlineKeyboardButton("🔙 عودة", callback_data="main_games"))
        bot.edit_message_text(f"✨ عروض {game_name}:", uid, call.message.message_id, reply_markup=mk)

    elif call.data == "recharge":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, f"🚀 للتحويل: استخدم الرقم `{CASH_NUMBER}`\nبعد التحويل، أرسل (المبلغ + اسم المحول) هنا 👇")
        bot.register_next_step_handler(msg, notify_admin_payment)

    elif call.data == "profile":
        bal = user_balances.get(uid, 0)
        bot.answer_callback_query(call.id, f"🆔: {uid}\n💳 رصيدك: {bal:,} SYP", show_alert=True)

    elif call.data == "back_home":
        bot.edit_message_text("القائمة الرئيسية:", uid, call.message.message_id, reply_markup=main_markup())

# --- معالجة الطلبات (نفس منطقك الأصلي مع تحسين السرعة) ---
def notify_admin_payment(message):
    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"re_ok_{message.chat.id}"),
        types.InlineKeyboardButton("❌ رفض", callback_data="re_no")
    )
    bot.send_message(MY_ID, f"🔔 طلب شحن جديد:\n👤 {message.from_user.first_name}\n🆔 `{message.chat.id}`\n📝 {message.text}", reply_markup=mk)
    bot.send_message(message.chat.id, "⏳ تم إرسال طلبك للمراجعة.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("re_ok_"))
def admin_confirm_pay(call):
    uid = int(call.data.split("_")[2])
    msg = bot.send_message(MY_ID, f"أدخل المبلغ المراد إضافته لـ {uid}:")
    bot.register_next_step_handler(msg, lambda m: finalize_cash(m, uid))

def finalize_cash(message, uid):
    amt = int(message.text)
    user_balances[uid] = user_balances.get(uid, 0) + amt
    bot.send_message(uid, f"✅ تم إضافة {amt:,} SYP لرصيدك!")
    bot.send_message(MY_ID, "✅ تمت الإضافة.")

bot.infinity_polling(skip_pending=True)

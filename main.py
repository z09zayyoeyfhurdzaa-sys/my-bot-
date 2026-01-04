import telebot
from telebot import types

# ===== الإعدادات =====
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

settings = {"rate": 15000, "cash_number": "0994601295"}
balances = {}
user_steps = {}

# ===== البيانات =====
GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}
APPS_DATA = {"نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5, "بيغو لايف": 2.0}

# ===== الأزرار الثابتة =====
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start")
    return markup

def back_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 رجوع")
    return markup

def main_inline_menu(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🎮 الألعاب", callback_data="menu_games"),
           types.InlineKeyboardButton("📱 التطبيقات", callback_data="menu_apps"),
           types.InlineKeyboardButton("🇸🇾 سيريتل كاش", callback_data="menu_syriatel"),
           types.InlineKeyboardButton("💰 شحن رصيد", callback_data="menu_recharge"),
           types.InlineKeyboardButton("👤 حسابي", callback_data="menu_profile"))
    if uid == ADMIN_ID: kb.add(types.InlineKeyboardButton("⚙️ الإدارة", callback_data="menu_admin"))
    return kb

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def send_welcome(message):
    uid = message.chat.id
    balances.setdefault(uid, 0)
    user_steps.pop(uid, None)
    bot.send_message(uid, "✨ أهلاً بك في متجر Game Card\nاختر من القائمة أدناه:", reply_markup=main_reply_keyboard())
    bot.send_message(uid, "القسم الرئيسي:", reply_markup=main_inline_menu(uid))

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data == "menu_recharge":
        user_steps[uid] = "recharge_process"
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_number']}`\nأرسل صورة أو تفاصيل التحويل:", reply_markup=back_reply_keyboard())
    
    # --- أزرار الإدارة الجديدة (قبول ورفض) ---
    elif data.startswith("adm_ok:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ لإضافته للحساب {target}:")
        bot.register_next_step_handler(msg, finalize_admin_add, target)

    elif data.startswith("adm_no:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أرسل سبب الرفض ليتم إبلاغ الزبون {target}:")
        bot.register_next_step_handler(msg, finalize_admin_reject, target)
    
    # بقية معالجات القوائم (Games, Apps, Profile...)
    elif data == "menu_profile":
        bot.answer_callback_query(call.id, f"رصيدك: {balances.get(uid, 0):,} SYP", show_alert=True)

# --- دوال الإدارة ---
def finalize_admin_add(m, target):
    try:
        amt = int(m.text)
        balances[target] = balances.get(target, 0) + amt
        bot.send_message(target, f"✅ تم قبول عملية الشحن وإضافة {amt:,} SYP لرصيدك!")
        bot.send_message(ADMIN_ID, "✅ تمت الإضافة بنجاح.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ في القيمة.")

def finalize_admin_reject(m, target):
    reason = m.text
    bot.send_message(target, f"❌ نعتذر، تم رفض طلب الشحن الخاص بك.\n📝 السبب: {reason}")
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الرفض لـ {target}.")

# --- استقبال الرسائل والتحويل للإدارة ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_all(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    
    step = user_steps.pop(uid)
    if step == "recharge_process":
        # إنشاء أزرار القبول والرفض للإدارة
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
               types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}"))
        
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن من {uid}", reply_markup=kb)
        bot.send_message(uid, "✅ تم إرسال طلبك للإدارة.", reply_markup=main_reply_keyboard())

bot.infinity_polling()

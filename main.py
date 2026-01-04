import telebot
from telebot import types

# ===== الإعدادات الأساسية =====
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

# ===== قاعدة البيانات المتغيرة (تستطيع تعديلها من البوت) =====
settings = {
    "rate": 12000,
    "cash_number": "0994601295",
    "syriatel_number": "09xxxxxxx" # يمكنك تعديله لاحقاً
}

balances = {}
user_steps = {}

GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0},
    "كلاش أوف كلانس 🏰": {"88 جوهرة": 1.2, "550 جوهرة": 6.0, "1200 جوهرة": 11.0}
}

APPS_DATA = {
    "Cocco live": 1.5, "بيغو لايف": 2.0, "Hiya chat": 1.2, "سوجو لايف": 1.0,
    "Likee": 2.0, "Ligo live": 1.5, "نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5
}

# ===== لوحة التحكم =====
def main_menu(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🎮 الألعاب", callback_data="cat_games"),
           types.InlineKeyboardButton("📱 التطبيقات", callback_data="cat_apps"))
    kb.add(types.InlineKeyboardButton("🇸🇾 تعبئة سيريتل", callback_data="syriatel"),
           types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"))
    kb.add(types.InlineKeyboardButton("👤 حسابي", callback_data="profile"))
    
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ إعدادات الإدارة", callback_data="admin_panel"))
    return kb

@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.chat.id
    balances.setdefault(uid, 0)
    bot.send_message(uid, "💎 **مرحباً بك في Game Card Store المطور**\nأفضل وأسرع خدمة شحن في سوريا.", 
                     reply_markup=main_menu(uid), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    uid = call.message.chat.id
    res = call.data
    
    if res == "cat_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES_DATA: kb.add(types.InlineKeyboardButton(g, callback_data=f"list_g:{g}"))
        bot.edit_message_text("🕹️ اختر اللعبة:", uid, call.message.message_id, reply_markup=kb)

    elif res.startswith("list_g:"):
        game = res.split(":")[1]
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES_DATA[game].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy:{p}:{price}"))
        bot.edit_message_text(f" عروض {game}:", uid, call.message.message_id, reply_markup=kb)

    elif res == "cat_apps":
        kb = types.InlineKeyboardMarkup()
        for a, u in APPS_DATA.items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"buy:{a}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", uid, call.message.message_id, reply_markup=kb)

    elif res == "syriatel":
        user_steps[uid] = "syriatel_order"
        bot.send_message(uid, "🇸🇾 أرسل رقم السيريتل والمبلغ المطلوب تعبئته:")

    elif res == "recharge":
        user_steps[uid] = "recharge_proof"
        bot.send_message(uid, f"💰 للتحويل (سيريتل كاش):\nرقمنا: `{settings['cash_number']}`\nأرسل تفاصيل التحويل هنا:")

    elif res == "admin_panel" and uid == ADMIN_ID:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📈 تغيير سعر الصرف", callback_data="edit_rate"))
        bot.send_message(uid, f"⚙️ إعداداتك الحالية:\nسعر الصرف: {settings['rate']}\nرقم الكاش: {settings['cash_number']}", reply_markup=kb)

    elif res == "edit_rate":
        user_steps[uid] = "set_rate"
        bot.send_message(uid, "أرسل سعر الصرف الجديد (رقم فقط):")

    elif res.startswith("buy:"):
        _, item, price = res.split(":")
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي!", show_alert=True)
        else:
            user_steps[uid] = {"item": item, "price": price}
            bot.send_message(uid, f"🛒 طلب {item}\nأرسل (رقمك أو ID اللاعب) للتنفيذ:")

    elif res.startswith("adm_ok:"):
        tid = int(res.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ المراد إضافته لـ {tid}:")
        bot.register_next_step_handler(msg, finalize_add, tid)

def finalize_add(message, tid):
    try:
        amt = int(message.text)
        balances[tid] = balances.get(tid, 0) + amt
        bot.send_message(tid, f"✅ تم إضافة {amt:,} SYP لرصيدك!")
        bot.send_message(ADMIN_ID, "✅ تم.")
    except: bot.send_message(ADMIN_ID, "❌ رقم غير صالح.")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_msg(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    
    step = user_steps.pop(uid)
    
    # تنفيذ الشراء
    if isinstance(step, dict):
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 **طلب جديد**\n👤 من: {uid}\n📦 المنتج: {step['item']}\n🆔 المعرف/الرقم: {msg.text}")
        bot.send_message(uid, "⏳ تم استلام طلبك وبدأ التنفيذ.")

    # طلب شحن سيريتل مباشر
    elif step == "syriatel_order":
        bot.send_message(ADMIN_ID, f"🇸🇾 **طلب تعبئة رصيد**\n👤 المستخدم: {uid}\n📝 التفاصيل: {msg.text}")
        bot.send_message(uid, "✅ تم إرسال طلب التعبئة للإدارة.")

    # إثبات شحن الرصيد
    elif step == "recharge_proof":
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ إضافة رصيد", callback_data=f"adm_ok:{uid}"))
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن رصيد من {uid}", reply_markup=kb)
        bot.send_message(uid, "✅ تم إرسال إثباتك للمراجعة.")

    # تعديل الإعدادات (للمطور فقط)
    elif step == "set_rate":
        settings["rate"] = int(msg.text)
        bot.send_message(ADMIN_ID, f"✅ تم تحديث سعر الصرف إلى: {settings['rate']}")

bot.infinity_polling()

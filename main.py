import telebot
from telebot import types

TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

# الإعدادات
settings = {"rate": 15000, "cash_num": "0994601295"}
balances = {}
user_steps = {}

# البيانات الكاملة
GAMES = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}
APPS = {"نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5, "بيغو لايف": 2.0}

# --- الأزرار الثابتة (start/ والرجوع فقط) ---
def main_kb():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("/start")

def back_kb():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 رجوع")

# --- القائمة الرئيسية الشفافة ---
def main_inline(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🎮 الألعاب", callback_data="open_games"),
           types.InlineKeyboardButton("📱 التطبيقات", callback_data="open_apps"),
           types.InlineKeyboardButton("🇸🇾 سيريتل كاش", callback_data="open_syriatel"),
           types.InlineKeyboardButton("💰 شحن رصيد", callback_data="open_recharge"),
           types.InlineKeyboardButton("👤 حسابي", callback_data="open_profile"))
    if uid == ADMIN_ID: kb.add(types.InlineKeyboardButton("⚙️ الإدارة", callback_data="open_admin"))
    return kb

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def start_cmd(message):
    uid = message.chat.id
    balances.setdefault(uid, 0)
    user_steps.pop(uid, None)
    bot.send_message(uid, "✨ أهلاً بك في المتجر\nاختر من القائمة أدناه:", reply_markup=main_kb())
    bot.send_message(uid, "القائمة الرئيسية:", reply_markup=main_inline(uid))

# --- معالج الأزرار الشفافة (تم إصلاح الوصلات) ---
@bot.callback_query_handler(func=lambda c: True)
def handle_all_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    # 1. القوائم الرئيسية
    if data == "open_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES: kb.add(types.InlineKeyboardButton(g, callback_data=f"select_game:{g}"))
        bot.edit_message_text("🕹️ اختر اللعبة:", uid, call.message.message_id, reply_markup=kb)

    elif data == "open_apps":
        kb = types.InlineKeyboardMarkup()
        for a, u in APPS.items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"buy_item:{a}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", uid, call.message.message_id, reply_markup=kb)

    elif data == "open_syriatel":
        user_steps[uid] = "step_syriatel"
        bot.send_message(uid, "🇸🇾 أرسل رقم السيريتل والمبلغ المراد تحويله:", reply_markup=back_kb())

    elif data == "open_recharge":
        user_steps[uid] = "step_recharge"
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_num']}`\nأرسل صورة أو تفاصيل التحويل:", reply_markup=back_kb())

    elif data == "open_profile":
        bot.answer_callback_query(call.id, f"💰 رصيدك: {balances.get(uid, 0):,} SYP", show_alert=True)

    # 2. اختيار الباقات
    elif data.startswith("select_game:"):
        game_name = data.split(":")[1]
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game_name].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy_item:{p}:{price}"))
        bot.edit_message_text(f"عروض {game_name}:", uid, call.message.message_id, reply_markup=kb)

    # 3. عملية الشراء
    elif data.startswith("buy_item:"):
        _, item, price = data.split(":")
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"item": item, "price": price}
            bot.send_message(uid, f"🛒 طلب {item}\nأرسل ID اللاعب أو الرقم الآن:", reply_markup=back_kb())

    # 4. أزرار الإدارة
    elif data.startswith("adm_ok:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ لإضافته للحساب {target}:")
        bot.register_next_step_handler(msg, finalize_add, target)

    elif data.startswith("adm_no:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, "أرسل سبب الرفض:")
        bot.register_next_step_handler(msg, finalize_reject, target)

# --- الدوال النهائية ---
def finalize_add(m, target):
    try:
        amt = int(m.text)
        balances[target] = balances.get(target, 0) + amt
        bot.send_message(target, f"✅ تم قبول شحن {amt:,} SYP لرصيدك!")
        bot.send_message(ADMIN_ID, "✅ تم الإضافة.")
    except: bot.send_message(ADMIN_ID, "❌ رقم غير صحيح.")

def finalize_reject(m, target):
    bot.send_message(target, f"❌ تم رفض طلب الشحن.\n📝 السبب: {m.text}")
    bot.send_message(ADMIN_ID, "✅ تم إرسال الرفض.")

# --- استقبال الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    
    step = user_steps.pop(uid)
    if isinstance(step, dict): # شراء منتج
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 طلب شراء:\n👤 {uid}\n📦 {step['item']}\n🆔 {msg.text}")
        bot.send_message(uid, "⏳ تم استلام طلبك.", reply_markup=main_kb())
    
    elif step == "step_syriatel":
        bot.send_message(ADMIN_ID, f"🇸🇾 طلب سيريتل كاش:\n👤 {uid}\n📝 {msg.text}")
        bot.send_message(uid, "✅ تم الإرسال للإدارة.", reply_markup=main_kb())

    elif step == "step_recharge":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن من {uid}", reply_markup=kb)
        bot.send_message(uid, "✅ تم الإرسال للمراجعة.", reply_markup=main_kb())

bot.infinity_polling()

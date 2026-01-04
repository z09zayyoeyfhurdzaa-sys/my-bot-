import telebot
from telebot import types

TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

# الإعدادات والبيانات
settings = {"rate": 15000, "cash_number": "0994601295"}
balances = {}
user_steps = {}

GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}
APPS_DATA = {"نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5, "بيغو لايف": 2.0}

# --- الأزرار الثابتة (فقط start والرجوع) ---
def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start")
    return markup

def back_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔙 رجوع")
    return markup

# --- الأزرار الشفافة للقائمة الرئيسية ---
def main_inline_menu(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🎮 الألعاب", callback_data="cat_games"),
           types.InlineKeyboardButton("📱 التطبيقات", callback_data="cat_apps"),
           types.InlineKeyboardButton("🇸🇾 سيريتل", callback_data="syriatel"),
           types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"),
           types.InlineKeyboardButton("👤 حسابي", callback_data="profile"))
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ الإدارة", callback_data="admin_panel"))
    return kb

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def start(msg):
    uid = msg.chat.id
    balances.setdefault(uid, 0)
    user_steps.pop(uid, None) # إلغاء أي خطوة عند الرجوع
    bot.send_message(uid, "✨ القائمة الرئيسية\nاستخدم الأزرار الشفافة للتنقل:", 
                     reply_markup=start_keyboard())
    bot.send_message(uid, "اختر القسم:", reply_markup=main_inline_menu(uid))

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    uid = call.message.chat.id
    if call.data == "cat_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES_DATA: kb.add(types.InlineKeyboardButton(g, callback_data=f"list_g:{g}"))
        bot.edit_message_text("🕹️ اختر اللعبة:", uid, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("list_g:"):
        game = call.data.split(":")[1]
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES_DATA[game].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy:{p}:{price}"))
        bot.edit_message_text(f" عروض {game}:", uid, call.message.message_id, reply_markup=kb)

    elif call.data == "recharge":
        user_steps[uid] = "recharge_proof"
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_number']}`\nأرسل تفاصيل التحويل:", reply_markup=back_keyboard())

    elif call.data.startswith("buy:"):
        _, item, price = call.data.split(":")
        if balances.get(uid, 0) < int(price):
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"item": item, "price": int(price)}
            bot.send_message(uid, f"🛒 أرسل ID اللاعب لـ {item}:", reply_markup=back_keyboard())

    elif call.data.startswith("adm_ok:"):
        target = int(call.data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, "أدخل المبلغ المراد إضافته:")
        bot.register_next_step_handler(msg, finalize_add, target)

def finalize_add(m, target):
    try:
        amt = int(m.text)
        balances[target] = balances.get(target, 0) + amt
        bot.send_message(target, f"✅ تم إضافة {amt:,} SYP")
        bot.send_message(ADMIN_ID, "✅ تم.")
    except: bot.send_message(ADMIN_ID, "خطأ في الرقم.")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    
    step = user_steps.pop(uid)
    if isinstance(step, dict): # شراء
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 طلب جديد من {uid}:\n📦 {step['item']}\n🆔 {msg.text}")
        bot.send_message(uid, "⏳ تم الاستلام، سيتم التنفيذ فوراً.", reply_markup=start_keyboard())
    elif step == "recharge_proof":
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ إضافة رصيد", callback_data=f"adm_ok:{uid}"))
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن من {uid}", reply_markup=kb)
        bot.send_message(uid, "✅ تم الإرسال للمراجعة.", reply_markup=start_keyboard())

bot.infinity_polling()

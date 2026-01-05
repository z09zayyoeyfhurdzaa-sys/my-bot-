import telebot
from telebot import types
from datetime import datetime

# يرجى تغيير التوكن فوراً من BotFather للأمان
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

# --- الإعدادات ---
settings = {"rate": 12000, "cash_num": "0994601295"}
balances = {}  
join_dates = {}  
user_steps = {}

GAMES = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}
APPS = {"نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5, "بيغو لايف": 2.0}

# --- الأزرار ---
def main_kb(): return types.ReplyKeyboardMarkup(resize_keyboard=True).add("/start")
def back_kb(): return types.ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 رجوع")

def main_inline(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="open_games"),
        types.InlineKeyboardButton("📱 التطبيقات", callback_data="open_apps"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="open_recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="open_profile")
    )
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ كشف الأرصدة", callback_data="admin_view_balances"))
        kb.add(types.InlineKeyboardButton("💸 شحن يدوي", callback_data="admin_add_balance"))
    return kb

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def start_cmd(message):
    uid = message.chat.id
    balances.setdefault(uid, 0)
    user_steps.pop(uid, None)
    bot.send_message(uid, "✨ أهلاً بك في المتجر:", reply_markup=main_kb())
    bot.send_message(uid, "القائمة الرئيسية:", reply_markup=main_inline(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data == "open_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES:
            kb.add(types.InlineKeyboardButton(g, callback_data=f"select_game:{g.replace(':','|')}"))
        bot.edit_message_text("🕹️ اختر اللعبة:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data == "open_apps":
        kb = types.InlineKeyboardMarkup()
        for a, u in APPS.items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"confirm_buy:{a.replace(':','|')}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data == "open_recharge":
        user_steps[uid] = {"step": "step_recharge"}
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_num']}`\nأرسل صورة التحويل الآن:", reply_markup=back_kb())

    elif data == "open_profile":
        bal = balances.get(uid, 0)
        bot.answer_callback_query(call.id, f"💰 رصيدك: {bal:,} SYP", show_alert=True)

    # --- تأكيد الشراء ---
    elif data.startswith("confirm_buy:"):
        _, item, price = data.split(":", 2)
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي!", show_alert=True)
        else:
            kb = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ نعم، شراء", callback_data=f"buy_now:{item}:{price}"),
                types.InlineKeyboardButton("❌ إلغاء", callback_data="open_profile")
            )
            bot.edit_message_text(f"هل أنت متأكد من شراء {item.replace('|',':')} بسعر {price:,} SYP؟", 
                                 chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data.startswith("buy_now:"):
        _, item, price = data.split(":", 2)
        user_steps[uid] = {"step": "get_id", "item": item.replace('|',':'), "price": int(price)}
        bot.send_message(uid, "🆔 أرسل ID اللاعب أو الرقم المطلوب التعبئة له:", reply_markup=back_kb())

    # --- إدارة الأدمن ---
    elif data.startswith("adm_ok:"):
        target = int(data.split(":")[1])
        user_steps[ADMIN_ID] = {"step": "adm_amt", "target": target}
        bot.send_message(ADMIN_ID, f"✅ أرسل المبلغ لإضافته لـ `{target}`:")

    elif data.startswith("adm_no:"):
        target = int(data.split(":")[1])
        user_steps[ADMIN_ID] = {"step": "adm_rej", "target": target}
        bot.send_message(ADMIN_ID, f"❌ أرسل سبب الرفض لـ `{target}`:")

    elif data == "admin_view_balances" and uid == ADMIN_ID:
        text = "📋 الأرصدة:\n" + "\n".join([f"`{u}`: {b:,}" for u, b in balances.items() if b > 0])
        bot.send_message(ADMIN_ID, text or "لا يوجد أرصدة.")

    elif data.startswith("select_game:"):
        game = data.split(":", 1)[1].replace("|", ":")
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"confirm_buy:{p.replace(':','|')}:{price}"))
        bot.edit_message_text(f"عروض {game}:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    step = user_steps[uid]

    if uid == ADMIN_ID:
        if step.get("step") == "adm_amt":
            try:
                amt = int(msg.text)
                balances[step['target']] = balances.get(step['target'], 0) + amt
                bot.send_message(step['target'], f"✅ تم شحن {amt:,} SYP لحسابك.")
                bot.send_message(ADMIN_ID, "✅ تمت الإضافة.")
                user_steps.pop(uid)
            except: bot.send_message(ADMIN_ID, "⚠️ أرقام فقط.")
            return
        elif step.get("step") == "adm_rej":
            bot.send_message(step['target'], f"❌ رُفض طلبك.\nالسبب: {msg.text}")
            bot.send_message(ADMIN_ID, "✅ تم إرسال الرفض.")
            user_steps.pop(uid)
            return

    if step.get("step") == "get_id":
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 طلب جديد\n👤: `{uid}`\n📦: {step['item']}\n🆔: `{msg.text}`")
        bot.send_message(uid, "⏳ جارٍ التنفيذ...", reply_markup=main_kb())
        user_steps.pop(uid)

    elif step.get("step") == "step_recharge":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 شحن من: `{uid}`", reply_markup=kb)
        bot.send_message(uid, "✅ تم الإرسال، انتظر التفعيل.", reply_markup=main_kb())
        user_steps.pop(uid)

bot.infinity_polling()

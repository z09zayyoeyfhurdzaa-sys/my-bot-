import telebot
from telebot import types
from datetime import datetime

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
        types.InlineKeyboardButton("🇸🇾 سيريتل كاش", callback_data="open_syriatel"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="open_recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="open_profile")
    )
    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ كشف الأرصدة ⚙️", callback_data="admin_view_balances"))
        kb.add(types.InlineKeyboardButton("💸 تعبئة رصيد يدوي", callback_data="admin_add_balance"))
    return kb

@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def start_cmd(message):
    uid = message.chat.id
    balances.setdefault(uid, 0)
    if uid not in join_dates:
        join_dates[uid] = datetime.now().strftime("%Y-%m-%d %H:%M")
    user_steps.pop(uid, None)
    bot.send_message(uid, "✨ أهلاً بك في المتجر:", reply_markup=main_kb())
    bot.send_message(uid, "القائمة الرئيسية:", reply_markup=main_inline(uid))

@bot.callback_query_handler(func=lambda c: True)
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
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"buy_item:{a.replace(':','|')}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data == "open_syriatel":
        user_steps[uid] = {"step": "syriatel_amount"}
        bot.send_message(uid, "💰 أرسل المبلغ الذي تريد تحويله:", reply_markup=back_kb())

    elif data == "open_recharge":
        user_steps[uid] = {"step": "step_recharge"}
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_num']}`\nأرسل صورة أو تفاصيل التحويل:", reply_markup=back_kb())

    elif data == "open_profile":
        balance_syp = balances.get(uid, 0)
        bot.answer_callback_query(call.id, f"💰 رصيدك الحالي: {balance_syp:,} SYP", show_alert=True)

    elif data == "admin_view_balances" and uid == ADMIN_ID:
        text = "📋 **كشف الأرصدة:**\n"
        for user, bal in balances.items():
            if bal > 0: text += f"👤 `{user}`: {bal:,} SYP\n"
        bot.send_message(ADMIN_ID, text or "لا يوجد أرصدة", parse_mode="Markdown")

    elif data == "admin_add_balance" and uid == ADMIN_ID:
        user_steps[ADMIN_ID] = {"step": "admin_add_balance_id"}
        bot.send_message(ADMIN_ID, "💸 أدخل ID المستخدم:")

    # --- معالجة القبول والرفض للأدمن ---
    elif data.startswith("adm_ok:"):
        target_id = int(data.split(":")[1])
        user_steps[ADMIN_ID] = {"step": "admin_confirm_amount", "target_id": target_id}
        bot.send_message(ADMIN_ID, f"✅ تم اختيار القبول. أرسل الآن المبلغ الذي تريد إضافته لحساب `{target_id}`:")

    elif data.startswith("adm_no:"):
        target_id = int(data.split(":")[1])
        bot.send_message(target_id, "❌ عذراً، تم رفض طلب شحن الرصيد. تأكد من البيانات.")
        bot.send_message(ADMIN_ID, "❌ تم إرسال الرفض للمستخدم.")

    elif data.startswith("select_game:"):
        game_name = data.split(":", 1)[1].replace("|", ":")
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game_name].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy_item:{p.replace(':','|')}:{price}"))
        bot.edit_message_text(f"عروض {game_name}:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data.startswith("buy_item:"):
        _, item, price = data.split(":", 2)
        item = item.replace("|", ":")
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"step": "buy_item", "item": item, "price": price}
            bot.send_message(uid, f"🛒 طلب {item}\nأرسل ID اللاعب أو الرقم الآن:", reply_markup=back_kb())

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    step = user_steps[uid]

    # تنفيذ القبول النهائي (إضافة المبلغ)
    if step.get("step") == "admin_confirm_amount" and uid == ADMIN_ID:
        try:
            amt = int(msg.text)
            target = step["target_id"]
            balances[target] = balances.get(target, 0) + amt
            bot.send_message(target, f"✅ تم قبول طلبك وشحن رصيدك بـ {amt:,} SYP")
            bot.send_message(ADMIN_ID, f"✅ تم شحن {amt:,} SYP للمستخدم {target}")
            user_steps.pop(ADMIN_ID)
        except:
            bot.send_message(ADMIN_ID, "❌ أرسل رقماً فقط.")

    elif step.get("step") == "buy_item":
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 **طلب شراء**\n👤: `{uid}`\n📦: {step['item']}\n🆔: `{msg.text}`", parse_mode="Markdown")
        bot.send_message(uid, "⏳ تم استلام بياناتك، سيتم التنفيذ فوراً.", reply_markup=main_kb())
        user_steps.pop(uid)

    elif step.get("step") == "step_recharge":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 **طلب شحن جديد**\n👤 ID: `{uid}`", reply_markup=kb, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال الإثبات، انتظر التفعيل.", reply_markup=main_kb())
        user_steps.pop(uid)

    # تكملة خطوات الأدمن اليدوية
    elif step.get("step") == "admin_add_balance_id" and uid == ADMIN_ID:
        try:
            step["target_id"] = int(msg.text)
            step["step"] = "admin_confirm_amount" # نعيد استخدامه لطلب المبلغ
            bot.send_message(ADMIN_ID, f"💰 أدخل المبلغ المطلوب إضافته لـ {msg.text}:")
        except:
            bot.send_message(ADMIN_ID, "❌ ID غير صحيح.")

bot.infinity_polling()

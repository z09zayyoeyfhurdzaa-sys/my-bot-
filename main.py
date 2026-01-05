import telebot
from telebot import types
from datetime import datetime

TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
bot = telebot.TeleBot(TOKEN, threaded=False)

# --- الإعدادات ---
settings = {"rate": 12000, "cash_num": "62154433"}
balances = {}  # الرصيد بالليرة
join_dates = {}  # تاريخ الانضمام
user_steps = {}

# --- الألعاب والتطبيقات ---
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
        kb.add(types.InlineKeyboardButton("💸 تعبئة الرصيد المجاني", callback_data="admin_add_balance"))
    return kb

# --- بدء البوت ---
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

# --- التعامل مع أزرار Inline ---
@bot.callback_query_handler(func=lambda c: True)
def handle_all_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    # الألعاب
    if data == "open_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES:
            kb.add(types.InlineKeyboardButton(g, callback_data=f"select_game:{g.replace(':','|')}"))
        bot.edit_message_text(اختر لعبتك و نطلق 🕹
        لعبة:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    # التطبيقات
    elif data == "open_apps":
        kb = types.InlineKeyboardMarkup()
        for a, u in APPS.items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"buy_item:{a.replace(':','|')}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    # سيريتل كاش
    elif data == "open_syriatel":
        user_steps[uid] = {"step": "syriatel_amount"}
        bot.send_message(uid, "💰 أرسل المبلغ الذي تريد تحويله:", reply_markup=back_kb())

    # شحن رصيد إثبات
    elif data == "open_recharge":
        user_steps[uid] = {"step": "step_recharge"}
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_num']}`\nأرسل صورة أو تفاصيل التحويل:", reply_markup=back_kb())

    # الحساب الشخصي
    elif data == "open_profile":
        first_name = call.message.chat.first_name
        last_name = call.message.chat.last_name or ""
        uid_user = call.message.chat.id
        join_date = join_dates.get(uid_user, "غير متوفر")
        balance_syp = balances.get(uid_user, 0)

        text = f"👤 الاسم: {first_name} {last_name}\n"
        text += f"🆔 الآيدي: {uid_user}\n"
        text += f"📅 تاريخ الانضمام: {join_date}\n"
        text += f"💰 الرصيد: {balance_syp:,} SYP"
        bot.answer_callback_query(call.id, text, show_alert=True)

    # كشف أرصدة المستخدمين
    elif data == "admin_view_balances" and uid == ADMIN_ID:
        text = "📋 **كشف أرصدة المستخدمين:**\n\n"
        found = False
        for user, bal in balances.items():
            if bal > 0:
                text += f"👤 ID: `{user}` | 💰: {bal:,} SYP\n"
                found = True
        if not found: text = "لا توجد حسابات فيها أرصدة حالياً."
        bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

    # تعبئة الرصيد المجاني
    elif data == "admin_add_balance" and uid == ADMIN_ID:
        user_steps[ADMIN_ID] = {"step": "admin_add_balance_id"}
        bot.send_message(ADMIN_ID, "💸 أدخل ID المستخدم لتعبئة الرصيد:")

    # اختيار لعبة
    elif data.startswith("select_game:"):
        game_name = data.split(":", 1)[1].replace("|", ":")
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game_name].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy_item:{p.replace(':','|')}:{price}"))
        bot.edit_message_text(f"عروض {game_name}:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    # شراء منتج
    elif data.startswith("buy_item:"):
        _, item, price = data.split(":", 2)
        item = item.replace("|", ":")
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"step": "buy_item", "item": item, "price": price}
            bot.send_message(uid, f"🛒 طلب {item}\nأرسل ID اللاعب أو الرقم الآن:", reply_markup=back_kb())

# --- استقبال الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    step = user_steps[uid]

    # شراء منتج
    if step.get("step") == "buy_item":
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 **طلب شراء جديد**\n👤 المستخدم: `{uid}`\n📦 المنتج: {step['item']}\n🆔 المعرف المرسل: `{msg.text}`", parse_mode="Markdown")
        bot.send_message(uid, "⏳ تم استلام بياناتك، سيتم التنفيذ فوراً.", reply_markup=main_kb())
        user_steps.pop(uid)

    # سيريتل كاش: المبلغ أولًا
    elif step.get("step") == "syriatel_amount":
        try:
            step["amount"] = int(msg.text)
            step["step"] = "syriatel_number"
            user_steps[uid] = step
            bot.send_message(uid, "📱 الآن أرسل رقم الهاتف:", reply_markup=back_kb())
        except:
            bot.send_message(uid, "❌ المبلغ غير صحيح، أرسل رقم فقط.", reply_markup=back_kb())

    # سيريتل كاش: رقم الهاتف
    elif step.get("step") == "syriatel_number":
        step["number"] = msg.text
        bot.send_message(ADMIN_ID, f"🇸🇾 **طلب سيريتل كاش جديد**\n👤 المستخدم: `{uid}`\n💰 المبلغ: {step['amount']:,} SYP\n📱 الرقم: `{step['number']}`", parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال الطلب للإدارة.", reply_markup=main_kb())
        user_steps.pop(uid)

    # شحن رصيد إثبات
    elif step.get("step") == "step_recharge":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 **طلب شحن جديد**\n👤 آيدي المستخدم: `{uid}`", reply_markup=kb, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال الإثبات، انتظر التفعيل.", reply_markup=main_kb())
        user_steps.pop(uid)

    # تعبئة الرصيد المجاني من الأدمن: ID أولًا
    elif step.get("step") == "admin_add_balance_id" and uid == ADMIN_ID:
        try:
            step["target_id"] = int(msg.text)
            step["step"] = "admin_add_balance_amount"
            user_steps[ADMIN_ID] = step
            bot.send_message(ADMIN_ID, f"💰 أدخل المبلغ لتعبئة رصيد المستخدم {step['target_id']}:")
        except:
            bot.send_message(ADMIN_ID, "❌ ID غير صحيح، أدخل رقم فقط.")

    # تعبئة الرصيد المجاني من الأدمن: المبلغ ثانيًا
    elif step.get("step") == "admin_add_balance_amount" and uid == ADMIN_ID:
        try:
            amt = int(msg.text)
            target = step["target_id"]
            balances[target] = balances.get(target, 0) + amt
            bot.send_message(target, f"✅ تم شحن رصيدك بمقدار {amt:,} SYP من الإدارة.")
            bot.send_message(ADMIN_ID, f"✅ تم إضافة {amt:,} SYP لحساب المستخدم {target}.")
            user_steps.pop(ADMIN_ID)
        except:
            bot.send_message(ADMIN_ID, "❌ المبلغ غير صحيح، أدخل رقم فقط.")

bot.infinity_polling()

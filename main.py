import telebot
from telebot import types
from datetime import datetime

# ⚠️ غيّر التوكن فوراً
TOKEN = "PUT_YOUR_TOKEN_HERE"
ADMIN_ID = 7557584016

bot = telebot.TeleBot(TOKEN, threaded=False)

# --- البيانات ---
settings = {"rate": 12000, "cash_num": "0994601295"}
balances = {}
join_dates = {}
user_steps = {}
transfer_ids = {}

GAMES = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}
APPS = {"نتفليكس 🍿": 3.0, "شاهد VIP 🎬": 2.5, "بيغو لايف": 2.0}

# --- الأزرار ---
def main_kb():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("/start")

def back_kb():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("🔙 رجوع")

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
    return kb

# --- بدء ---
@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda m: m.text == "🔙 رجوع")
def start_cmd(message):
    uid = message.chat.id

    balances.setdefault(uid, 0)
    join_dates.setdefault(uid, datetime.now().strftime("%Y-%m-%d"))
    user_steps.pop(uid, None)

    bot.send_message(uid, "✨ أهلاً بك في المتجر:", reply_markup=main_kb())
    bot.send_message(uid, "القائمة الرئيسية:", reply_markup=main_inline(uid))

# --- أزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    if data == "open_profile":
        u = call.from_user
        text = (
            f"👤 الاسم: {u.first_name}\n"
            f"🆔 الآيدي: `{uid}`\n"
            f"📅 تاريخ الانضمام: {join_dates.get(uid)}\n"
            f"💰 الرصيد: {balances.get(uid, 0):,} ل.س"
        )
        bot.send_message(uid, text, parse_mode="Markdown")

    elif data == "open_recharge":
        user_steps[uid] = {"step": "wait_transfer"}
        bot.send_message(
            uid,
            f"💰 رقم الكاش: `{settings['cash_num']}`\n"
            f"📸 أرسل صورة التحويل + رقم العملية:",
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )

    elif data == "admin_view_balances" and uid == ADMIN_ID:
        text = "📋 الأرصدة:\n"
        for u, b in balances.items():
            if b > 0:
                text += f"`{u}` ➜ {b:,}\n"
        bot.send_message(ADMIN_ID, text or "لا يوجد أرصدة.", parse_mode="Markdown")

    elif data.startswith("adm_ok:"):
        target = int(data.split(":")[1])
        user_steps[ADMIN_ID] = {"step": "ok_reason", "target": target}
        bot.send_message(ADMIN_ID, "✍️ اكتب سبب القبول:")

    elif data.startswith("adm_no:"):
        target = int(data.split(":")[1])
        user_steps[ADMIN_ID] = {"step": "rej_reason", "target": target}
        bot.send_message(ADMIN_ID, "✍️ اكتب سبب الرفض:")

# --- الرسائل ---
@bot.message_handler(content_types=["text", "photo"])
def handle_messages(msg):
    uid = msg.chat.id
    if uid not in user_steps:
        return

    step = user_steps[uid]

    # --- المستخدم ---
    if step["step"] == "wait_transfer":
        transfer_ids[uid] = msg.caption or msg.text or "غير مذكور"

        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )

        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(
            ADMIN_ID,
            f"🔔 طلب شحن جديد\n"
            f"👤 الاسم: {msg.from_user.first_name}\n"
            f"🆔 الآيدي: `{uid}`\n"
            f"🔢 رقم العملية: `{transfer_ids[uid]}`",
            reply_markup=kb,
            parse_mode="Markdown"
        )

        bot.send_message(uid, "⏳ تم استلام طلبك، انتظر المراجعة.", reply_markup=main_kb())
        user_steps.pop(uid)

    # --- الأدمن ---
    elif uid == ADMIN_ID and step["step"] == "ok_reason":
        target = step["target"]
        bot.send_message(
            target,
            f"✅ تم قبول الشحن\n"
            f"💬 السبب: {msg.text}\n"
            f"🔢 رقم العملية: {transfer_ids.get(target)}"
        )
        bot.send_message(ADMIN_ID, "✅ تم الإرسال.")
        user_steps.pop(uid)

    elif uid == ADMIN_ID and step["step"] == "rej_reason":
        target = step["target"]
        bot.send_message(
            target,
            f"❌ تم رفض الشحن\n"
            f"💬 السبب: {msg.text}\n"
            f"🔢 رقم العملية: {transfer_ids.get(target)}"
        )
        bot.send_message(ADMIN_ID, "❌ تم الإرسال.")
        user_steps.pop(uid)

# --- تشغيل ---
bot.infinity_polling()

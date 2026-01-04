import telebot
from telebot import types

# ===== الإعدادات =====
TOKEN = "PUT_YOUR_TOKEN"
ADMIN_ID = 7557584016
CHANNEL = "@Game1stor"
CASH = "0994601295"
RATE = 15000

bot = telebot.TeleBot(TOKEN)

# ===== تخزين بسيط (مستقر) =====
balances = {}
user_steps = {}

# ===== البيانات =====
GAMES = {
    "🔫 شدات ببجي": {"60 UC": 1, "325 UC": 5, "660 UC": 10},
    "💎 جواهر فري فاير": {"100 💎": 1, "210 💎": 2, "530 💎": 5}
}

# ===== الواجهات =====
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 الألعاب", callback_data="games"),
        types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="profile"),
        types.InlineKeyboardButton("📢 القناة", url=f"https://t.me/{CHANNEL[1:]}")
    )
    return kb

def back_btn():
    return types.InlineKeyboardButton("🔙 رجوع", callback_data="back")

# ===== /start =====
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.chat.id
    balances.setdefault(uid, 0)
    bot.send_message(
        uid,
        "✨ *مرحباً بك في Game Card Store*\nاختر ما تريد بكل سهولة 👇",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ===== الأزرار =====
@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    uid = call.message.chat.id
    bot.answer_callback_query(call.id)

    if call.data == "back":
        bot.edit_message_text(
            "🏠 القائمة الرئيسية:",
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif call.data == "profile":
        bal = balances.get(uid, 0)
        bot.send_message(
            uid,
            f"👤 *حسابك*\n💰 رصيدك: `{bal:,}` SYP",
            parse_mode="Markdown"
        )

    elif call.data == "games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES:
            kb.add(types.InlineKeyboardButton(g, callback_data=f"game:{g}"))
        kb.add(back_btn())
        bot.edit_message_text("🎮 اختر اللعبة:", uid, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("game:"):
        game = call.data.split(":", 1)[1]
        kb = types.InlineKeyboardMarkup()
        for pack, usd in GAMES[game].items():
            price = usd * RATE
            kb.add(
                types.InlineKeyboardButton(
                    f"{pack} • {price:,} SYP",
                    callback_data=f"buy:{game}:{pack}:{price}"
                )
            )
        kb.add(back_btn())
        bot.edit_message_text(f"🛒 عروض {game}:", uid, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("buy:"):
        _, game, pack, price = call.data.split(":")
        price = int(price)

        if balances.get(uid, 0) < price:
            bot.send_message(uid, "❌ رصيدك غير كافٍ")
            return

        user_steps[uid] = {"game": game, "pack": pack, "price": price}
        bot.send_message(uid, "🆔 أرسل ID اللاعب الآن:")

    elif call.data == "recharge":
        user_steps[uid] = {"action": "recharge"}
        bot.send_message(
            uid,
            f"💳 رقم التحويل:\n`{CASH}`\n\n📸 أرسل صورة التحويل أو التفاصيل",
            parse_mode="Markdown"
        )

# ===== الرسائل النصية =====
@bot.message_handler(func=lambda m: True)
def messages(msg):
    uid = msg.chat.id
    if uid not in user_steps:
        return

    step = user_steps.pop(uid)

    # طلب شراء
    if "price" in step:
        balances[uid] -= step["price"]
        bot.send_message(
            ADMIN_ID,
            f"🛒 طلب جديد\n👤 {uid}\n🎮 {step['game']}\n📦 {step['pack']}\n🆔 {msg.text}"
        )
        bot.send_message(uid, "⏳ تم استلام طلبك، سيتم التنفيذ قريباً ✨")

    # شحن
    elif step.get("action") == "recharge":
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(uid, "✅ تم إرسال طلب الشحن للإدارة")

# ===== تشغيل =====
print("Bot is running safely...")
bot.infinity_polling(skip_pending=True)

import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  # آيدي حسابك لتلقي الطلبات
bot = telebot.TeleBot(TOKEN)

# --- بيانات الألعاب والكميات ---
GAMES_PACKS = {
    "شدات ببجي 🔫": ["60 شدة", "325 شدة", "660 شدة"],
    "جواهر فري فاير 💎": ["100 جوهرة", "210 جوهرة", "530 جوهرة"]
}

@bot.message_handler(commands=['start'])
def start(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("🎮 قسم الألعاب", "📱 قسم التطبيقات")
    mk.add("👤 حسابي", "🛠️ الدعم الفني")
    bot.send_message(message.chat.id, "✅ أهلاً بك! اختر القسم المطلوب:", reply_markup=mk)

# --- عرض الألعاب والكميات ---
@bot.message_handler(func=lambda m: m.text == "🎮 قسم الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for game in GAMES_PACKS.keys(): mk.add(game)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, "اختر اللعبة:", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text in GAMES_PACKS)
def show_packs(message):
    game_name = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pack in GAMES_PACKS[game_name]: mk.add(pack)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, f"اختر الكمية لـ {game_name}:", reply_markup=mk)

# --- طلب الآيدي ثم إرسال الطلب للإدارة ---
@bot.message_handler(func=lambda m: any(m.text in packs for packs in GAMES_PACKS.values()))
def ask_id(message):
    selected_pack = message.text
    # تحديد اسم اللعبة بناءً على الكمية المختارة
    game_name = next(g for g, p in GAMES_PACKS.items() if selected_pack in p)
    msg = bot.send_message(message.chat.id, f"أرسل الآن **الآيدي (ID)** الخاص باللاعب لطلب {selected_pack}:")
    bot.register_next_step_handler(msg, send_to_admin, game_name, selected_pack)

def send_to_admin(message, game, pack):
    player_id = message.text
    user_chat_id = message.chat.id
    user_name = message.from_user.first_name

    # إنشاء أزرار القبول والرفض للإدارة
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"accept_{user_chat_id}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_chat_id}"))

    admin_msg = f"""
🔔 **طلب شحن جديد:**
━━━━━━━━━━━━━
👤 **صاحب الطلب:** {user_name}
🆔 **آيدي حساب البوت:** `{user_chat_id}`
🎮 **اللعبة:** {game}
📦 **الكمية:** {pack}
🆔 **آيدي اللاعب:** `{player_id}`
━━━━━━━━━━━━━
    """
    bot.send_message(MY_ID, admin_msg, reply_markup=mk, parse_mode="Markdown")
    bot.send_message(user_chat_id, "⏳ تم إرسال طلبك للإدارة، يرجى الانتظار للموافقة.")

# --- معالجة قرار الإدارة (قبول/رفض) ---
@bot.callback_query_handler(func=lambda c: c.data.startswith(("accept_", "reject_")))
def admin_decision(call):
    target_user_id = int(call.data.split("_")[1])
    
    if "accept" in call.data:
        bot.send_message(target_user_id, "✅ تم قبول طلبك وشحن حسابك بنجاح! شكراً لتعاملك معنا.")
        bot.edit_message_text(f"{call.message.text}\n\n✅ **تمت الموافقة بنجاح**", MY_ID, call.message.message_id)
    else:
        bot.send_message(target_user_id, "❌ نعتذر منك، تم رفض طلب الشحن الخاص بك.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ **تم الرفض**", MY_ID, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "🔙 الرجوع")
def back(message): start(message)

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

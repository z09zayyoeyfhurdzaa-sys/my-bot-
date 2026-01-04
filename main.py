import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  

bot = telebot.TeleBot(TOKEN)
user_balances = {} 

# --- القوائم والكميات ---
GAMES_PACKS = {
    "شدات ببجي 🔫": ["60 شدة", "325 شدة", "660 شدة"],
    "جواهر فري فاير 💎": ["100 جوهرة", "210 جوهرة", "530 جوهرة"]
}

APPS_DATA = ["Cocco live", "بيغو لايف", "Hiya chat", "سوجو لايف"] # يمكنك إكمال القائمة

@bot.message_handler(commands=['start'])
def start(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("🎮 قسم الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن رصيدي", "👤 حسابي")
    bot.send_message(message.chat.id, "✅ اختر القسم المطلوب:", reply_markup=mk)

# --- عرض الألعاب ---
@bot.message_handler(func=lambda m: m.text == "🎮 قسم الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for game in GAMES_PACKS.keys():
        mk.add(game)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, "اختر اللعبة:", reply_markup=mk)

# --- عرض الكميات بعد اختيار اللعبة ---
@bot.message_handler(func=lambda m: m.text in GAMES_PACKS)
def show_packs(message):
    game_name = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for pack in GAMES_PACKS[game_name]:
        mk.add(pack)
    mk.add("🔙 الرجوع")
    bot.send_message(message.chat.id, f"اختر الكمية المطلوبة لـ {game_name}:", reply_markup=mk)

# --- طلب الآيدي بعد اختيار الكمية ---
@bot.message_handler(func=lambda m: any(m.text in packs for packs in GAMES_PACKS.values()))
def ask_id(message):
    selected_pack = message.text
    msg = bot.send_message(message.chat.id, f"لقد اخترت {selected_pack}.\nالآن أرسل **الآيدي (ID)** الخاص بك لإتمام الطلب:")
    bot.register_next_step_handler(msg, process_order, selected_pack)

def process_order(message, pack):
    user_id_game = message.text
    # إرسال الطلب لك كصاحب متجر
    bot.send_message(MY_ID, f"🔔 طلب جديد:\n👤 {message.from_user.first_name}\n📦 المنتج: {pack}\n🆔 آيدي اللاعب: `{user_id_game}`")
    bot.send_message(message.chat.id, "✅ تم استلام طلبك بنجاح! سيتم التنفيذ قريباً.")

@bot.message_handler(func=lambda m: m.text == "🔙 الرجوع")
def back(message):
    start(message)

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

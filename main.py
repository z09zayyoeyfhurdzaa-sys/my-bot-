import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  

bot = telebot.TeleBot(TOKEN)
user_balances = {} # هنا يتم تخزين أرصدة المستخدمين

# --- الألعاب والأسعار (بالدولار) ---
GAMES_PACKS = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}

@bot.message_handler(commands=['start'])
def start(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("🎮 قسم الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن رصيدي", "👤 حسابي")
    bot.send_message(message.chat.id, f"✅ أهلاً بك! سعر الصرف: {RATE:,}", reply_markup=mk)

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

# --- فحص الرصيد قبل طلب الآيدي ---
@bot.message_handler(func=lambda m: any(m.text in packs for packs in GAMES_PACKS.values()))
def check_balance_and_ask_id(message):
    selected_pack = message.text
    # جلب السعر
    game_name = next(g for g, p in GAMES_PACKS.items() if selected_pack in p)
    price_usd = GAMES_PACKS[game_name][selected_pack]
    price_sp = int(price_usd * RATE)
    
    user_id = message.chat.id
    current_balance = user_balances.get(user_id, 0)

    if current_balance < price_sp:
        bot.send_message(user_id, f"❌ رصيدك غير كافٍ!\n💰 سعر المنتج: {price_sp:,} ل.س\n💳 رصيدك الحالي: {current_balance:,} ل.س\n\nيرجى ضغط '💰 شحن رصيدي' وتعبئة حسابك أولاً.")
    else:
        msg = bot.send_message(user_id, f"✅ رصيدك كافٍ. السعر: {price_sp:,} ل.س\nأرسل الآن **آيدي اللاعب** لإتمام الطلب:")
        bot.register_next_step_handler(msg, send_to_admin, game_name, selected_pack, price_sp)

def send_to_admin(message, game, pack, price):
    player_id = message.text
    user_chat_id = message.chat.id
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"acc_{user_chat_id}_{price}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_{user_chat_id}"))

    admin_msg = f"🔔 **طلب شحن جديد:**\n👤 الحساب: {message.from_user.first_name}\n🆔 آيدي الحساب: `{user_chat_id}`\n🎮 اللعبة: {game}\n📦 الكمية: {pack}\n🆔 آيدي اللاعب: `{player_id}`\n💰 السعر: {price:,} ل.س"
    bot.send_message(MY_ID, admin_msg, reply_markup=mk)
    bot.send_message(user_chat_id, "⏳ تم إرسال طلبك. سيتم خصم المبلغ عند موافقة الإدارة.")

# --- معالجة قرار الإدارة والخصم التلقائي ---
@bot.callback_query_handler(func=lambda c: c.data.startswith(("acc_", "rej_", "ok_", "no_")))
def admin_res(call):
    data = call.data.split("_")
    uid = int(data[1])
    
    if data[0] == "acc": # موافقة على طلب شحن لعبة
        price = int(data[2])
        user_balances[uid] -= price # خصم المبلغ من الرصيد
        bot.send_message(uid, f"✅ تم قبول طلبك وشحن حسابك! تم خصم {price:,} ل.س.")
        bot.edit_message_text(f"{call.message.text}\n\n✅ تمت الموافقة والخصم.", MY_ID, call.message.message_id)
    
    elif data[0] == "rej": # رفض طلب شحن لعبة
        bot.send_message(uid, "❌ نعتذر، تم رفض طلبك.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ تم الرفض.", MY_ID, call.message.message_id)

    # نظام شحن الرصيد الأساسي (موافقة المسؤول على زيادة رصيد مستخدم)
    elif data[0] == "ok":
        msg = bot.send_message(MY_ID, f"أدخل مبلغ التعبئة للحساب {uid}:")
        bot.register_next_step_handler(msg, add_money, uid)

def add_money(message, uid):
    try:
        amt = int(message.text)
        user_balances[uid] = user_balances.get(uid, 0) + amt
        bot.send_message(uid, f"✅ تمت تعبئة رصيدك بمبلغ {amt:,} ل.س بنجاح!")
        bot.send_message(MY_ID, f"✅ تم إضافة الرصيد للحساب {uid}")
    except:
        bot.send_message(MY_ID, "خطأ في الرقم.")

@bot.message_handler(func=lambda m: m.text == "👤 حسابي")
def info(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 معلوماتك:\n🆔 `{message.chat.id}`\n💳 الرصيد: {bal:,} ل.س")

@bot.message_handler(func=lambda m: m.text == "🔙 الرجوع")
def back(message): start(message)

# نظام شحن الرصيد (الطلب الأولي)
@bot.message_handler(func=lambda m: m.text == "💰 شحن رصيدي")
def recharge_req(message):
    msg = bot.send_message(message.chat.id, f"🚀 حول للرقم `{CASH_NUMBER}`\nأرسل (المبلغ - رقم العملية) هنا:")
    bot.register_next_step_handler(msg, notify_admin_recharge)

def notify_admin_recharge(message):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ تعبئة رصيد", callback_data=f"ok_{message.chat.id}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"no_{message.chat.id}"))
    bot.send_message(MY_ID, f"🔔 طلب تعبئة رصيد:\n📝 {message.text}", reply_markup=mk)
    bot.send_message(message.chat.id, "⏳ تم إرسال طلب التعبئة للمراجعة.")

bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

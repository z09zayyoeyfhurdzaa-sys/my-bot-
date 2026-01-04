import telebot
from telebot import types
from datetime import datetime

# --- الإعدادات الأساسية ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  # سعر الصرف داخلي فقط

bot = telebot.TeleBot(TOKEN, threaded=True)

# قواعد بيانات مؤقتة
user_balances = {} 
user_orders = {} 

# --- المنتجات (السعر بالدولار ليتم تحويله تلقائياً) ---
GAMES_PACKS = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}

# --- عبارة ترحيبية جذابة ---
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن الرصيد", "👤 ملفي الشخصي")
    mk.add("📜 سجل طلباتي")
    
    welcome_msg = (
        f"يا أهلاً بك يا {name} في متجر VANTOM CARD! ✨\n\n"
        "يسعدنا أن نكون اختيارك الأول لشحن ألعابك وتطبيقاتك المفضلة. 🌟\n"
        "تصفح الأقسام الآن واستمتع بأفضل الأسعار والخدمة السريعة! 🚀"
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=mk)

# --- عرض المنتجات بالليرة السورية فقط ---
@bot.message_handler(func=lambda m: m.text == "🎮 تسوق الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for game in GAMES_PACKS.keys(): mk.add(game)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر اللعبة التي تود شحنها الآن: 🕹️", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text in GAMES_PACKS)
def show_packs(message):
    game_name = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for pack, price_usd in GAMES_PACKS[game_name].items():
        price_syp = int(price_usd * RATE) # التحويل لليرة
        mk.add(f"{pack} | {price_syp:,} SYP")
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, f"إليك عروض {game_name} المتوفرة: ✨", reply_markup=mk)

# --- معالجة الطلب وفحص الرصيد ---
@bot.message_handler(func=lambda m: " | " in m.text and "SYP" in m.text)
def process_order(message):
    data = message.text.split(" | ")
    pack = data[0]
    price_syp = int(data[1].replace(",", "").replace(" SYP", ""))
    uid = message.chat.id
    
    balance = user_balances.get(uid, 0)
    if balance < price_syp:
        bot.send_message(uid, f"عذراً يا صديقي، رصيدك الحالي ({balance:,} SYP) لا يكفي لإتمام الطلب. 😔\nيرجى شحن رصيدك للمتابعة.")
    else:
        user_balances[uid] -= price_syp
        msg = bot.send_message(uid, f"تم حجز {price_syp:,} SYP من رصيدك بنجاح. ✅\nيرجى إرسال **الآيدي (ID)** الخاص باللاعب الآن:")
        bot.register_next_step_handler(msg, send_to_admin, pack, price_syp)

def send_to_admin(message, pack, price):
    player_id = message.text
    uid = message.chat.id
    
    # إضافة للسجل
    order_info = {"item": pack, "price": price, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "⏳ قيد المراجعة"}
    if uid not in user_orders: user_orders[uid] = []
    user_orders[uid].append(order_info)
    order_idx = len(user_orders[uid]) - 1

    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"acc_{uid}_{order_idx}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_{uid}_{order_idx}_{price}"))

    bot.send_message(MY_ID, f"🔔 **طلب شحن جديد:**\n👤 {message.from_user.first_name}\n📦 {pack}\n🆔 اللاعب: `{player_id}`\n💰 السعر: {price:,} SYP", reply_markup=mk)
    bot.send_message(uid, "وصل طلبك لفريقنا! يمكنك متابعة الحالة من 'سجل طلباتي'. 📅")

# --- التحكم بالإدارة ---
@bot.callback_query_handler(func=lambda c: c.data.startswith(("acc_", "rej_")))
def handle_admin(call):
    data = call.data.split("_")
    uid, idx = int(data[1]), int(data[2])
    
    if data[0] == "acc":
        user_orders[uid][idx]['status'] = "✅ تم الشحن"
        bot.send_message(uid, f"أخبار رائعة! 🎉 تم شحن طلبك ({user_orders[uid][idx]['item']}) بنجاح.")
        bot.edit_message_text(f"{call.message.text}\n\n✅ تم القبول", MY_ID, call.message.message_id)
    elif data[0] == "rej":
        price = int(data[3])
        user_balances[uid] += price
        user_orders[uid][idx]['status'] = "❌ مرفوض (مسترجع)"
        bot.send_message(uid, f"نعتذر، تم رفض الطلب وأعيد مبلغ {price:,} SYP لرصيدك. 🔄")
        bot.edit_message_text(f"{call.message.text}\n\n❌ تم الرفض", MY_ID, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "📜 سجل طلباتي")
def history(message):
    uid = message.chat.id
    orders = user_orders.get(uid, [])
    if not orders:
        bot.send_message(uid, "سجلك فارغ حالياً، بانتظار أول طلب لك! 😉")
        return
    msg = "📜 **تاريخ طلباتك:**\n\n"
    for o in orders[-5:]:
        msg += f"📦 {o['item']}\n💰 {o['price']:,} SYP\n📅 {o['date']}\nحالة: {o['status']}\n\n"
    bot.send_message(uid, msg)

@bot.message_handler(func=lambda m: m.text == "👤 ملفي الشخصي")
def profile(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 **ملفك الشخصي:**\n\n🆔 المعرف: `{message.chat.id}`\n💳 الرصيد: {bal:,} SYP", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 العودة للرئيسية")
def back(message): start(message)

bot.infinity_polling(skip_pending=True)

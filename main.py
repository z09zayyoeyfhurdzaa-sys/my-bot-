import telebot
from telebot import types
from datetime import datetime

# --- الإعدادات (سرعة قصوى) ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
RATE = 15000  

# تفعيل 20 مسار معالجة لضمان عدم التأخير نهائياً
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

user_balances = {} 
user_orders = {} 

# --- قائمة المنتجات المحدثة ---
GAMES_DATA = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0},
    "كلاش أوف كلانس 🏰": {"88 جوهرة": 1.2, "550 جوهرة": 6.0, "1200 جوهرة": 11.0}
}

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات", "💰 شحن الرصيد", "👤 ملفي الشخصي", "📜 سجل طلباتي")
    
    welcome = f"يا أهلاً بك يا {name} في Game Card Store ✨\n\nأسرع بوت شحن في سوريا بخدمتك الآن.. تفضل باختيار القسم المطلوب: 👇"
    bot.send_message(message.chat.id, welcome, reply_markup=mk)

@bot.message_handler(func=lambda m: m.text == "🎮 تسوق الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for game in GAMES_DATA.keys(): mk.add(game)
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, "اختر لعبتك المفضلة وانطلق! 🕹️", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text in GAMES_DATA)
def show_packs(message):
    game_name = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for pack, price_usd in GAMES_DATA[game_name].items():
        price_syp = int(price_usd * RATE)
        mk.add(f"{pack} | {price_syp:,} SYP")
    mk.add("🔙 العودة للرئيسية")
    bot.send_message(message.chat.id, f"إليك عروض {game_name}: ✨", reply_markup=mk)

@bot.message_handler(func=lambda m: " | " in m.text and "SYP" in m.text)
def handle_purchase(message):
    try:
        data = message.text.split(" | ")
        pack = data[0]
        price = int(data[1].replace(",", "").replace(" SYP", ""))
        uid = message.chat.id
        
        if user_balances.get(uid, 0) < price:
            bot.send_message(uid, f"عذراً، رصيدك الحالي لا يكفي. 😔\nسعر المنتج: {price:,} SYP")
            return

        user_balances[uid] -= price
        msg = bot.send_message(uid, f"تم حجز {price:,} SYP. ✅\nأرسل الآن **الآيدي (ID)** أو **كود الحساب**:")
        bot.register_next_step_handler(msg, send_to_admin, pack, price)
    except: pass

def send_to_admin(message, pack, price):
    p_id = message.text
    uid = message.chat.id
    
    order_idx = len(user_orders.get(uid, []))
    if uid not in user_orders: user_orders[uid] = []
    user_orders[uid].append({"item": pack, "price": price, "date": datetime.now().strftime("%H:%M"), "status": "⏳ مراجعة"})

    mk = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ موافقة", callback_data=f"acc_{uid}_{order_idx}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_{uid}_{order_idx}_{price}")
    )
    bot.send_message(MY_ID, f"🔔 **طلب جديد:**\n👤 {message.from_user.first_name}\n📦 {pack}\n🆔 `{p_id}`\n💰 {price:,} SYP", reply_markup=mk)
    bot.send_message(uid, "استلمنا طلبك! سيتم التنفيذ خلال لحظات. 🚀")

@bot.callback_query_handler(func=lambda c: True)
def admin_buttons(call):
    d = call.data.split("_")
    uid, idx = int(d[1]), int(d[2])
    
    if d[0] == "acc":
        user_orders[uid][idx]['status'] = "✅ تم"
        bot.send_message(uid, f"تم شحن {user_orders[uid][idx]['item']}! استمتع 🎉")
        bot.edit_message_text(f"{call.message.text}\n\n✅ تم التنفيذ", MY_ID, call.message.message_id)
    elif d[0] == "rej":
        price = int(d[3])
        user_balances[uid] += price
        user_orders[uid][idx]['status'] = "❌ مرفوض"
        bot.send_message(uid, f"نعتذر، تم الرفض وإعادة {price:,} SYP لرصيدك. 🔄")
        bot.edit_message_text(f"{call.message.text}\n\n❌ تم الرفض", MY_ID, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "👤 ملفي الشخصي")
def profile(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 **حسابك:**\n🆔 `{message.chat.id}`\n💳 الرصيد: {bal:,} SYP")

@bot.message_handler(func=lambda m: m.text == "🔙 العودة للرئيسية")
def back(message): start(message)

# حذف الويب هوك وبدء العمل بأقصى سرعة
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)

import telebot
from telebot import types
from datetime import datetime

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 
RATE = 15000  

bot = telebot.TeleBot(TOKEN, threaded=True)

# مخزن البيانات
user_balances = {} 
user_orders = {} 

# --- المنتجات والأسعار ---
GAMES_PACKS = {
    "شدات ببجي 🔫": {"60 شدة": 1.0, "325 شدة": 5.0, "660 شدة": 10.0},
    "جواهر فري فاير 💎": {"100 جوهرة": 1.0, "210 جوهرة": 2.0, "530 جوهرة": 5.0}
}

# --- 1. الرسالة الترحيبية (تظهر عند البداية فقط) ---
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    
    # بناء الأزرار بحجم كبير وواضح
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add(types.KeyboardButton("🎮 تسوق الألعاب"), types.KeyboardButton("📱 قسم التطبيقات"))
    mk.add(types.KeyboardButton("💰 شحن الرصيد"), types.KeyboardButton("👤 ملفي الشخصي"))
    mk.add(types.KeyboardButton("📜 سجل طلباتي"))
    
    # نص ترحيبي ودي بدون سعر الصرف
    welcome_text = (
        f"يا أهلاً بك يا {name} في متجر VANTOM CARD! ✨\n\n"
        "يسعدنا جداً انضمامك إلينا. هنا تجد كل ما تحتاجه لشحن ألعابك وتطبيقاتك المفضلة بأفضل الأسعار وأسرع خدمة في سوريا! 🇸🇾🚀\n\n"
        "تفضل باختيار القسم الذي تريده من القائمة بالأسفل ونحن في خدمتك. 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=mk)

# --- 2. عرض المنتجات بالـ SYP فقط ---
@bot.message_handler(func=lambda m: m.text == "🎮 تسوق الألعاب")
def games_menu(message):
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for game in GAMES_PACKS.keys(): mk.add(types.KeyboardButton(game))
    mk.add(types.KeyboardButton("🔙 العودة للرئيسية"))
    bot.send_message(message.chat.id, "اختر اللعبة التي تود شحنها الآن: 🕹️", reply_markup=mk)

@bot.message_handler(func=lambda m: m.text in GAMES_PACKS)
def show_packs(message):
    game_name = message.text
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for pack, price_usd in GAMES_PACKS[game_name].items():
        price_syp = int(price_usd * RATE) 
        mk.add(types.KeyboardButton(f"{pack} | {price_syp:,} SYP"))
    mk.add(types.KeyboardButton("🔙 العودة للرئيسية"))
    bot.send_message(message.chat.id, f"إليك أفضل العروض المتوفرة لـ {game_name}: ✨", reply_markup=mk)

# --- 3. معالجة الطلب وفحص الرصيد ---
@bot.message_handler(func=lambda m: " | " in m.text and "SYP" in m.text)
def process_order(message):
    try:
        data = message.text.split(" | ")
        pack = data[0]
        price_syp = int(data[1].replace(",", "").replace(" SYP", ""))
        uid = message.chat.id
        
        balance = user_balances.get(uid, 0)
        if balance < price_syp:
            bot.send_message(uid, f"عذراً يا صديقي، رصيدك الحالي ({balance:,} SYP) أقل من سعر المنتج. 😔\nيرجى شحن رصيدك للمتابعة.")
        else:
            user_balances[uid] -= price_syp
            msg = bot.send_message(uid, f"تم حجز {price_syp:,} SYP من رصيدك بنجاح. ✅\nأرسل الآن **الآيدي (ID)** الخاص باللاعب لإتمام الشحن:")
            bot.register_next_step_handler(msg, send_to_admin, pack, price_syp)
    except:
        bot.send_message(message.chat.id, "حدث خطأ بسيط، يرجى المحاولة مرة أخرى.")

def send_to_admin(message, pack, price):
    player_id = message.text
    uid = message.chat.id
    
    # تسجيل في السجل
    order_info = {"item": pack, "price": price, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "⏳ قيد المراجعة"}
    if uid not in user_orders: user_orders[uid] = []
    user_orders[uid].append(order_info)
    order_idx = len(user_orders[uid]) - 1

    # أزرار الإدارة
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"acc_{uid}_{order_idx}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"rej_{uid}_{order_idx}_{price}"))

    bot.send_message(MY_ID, f"🔔 **طلب شحن جديد:**\n👤 {message.from_user.first_name}\n📦 {pack}\n🆔 اللاعب: `{player_id}`\n💰 السعر: {price:,} SYP", reply_markup=mk)
    bot.send_message(uid, "رائع! وصل طلبك لفريقنا بنجاح. 🚀\nسنقوم بمعالجته خلال دقائق، ترقب الإشعار!")

# --- 4. التحكم بالإدارة (الموافقة والرفض) ---
@bot.callback_query_handler(func=lambda c: c.data.startswith(("acc_", "rej_")))
def handle_admin(call):
    data = call.data.split("_")
    uid, idx = int(data[1]), int(data[2])
    
    if data[0] == "acc":
        user_orders[uid][idx]['status'] = "✅ تم الشحن"
        bot.send_message(uid, f"أخبار رائعة! 🎉 تم شحن طلبك ({user_orders[uid][idx]['item']}) بنجاح. استمتع!")
        bot.edit_message_text(f"{call.message.text}\n\n✅ تم القبول والشحن", MY_ID, call.message.message_id)
    elif data[0] == "rej":
        price = int(data[3])
        user_balances[uid] += price
        user_orders[uid][idx]['status'] = "❌ مرفوض (مسترجع)"
        bot.send_message(uid, f"نعتذر منك، تم رفض الطلب وأعيد مبلغ {price:,} SYP لرصيدك فوراً. 🔄")
        bot.edit_message_text(f"{call.message.text}\n\n❌ تم الرفض وإعادة الرصيد", MY_ID, call.message.message_id)

# --- 5. خدمات إضافية ---
@bot.message_handler(func=lambda m: m.text == "🔙 العودة للرئيسية")
def back_to_start(message):
    start(message)

@bot.message_handler(func=lambda m: m.text == "👤 ملفي الشخصي")
def profile(message):
    bal = user_balances.get(message.chat.id, 0)
    bot.send_message(message.chat.id, f"👤 **ملفك الشخصي:**\n\n🆔 المعرف الخاص بك: `{message.chat.id}`\n💳 رصيدك الحالي: {bal:,} SYP\n\nنحن نسعد بخدمتك دائماً! 🌸", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📜 سجل طلباتي")
def history(message):
    uid = message.chat.id
    orders = user_orders.get(uid, [])
    if not orders:
        bot.send_message(uid, "سجل طلباتك فارغ حالياً. ابدأ التسوق الآن! 😉")
        return
    msg = "📜 **تاريخ طلباتك الأخيرة:**\n\n"
    for o in orders[-5:]:
        msg += f"📦 {o['item']}\n💰 {o['price']:,} SYP\n📅 {o['date']}\nالحالة: {o['status']}\n\n"
    bot.send_message(uid, msg)

bot.infinity_polling(skip_pending=True)

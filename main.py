import telebot
from telebot import types

# --- الإعدادات ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 7557584016  # الآيدي المطور الخاص بك من الصورة
CHANNEL_ID = "@YourChannelUsername" # قم بتغيير هذا إلى يوزر قناتك (مثال: @VantomCard)
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

user_balances = {}

# --- دالة التحقق من الاشتراك في القناة ---
def is_subscribed(uid):
    try:
        status = bot.get_chat_member(CHANNEL_ID, uid).status
        return status in ['member', 'administrator', 'creator']
    except:
        return True # في حال وجود خطأ تقني لا يعطل الزبائن

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    # التحقق من الاشتراك أولاً
    if not is_subscribed(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📢 انضم للقناة الرسمية", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
        bot.send_message(uid, f"عذراً يا صديقي، لضمان استمرارية الخدمة يرجى الانضمام لقناة متجر **Game Card Store** أولاً ثم أرسل /start مجدداً! ✨", reply_markup=mk)
        return

    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن الرصيد", "👤 ملفي الشخصي")
    mk.add("📜 سجل طلباتي", "📢 قناة المتجر") # أضفنا زر القناة
    
    welcome = f"يا أهلاً بك في متجر Game Card Store! ✨\nتم التحقق من عضويتك بنجاح.. تفضل بالاختيار: 👇"
    bot.send_message(uid, welcome, reply_markup=mk)

# --- التعامل مع زر القناة ---
@bot.message_handler(func=lambda m: m.text == "📢 قناة المتجر")
def show_channel(message):
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("🔗 اضغط هنا للدخول للقناة", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
    bot.send_message(message.chat.id, "تابع قناتنا الرسمية لتعرف أحدث الأسعار والعروض اليومية! 🚀", reply_markup=mk)

# (بقية الكود الخاص بالألعاب والشحن يبقى كما هو في النسخة السابقة)
bot.infinity_polling(skip_pending=True)

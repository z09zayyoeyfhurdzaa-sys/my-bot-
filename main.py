import telebot
from telebot import types

# --- الإعدادات النهائية المعتمدة ---
TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 7557584016  # آيدي المطور أحمد عيسى
CHANNEL_ID = "@Game1stor"  # يوزر القناة من الصورة الأخيرة

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)

# ذاكرة الأرصدة المؤقتة
user_balances = {} 

# دالة فحص الاشتراك الإجباري
def check_sub(uid):
    try:
        member = bot.get_chat_member(CHANNEL_ID, uid)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        # في حال لم يتم إضافة البوت كمسؤول بعد، سيسمح بالدخول مؤقتاً
        return True 

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    
    # التحقق من الاشتراك في قناة @Game1stor
    if not check_sub(uid):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📢 انضم للقناة الرسمية", url=f"https://t.me/Game1stor"))
        bot.send_message(uid, "يا أهلاً بك! لضمان عمل الخدمة، يرجى الاشتراك في قناة المتجر أولاً، ثم أرسل /start مجدداً! ✨", reply_markup=mk)
        return

    # القائمة الرئيسية الاحترافية
    mk = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mk.add("🎮 تسوق الألعاب", "📱 قسم التطبيقات")
    mk.add("💰 شحن الرصيد", "👤 ملفي الشخصي")
    mk.add("📜 سجل طلباتي", "📢 قناة المتجر")
    
    welcome = f"مرحباً بك في Game Card Store! 🚀\nيسعدنا خدمتك يا {message.from_user.first_name}. تفضل بالاختيار:"
    bot.send_message(uid, welcome, reply_markup=mk)

# (بقية الكود الخاص بالألعاب والشراء يبقى كما هو)

bot.infinity_polling(skip_pending=True)

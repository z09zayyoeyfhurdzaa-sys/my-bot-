import telebot
from telebot import types

TOKEN = '8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU'
MY_ID = 1767254345  
CASH_NUMBER = "0994601295" 

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)
user_balances = {} 

# --- خاص للمسؤول: شحن رصيد يدوي ---
# أرسل رسالة للبوت: شحن 123456 50000 (الآيدي ثم المبلغ)
@bot.message_handler(func=lambda m: m.chat.id == MY_ID and m.text.startswith("شحن"))
def manual_recharge(message):
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        amount = int(parts[2])
        user_balances[target_id] = user_balances.get(target_id, 0) + amount
        bot.send_message(MY_ID, f"✅ تمت إضافة {amount:,} SYP للحساب {target_id}")
        bot.send_message(target_id, f"✅ تم شحن رصيدك بمبلغ {amount:,} SYP بنجاح!")
    except:
        bot.send_message(MY_ID, "❌ خطأ! الصيغة: شحن [الآيدي] [المبلغ]")

# --- طلب شحن الرصيد من الزبون ---
@bot.message_handler(func=lambda m: m.text == "💰 شحن الرصيد")
def recharge_req(message):
    msg = bot.send_message(message.chat.id, f"🚀 للتحويل: استخدم الرقم `{CASH_NUMBER}`\nبعد التحويل، أرسل ("المبلغ+رقم عمليه التحويل" كل منها على حدا) هنا 👇")
    bot.register_next_step_handler(msg, notify_admin_payment)

def notify_admin_payment(message):
    uid = message.chat.id
    name = message.from_user.first_name
    
    # أزرار الموافقة والرفض التي لم تظهر سابقاً
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ موافقة", callback_data=f"ok_{uid}"),
           types.InlineKeyboardButton("❌ رفض", callback_data=f"no_{uid}"))
    
    bot.send_message(MY_ID, f"🔔 طلب شحن جديد:\n👤 الاسم: {name}\n🆔 الآيدي: `{uid}`\n📝 التفاصيل: {message.text}", reply_markup=mk)
    bot.send_message(uid, "⏳ تم إرسال طلبك للإدارة. ستصلك رسالة فور تأكيد العملية.")

@bot.callback_query_handler(func=lambda c: c.data.startswith(("ok_", "no_")))
def admin_approval(call):
    uid = int(call.data.split("_")[1])
    if "ok" in call.data:
        msg = bot.send_message(MY_ID, f"🔢 أدخل المبلغ المراد إضافته للحساب {uid}:")
        bot.register_next_step_handler(msg, finalize_recharge, uid)
    else:
        bot.send_message(uid, "❌ نعتذر، تم رفض طلب الشحن الخاص بك.")

def finalize_recharge(message, uid):
    try:
        amt = int(message.text)
        user_balances[uid] = user_balances.get(uid, 0) + amt
        bot.send_message(uid, f"✅ مبروك! تمت إضافة {amt:,} SYP لرصيدك.")
        bot.send_message(MY_ID, "✅ تم تحديث الرصيد بنجاح.")
    except:
        bot.send_message(MY_ID, "⚠️ خطأ! أرسل أرقام فقط.")

bot.infinity_polling(skip_pending=True)

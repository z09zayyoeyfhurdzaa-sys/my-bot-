import telebot
from telebot import types
import os

# ===== الإعدادات الآمنة =====
TOKEN = "8372753026:AAG7SJLu_FkLrz-MzPJXNNE4D_5hyemyLlU"
ADMIN_ID = 7557584016
CASH = "0994601295"
RATE = 15000

# استخدام threaded=False يحسن الاستقرار على السيرفرات المجانية
bot = telebot.TeleBot(TOKEN, threaded=False)

balances = {}
user_steps = {}

GAMES = {
    "🔫 شدات ببجي": {"60 UC": 1, "325 UC": 5, "660 UC": 10},
    "💎 جواهر فري فاير": {"100 💎": 1, "210 💎": 2, "530 💎": 5}
}

# --- لوحة التحكم ---
def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🎮 الألعاب", callback_data="games"),
           types.InlineKeyboardButton("💰 شحن رصيد", callback_data="recharge"),
           types.InlineKeyboardButton("👤 حسابي", callback_data="profile"))
    return kb

@bot.message_handler(commands=["start"])
def start(msg):
    balances.setdefault(msg.chat.id, 0)
    bot.send_message(msg.chat.id, "🚀 **مرحباً بك في المتجر الشغال بنجاح!**", 
                     reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: True)
def callbacks(call):
    uid = call.message.chat.id
    if call.data == "games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES: kb.add(types.InlineKeyboardButton(g, callback_data=f"game:{g}"))
        bot.edit_message_text("🎮 اختر اللعبة:", uid, call.message.message_id, reply_markup=kb)
    
    elif call.data.startswith("game:"):
        game = call.data.split(":")[1]
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game].items():
            kb.add(types.InlineKeyboardButton(f"{p} • {u*RATE:,} SYP", callback_data=f"buy:{game}:{p}:{u*RATE}"))
        bot.edit_message_text(f"🛒 {game}:", uid, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("buy:"):
        _, g, p, pr = call.data.split(":")
        if balances.get(uid, 0) < int(pr):
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"g": g, "p": p, "pr": int(pr)}
            bot.send_message(uid, "🆔 أرسل ID اللاعب الآن:")

    elif call.data == "recharge":
        user_steps[uid] = "recharge"
        bot.send_message(uid, f"💳 رقم التحويل: `{CASH}`\nأرسل صورة أو تفاصيل التحويل:")

    elif call.data.startswith("adm_ok:"):
        target = int(call.data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ لـ {target}:")
        bot.register_next_step_handler(msg, finalize_add, target)

def finalize_add(message, target):
    try:
        amt = int(message.text)
        balances[target] = balances.get(target, 0) + amt
        bot.send_message(target, f"✅ تم شحن حسابك بـ {amt:,} SYP")
        bot.send_message(ADMIN_ID, "✅ تم.")
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ في القيمة.")

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_all(msg):
    uid = msg.chat.id
    if uid not in user_steps: return
    
    step = user_steps.pop(uid)
    if isinstance(step, dict): # شراء
        balances[uid] -= step['pr']
        bot.send_message(ADMIN_ID, f"🛒 طلب جديد:\n👤 {uid}\n📦 {step['g']}\n🆔 `{msg.text}`")
        bot.send_message(uid, "⏳ تم استلام طلبك.")
    elif step == "recharge":
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ شحن الرصيد", callback_data=f"adm_ok:{uid}"))
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 طلب شحن من {uid}", reply_markup=kb)
        bot.send_message(uid, "✅ تم الإرسال.")

# لضمان عدم توقف البوت على الاستضافات السحابية
if __name__ == "__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

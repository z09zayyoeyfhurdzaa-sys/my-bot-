# عند الضغط على سيريتل
elif data == "open_syriatel":
    user_steps[uid] = {"step": "syriatel_number"}  # بداية الطلب
    bot.send_message(uid, "🇸🇾 أرسل رقم السيريتل الخاص بك:", reply_markup=back_kb())

# عند استقبال الرسائل
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo'])
def handle_steps(msg):
    uid = msg.chat.id
    if uid not in user_steps: return

    step = user_steps[uid]

    # --- شراء منتج ---
    if isinstance(step, dict) and step.get("item"):
        user_steps.pop(uid)
        balances[uid] -= step['price']
        bot.send_message(ADMIN_ID, f"🛒 **طلب شراء جديد**\n👤 المستخدم: `{uid}`\n📦 المنتج: {step['item']}\n🆔 المعرف المرسل: `{msg.text}`", parse_mode="Markdown")
        bot.send_message(uid, "⏳ تم استلام بياناتك، سيتم التنفيذ فوراً.", reply_markup=main_kb())

    # --- سيريتل كاش خطوة خطوة ---
    elif step.get("step") == "syriatel_number":
        step["number"] = msg.text
        step["step"] = "syriatel_amount"
        user_steps[uid] = step
        bot.send_message(uid, "💰 الآن أرسل المبلغ الذي تريد تحويله:", reply_markup=back_kb())

    elif step.get("step") == "syriatel_amount":
        try:
            amount = int(msg.text)
            number = step.get("number")
            # إرسال للإدارة
            bot.send_message(ADMIN_ID, f"🇸🇾 **طلب سيريتل كاش جديد**\n👤 المستخدم: `{uid}`\n📱 الرقم: `{number}`\n💰 المبلغ: {amount:,} SYP", parse_mode="Markdown")
            bot.send_message(uid, "✅ تم إرسال الطلب للإدارة.", reply_markup=main_kb())
            user_steps.pop(uid)  # إنهاء الطلب
        except:
            bot.send_message(uid, "❌ المبلغ غير صحيح، أرسل رقم فقط.", reply_markup=back_kb())

    # --- إثبات شحن للكاش ---
    elif step.get("step") == "step_recharge":
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ قبول", callback_data=f"adm_ok:{uid}"),
            types.InlineKeyboardButton("❌ رفض", callback_data=f"adm_no:{uid}")
        )
        bot.forward_message(ADMIN_ID, uid, msg.message_id)
        bot.send_message(ADMIN_ID, f"🔔 **طلب شحن جديد**\n👤 آيدي المستخدم: `{uid}`", reply_markup=kb, parse_mode="Markdown")
        bot.send_message(uid, "✅ تم إرسال الإثبات، انتظر التفعيل.", reply_markup=main_kb())

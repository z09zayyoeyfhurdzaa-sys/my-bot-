@bot.callback_query_handler(func=lambda c: True)
def handle_all_callbacks(call):
    uid = call.message.chat.id
    data = call.data

    # 1. القوائم الرئيسية
    if data == "open_games":
        kb = types.InlineKeyboardMarkup()
        for g in GAMES:
            kb.add(types.InlineKeyboardButton(g, callback_data=f"select_game:{g.replace(':','|')}"))
        bot.edit_message_text("🕹️ اختر اللعبة:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data == "open_apps":
        kb = types.InlineKeyboardMarkup()
        for a, u in APPS.items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{a} • {price:,} SYP", callback_data=f"buy_item:{a.replace(':','|')}:{price}"))
        bot.edit_message_text("📱 اختر التطبيق:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    elif data == "open_syriatel":
        user_steps[uid] = "step_syriatel"
        bot.send_message(uid, "🇸🇾 أرسل رقم السيريتل والمبلغ المراد تحويله:", reply_markup=back_kb())

    elif data == "open_recharge":
        user_steps[uid] = "step_recharge"
        bot.send_message(uid, f"💰 رقم الكاش: `{settings['cash_num']}`\nأرسل صورة أو تفاصيل التحويل:", reply_markup=back_kb())

    elif data == "open_profile":
        bot.answer_callback_query(call.id, f"💰 رصيدك: {balances.get(uid, 0):,} SYP", show_alert=True)

    # 2. اختيار الباقات
    elif data.startswith("select_game:"):
        game_name = data.split(":", 1)[1].replace("|", ":")
        kb = types.InlineKeyboardMarkup()
        for p, u in GAMES[game_name].items():
            price = int(u * settings["rate"])
            kb.add(types.InlineKeyboardButton(f"{p} • {price:,} SYP", callback_data=f"buy_item:{p.replace(':','|')}:{price}"))
        bot.edit_message_text(f"عروض {game_name}:", chat_id=uid, message_id=call.message.message_id, reply_markup=kb)

    # 3. عملية الشراء
    elif data.startswith("buy_item:"):
        _, item, price = data.split(":", 2)
        item = item.replace("|", ":")
        price = int(price)
        if balances.get(uid, 0) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك لا يكفي", show_alert=True)
        else:
            user_steps[uid] = {"item": item, "price": price}
            bot.send_message(uid, f"🛒 طلب {item}\nأرسل ID اللاعب أو الرقم الآن:", reply_markup=back_kb())

    # 4. أزرار الإدارة
    elif data.startswith("adm_ok:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, f"أدخل المبلغ لإضافته للحساب {target}:")
        bot.register_next_step_handler(msg, finalize_add, target)

    elif data.startswith("adm_no:"):
        target = int(data.split(":")[1])
        msg = bot.send_message(ADMIN_ID, "أرسل سبب الرفض:")
        bot.register_next_step_handler(msg, finalize_reject, target)

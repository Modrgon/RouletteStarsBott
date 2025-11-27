# handlers/booster/activate.py

from loader import bot
from telebot import types
from database import get_booster, get_boosters, get_user, update_stars, activate_booster

# تفعيل Booster من قائمة
@bot.message_handler(commands=['activate_booster'])
def activate_booster_cmd(message):
    chat_id = message.chat.id
    boosters = get_boosters()

    if not boosters:
        bot.send_message(chat_id, "❌ لا يوجد أي Booster متاح حاليًا.")
        return

    keyboard = types.InlineKeyboardMarkup()
    for booster in boosters:
        keyboard.add(types.InlineKeyboardButton(
            text=f"{booster.get('name','Booster')} - {booster.get('price',0)} نجوم",
            callback_data=f"activate_{booster.get('_id')}"
        ))

    bot.send_message(chat_id, "🎯 اختر Booster لتفعيله:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('activate_'))
def activate_booster_callback(call):
    booster_id = call.data.split('_')[-1]
    chat_id = call.message.chat.id

    booster = get_booster(booster_id)
    if not booster:
        bot.send_message(chat_id, "❌ هذا الـ Booster غير موجود.")
        return

    duration = booster.get('duration_hours', 24)
    activate_booster(chat_id, duration_hours=duration)
    bot.send_message(chat_id, f"✅ تم تفعيل Booster: {booster.get('name')} لمدة {duration} ساعة!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_booster_'))
def buy_booster(call):
    booster_id = call.data.split('_')[-1]
    chat_id = call.message.chat.id

    booster = get_booster(booster_id)
    if not booster:
        bot.send_message(chat_id, "❌ هذا الـ Booster غير موجود.")
        return

    user = get_user(chat_id)
    if user['stars'] < booster.get('price', 0):
        bot.send_message(chat_id, f"❌ ليس لديك ما يكفي من النجوم لشراء {booster.get('name')}!\nالمطلوب: {booster.get('price',0)} نجوم، لديك: {user['stars']} نجمة.")
        return

    update_stars(chat_id, -booster.get('price', 0))
    duration = booster.get('duration_hours', 24)
    activate_booster(chat_id, duration_hours=duration)

    bot.send_message(chat_id, f"✅ تم شراء وتفعيل Booster: {booster.get('name')} لمدة {duration} ساعة!\nتم خصم {booster.get('price',0)} نجوم من حسابك.")
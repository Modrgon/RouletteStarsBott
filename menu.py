# handlers/booster/menu.py

from loader import bot
from telebot import types
from database import get_boosters

@bot.message_handler(commands=['booster_menu'])
def booster_menu(message):
    chat_id = message.chat.id
    boosters = get_boosters()

    if not boosters:
        bot.send_message(chat_id, "❌ لا يوجد أي Booster متاح حالياً.")
        return

    keyboard = types.InlineKeyboardMarkup()
    for booster in boosters:
        keyboard.add(types.InlineKeyboardButton(
            text=f"{booster.get('name','Booster')} - {booster.get('price',0)} نجوم",
            callback_data=f"buy_booster_{booster.get('_id')}"
        ))

    bot.send_message(chat_id, "🎁 قائمة الـ Boosters المتاحة:", reply_markup=keyboard)
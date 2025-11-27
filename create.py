# handlers/booster/create.py

from loader import bot
from telebot import types
from database import create_booster

@bot.message_handler(commands=['create_booster'])
def create_booster_cmd(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "🎉 أهلاً بك في إنشاء Booster جديد!\nأرسل اسم الـ Booster:")
    bot.register_next_step_handler(message, receive_booster_name)

def receive_booster_name(message):
    chat_id = message.chat.id
    booster_name = message.text.strip()

    if not booster_name:
        bot.send_message(chat_id, "❌ الاسم فارغ، حاول مرة أخرى:")
        bot.register_next_step_handler(message, receive_booster_name)
        return

    bot_data = {
        "name": booster_name,
        "level": 1,
        "price": 0
    }

    bot.send_message(chat_id, f"✅ تم إنشاء Booster باسم: {booster_name}\nأرسل سعر الـ Booster بالنجوم:")
    bot.register_next_step_handler(message, receive_booster_price, bot_data)

def receive_booster_price(message, bot_data):
    chat_id = message.chat.id
    try:
        price = int(message.text.strip())
        bot_data['price'] = price
        bot.send_message(chat_id, "⏱ الآن أرسل مدة التفعيل بالساعة (مثلاً 24):")
        bot.register_next_step_handler(message, receive_booster_duration, bot_data)
    except ValueError:
        bot.send_message(chat_id, "❌ يجب أن يكون السعر رقم صحيح، أرسل السعر مرة أخرى:")
        bot.register_next_step_handler(message, receive_booster_price, bot_data)

def receive_booster_duration(message, bot_data):
    chat_id = message.chat.id
    try:
        duration = int(message.text.strip())
        bot_data['duration_hours'] = duration
        booster_id = create_booster(bot_data['name'], bot_data['level'], bot_data['price'], bot_data['duration_hours'])
        bot.send_message(chat_id, f"🎉 تم إنشاء Booster بنجاح! (ID: {booster_id}) لمدة {duration} ساعة.")
    except ValueError:
        bot.send_message(chat_id, "❌ يجب أن تكون المدة رقم صحيح بالساعة، أرسل مرة أخرى:")
        bot.register_next_step_handler(message, receive_booster_duration, bot_data)
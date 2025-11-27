# handlers/gift/join.py

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from database import get_gift_box, get_user, update_stars, add_participant_to_box
from handlers.gift.publish import format_conditions

@bot.callback_query_handler(func=lambda c: c.data.startswith("join_box_"))
def join_gift_box(call):
    user_id = call.from_user.id
    box_id = call.data.split("_", 2)[2]

    box = get_gift_box(box_id)
    if not box:
        return bot.answer_callback_query(call.id, "❌ الصندوق غير موجود!", show_alert=True)

    price = box.get("price", 0)
    participants = box.get("participants", [])
    channels = box.get("cond_channels", [])

    # ----------------------------------------
    # 1️⃣ التحقق من قنوات الشرط
    # ----------------------------------------
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                kb = InlineKeyboardMarkup()
                kb.add(InlineKeyboardButton("🔁 اشترك ثم اضغط هنا", callback_data=f"join_box_{box_id}"))
                return bot.send_message(user_id, f"❌ لازم تشترك في:\n{ch}", reply_markup=kb)
        except Exception:
            return bot.send_message(user_id, f"⚠️ في مشكلة في قناة الشرط:\n{ch}")

    # ----------------------------------------
    # 2️⃣ التأكد من الرصيد
    # ----------------------------------------
    user = get_user(user_id)
    if user["stars"] < price:
        return bot.answer_callback_query(call.id, "❌ ممعكش نجوم كفاية!", show_alert=True)

    # خصم النجوم
    update_stars(user_id, -price)

    # ----------------------------------------
    # 3️⃣ إضافة المستخدم للمشاركين
    # ----------------------------------------
    add_participant_to_box(box_id, user_id)

    bot.answer_callback_query(call.id, "🎉 دخلت السحب!", show_alert=True)
    bot.send_message(user_id, "🎉 تم انضمامك لصندوق الهدايا بنجاح!")
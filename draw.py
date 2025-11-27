# handlers/gift/draw.py

import random
from loader import bot
from database import get_gift_box, set_box_winners_and_close, update_stars, mark_box_claimed
from config import OWNER_ID
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@bot.callback_query_handler(func=lambda c: c.data.startswith("drawbox_"))
def draw_gift_box(call):
    user_id = call.from_user.id
    box_id = call.data.split("_")[1]

    box = get_gift_box(box_id)
    if not box:
        return bot.answer_callback_query(call.id, "❌ الصندوق غير موجود!", show_alert=True)

    # حماية — محدش ينفذ السحب غير صاحب الصندوق
    if box.get("owner_id") != user_id:
        return bot.answer_callback_query(call.id, "❌ السحب دا مش بتاعك!", show_alert=True)

    participants = box.get("participants", [])
    max_winners = box.get("max_winners", 1)
    package = box.get("pack_value", 0)

    if len(participants) < max_winners:
        return bot.answer_callback_query(call.id, "⚠️ عدد المشتركين أقل من عدد الفائزين!", show_alert=True)

    winners = random.sample(participants, max_winners)

    # توزيع النجوم على الفائزين
    for win in winners:
        update_stars(win, package)

    # تحويل عمولة للصاحب (مثال: عمولة ثابتة)
    # هنا استخدمت OWNER_ID من config
    owner_commission = 20 if package <= 100 else 10
    try:
        update_stars(OWNER_ID, owner_commission)
    except Exception:
        pass

    set_box_winners_and_close(box_id, winners)

    result = "🎁 **نتيجة سحب صندوق الهدايا:**\n\n"
    for w in winners:
        result += f"🏆 فائز: [{w}](tg://user?id={w}) — حصل على {package} ⭐\n"

    bot.send_message(call.message.chat.id, result, parse_mode="Markdown")
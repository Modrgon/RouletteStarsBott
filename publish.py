# handlers/gift/publish.py

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from database import get_gift_box
from config import DRAW_CHANNEL

def format_conditions(cond_list):
    if not cond_list:
        return "لا يوجد شروط.\n"

    txt = ""
    for ch in cond_list:
        txt += f"- {ch}\n"
    return txt

def publish_gift_box(box_id):
    box = get_gift_box(box_id)
    if not box:
        return

    title = box.get("title", "صندوق هدايا")
    price = box.get("price", 0)
    package = box.get("pack_value", 0)
    channels = box.get("cond_channels", [])

    text = f"""
🎁 **صندوق هدايا جديد!**

📌 **العنوان:** {title}
💎 **الباقة:** {package} نجمة
💰 **سعر الاشتراك:** {'مجاني' if price == 0 else str(price) + ' نجمة'}

📢 **قنوات الشرط:**
{format_conditions(channels)}

اضغط الزر للانضمام للسحب 👇
"""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎫 ادخل السحب", callback_data=f"join_box_{box_id}"))
    kb.add(InlineKeyboardButton("ℹ️ معلومات", callback_data=f"boxinfo_{box_id}"))
    kb.add(InlineKeyboardButton("🔃 نفّذ السحب (لصاحب الصندوق)", callback_data=f"drawbox_{box_id}"))

    try:
        bot.send_message(
            chat_id=DRAW_CHANNEL,
            text=text,
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception:
        # إما القناة غير صحيحة أو البوت ليس مشرفًا — نتخطى الخطأ
        return
# handlers/gift/create.py

from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from config import DRAW_CHANNEL
from database import create_gift_box, get_gift_box
from bson import ObjectId

# Fixed gift packages
GIFT_PACKS = [50, 100, 150, 200]

@bot.callback_query_handler(func=lambda c: c.data == "create_giftbox")
def _start_create_box(call: CallbackQuery):
    bot.edit_message_text(
        "🎁 *إنشاء صندوق هدايا جديد*\n\n"
        "أرسل *عنوان* الصندوق الآن (مثال: مفاجأة 50 نجمة).",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(call.message, _get_box_title)

def _get_box_title(message: Message):
    title = message.text.strip()
    if not title:
        bot.send_message(message.chat.id, "❌ اكتب عنوان صحيح للصندوق.")
        return bot.register_next_step_handler(message, _get_box_title)

    kb = InlineKeyboardMarkup()
    for p in GIFT_PACKS:
        kb.add(InlineKeyboardButton(f"{p} نجمة", callback_data=f"giftpack_{p}"))
    kb.add(InlineKeyboardButton("إلغاء", callback_data="back_home"))

    sent = bot.send_message(message.chat.id, "اختر قيمة الجائزة من الباقات التالية:", reply_markup=kb)
    # سنحتفظ بالعنوان في رسالة مؤقتة: سنطلب السعر بعد اختيار الباقة
    bot.register_next_step_handler(sent, lambda msg: _pack_error(msg, title))

def _pack_error(message: Message, title: str):
    bot.send_message(message.chat.id, "❌ يرجى اختيار الباقة عبر الأزرار.")
    bot.register_next_step_handler(message, lambda msg: _get_box_title(msg))

@bot.callback_query_handler(func=lambda c: c.data.startswith("giftpack_"))
def _pack_selected(call: CallbackQuery):
    try:
        pack = int(call.data.split("_", 1)[1])
    except:
        return bot.answer_callback_query(call.id, "❌ خطأ في اختيار الباقة.")
    bot.edit_message_text("📝 الآن ارسل *سعر الاشتراك* الذي سيرسله المتسابق (اكتب 0 للانضمام المجاني).",
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.register_next_step_handler(call.message, lambda msg: _get_price(msg, pack, call.message))

def _get_price(message: Message, pack: int, prev_message):
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ السعر لازم يكون رقم (0 أو أكبر). حاول تاني.")
        return bot.register_next_step_handler(message, lambda msg: _get_price(msg, pack, prev_message))

    bot.send_message(message.chat.id, "👥 اكتب عدد الفائزين للصندوق (مثال: 1 أو 3):")
    bot.register_next_step_handler(message, lambda msg: _get_winners(msg, pack, price))

def _get_winners(message: Message, pack: int, price: int):
    try:
        winners = int(message.text.strip())
        if winners <= 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ لازم تكتب رقم صحيح لعدد الفائزين.")
        return bot.register_next_step_handler(message, lambda msg: _get_winners(msg, pack, price))

    bot.send_message(
        message.chat.id,
        "📢 هل تريد إضافة قنوات شرط للصندوق؟ (قناة أو قناتين)\nاكتب: نعم أو لا"
    )
    bot.register_next_step_handler(message, lambda msg: _ask_cond_channels(msg, pack, price, winners))

def _ask_cond_channels(message: Message, pack: int, price: int, winners: int):
    txt = message.text.strip().lower()
    if txt in ["لا", "no", "0"]:
        return _finish_create_box(message, pack, price, winners, [])
    if txt in ["نعم", "yes", "اوك", "ايوه", "أيوه", "اه"]:
        bot.send_message(message.chat.id, "📡 أرسل رابط قناة الشرط الأولى (مثال t.me/channel):")
        bot.register_next_step_handler(message, lambda msg: _get_cond1(msg, pack, price, winners))
        return
    bot.send_message(message.chat.id, "❌ اكتب فقط نعم أو لا.")
    bot.register_next_step_handler(message, lambda msg: _ask_cond_channels(msg, pack, price, winners))

def _get_cond1(message: Message, pack: int, price: int, winners: int):
    link1 = message.text.strip()
    if "t.me" not in link1 and not link1.startswith("http"):
        bot.send_message(message.chat.id, "❌ رابط غير صالح. تم إلغاء إضافة قنوات الشرط.")
        return _finish_create_box(message, pack, price, winners, [])

    bot.send_message(message.chat.id, "📢 هل تريد إضافة قناة شرط ثانية؟ اكتب نعم أو لا")
    bot.register_next_step_handler(message, lambda msg: _maybe_cond2(msg, pack, price, winners, link1))

def _maybe_cond2(message: Message, pack: int, price: int, winners: int, link1: str):
    a = message.text.strip().lower()
    if a in ["لا", "no", "0"]:
        return _finish_create_box(message, pack, price, winners, [link1])
    bot.send_message(message.chat.id, "📡 أرسل رابط قناة الشرط الثانية:")
    bot.register_next_step_handler(message, lambda msg: _get_cond2(msg, pack, price, winners, link1))

def _get_cond2(message: Message, pack: int, price: int, winners: int, link1: str):
    link2 = message.text.strip()
    if "t.me" not in link2 and not link2.startswith("http"):
        bot.send_message(message.chat.id, "❌ رابط غير صالح. سيتم حفظ القناة الأولى فقط.")
        return _finish_create_box(message, pack, price, winners, [link1])
    return _finish_create_box(message, pack, price, winners, [link1, link2])

def _finish_create_box(message: Message, pack: int, price: int, winners: int, cond_channels: list):
    owner = message.from_user.id
    title = f"{pack} نجمة - {winners} فائز(ين)"
    inserted_id = create_gift_box(owner, title, pack, price, winners, cond_channels)

    bot.send_message(message.chat.id,
                     f"✅ تم إنشاء صندوق الهدايا!\n📌 {title}\n💰 سعر الاشتراك: {price}\n🏆 الفائزين: {winners}")

    # try to publish automatically
    try:
        from handlers.gift.publish import publish_gift_box
        publish_gift_box(inserted_id)
    except Exception:
        pass
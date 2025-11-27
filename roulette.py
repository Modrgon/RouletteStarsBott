# handlers/roulette.py
# منظم: create / conditions / publish / join / draw / info
# تذكير: هذا الملف يفترض وجود الدوال التالية في database.py:
# create_roulette(owner_id, title, price, max_winners, cond_channels) -> returns inserted_id (string)
# get_roulette(rid) -> returns roulette doc
# update_roulette(rid, new_data: dict)
# join_roulette(rid, user_id)
# update_stars(user_id, amount)
# get_user(user_id)

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import CallbackQuery, Message
from main import bot
from config import DRAW_CHANNEL, OWNER_ID
from database import (
    create_roulette,
    get_roulette,
    update_roulette,
    join_roulette,
    update_stars,
    get_user,
    roulettes
)
import random

# ---------------------------
# Registraton entrypoint
# ---------------------------
def register_handlers_roulette():
    """
    Call this from main (once) to register roulette handlers.
    """
    # menu opener
    @bot.callback_query_handler(func=lambda c: c.data == "roulette_menu")
    def _open_roulette_menu(call: CallbackQuery):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🎯 إنشاء روليت جديدة", callback_data="create_roulette"))
        kb.add(InlineKeyboardButton("📋 روليتاتي", callback_data="my_roulettes"))
        kb.add(InlineKeyboardButton("⬅️ رجوع", callback_data="back_home"))
        bot.edit_message_text(
            "🎰 *قسم الروليت*\nاختر ما تريد:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kb,
            parse_mode="Markdown"
        )

    # start creation
    @bot.callback_query_handler(func=lambda c: c.data == "create_roulette")
    def _create_roulette_step1(call: CallbackQuery):
        bot.edit_message_text(
            "📌 أرسل *عنوان الروليت* الآن:",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, _get_roulette_title)


# ---------------------------
# Create flow helpers
# ---------------------------
def _get_roulette_title(message: Message):
    title = message.text.strip()
    if not title:
        bot.send_message(message.chat.id, "❌ اكتب عنوان صحيح.")
        return bot.register_next_step_handler(message, _get_roulette_title)

    bot.send_message(message.chat.id, "💰 أرسل *سعر الاشتراك بالنجوم* (اكتب 0 لو مجاني):", parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: _get_roulette_price(msg, title))


def _get_roulette_price(message: Message, title: str):
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ السعر لازم يكون رقم صحيح. حاول تاني.")
        return bot.register_next_step_handler(message, lambda msg: _get_roulette_price(msg, title))

    bot.send_message(message.chat.id, "👥 أرسل *عدد الفائزين* (مثال: 1 أو 3):", parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: _get_roulette_winners(msg, title, price))


def _get_roulette_winners(message: Message, title: str, price: int):
    try:
        max_winners = int(message.text.strip())
        if max_winners <= 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ لازم تكتب رقم صحيح للفائزين")
        return bot.register_next_step_handler(message, lambda msg: _get_roulette_winners(msg, title, price))

    # ask for condition channels
    bot.send_message(
        message.chat.id,
        "📢 هل تريد إضافة قنوات شرط للسحب؟\n(يمكنك إضافة قناة واحدة أو اثنتين)\nاكتب: نعم أو لا",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, lambda msg: _ask_condition_channels(msg, title, price, max_winners))


def _ask_condition_channels(message: Message, title: str, price: int, max_winners: int):
    txt = message.text.strip().lower()
    if txt in ["لا", "no", "0"]:
        _finish_roulette(message, title, price, max_winners, [])
        return
    if txt in ["نعم", "yes", "اه", "أيوه", "ايوه"]:
        bot.send_message(message.chat.id, "📡 أرسل رابط قناة الشرط الأولى (مثال t.me/channel):")
        bot.register_next_step_handler(message, lambda msg: _get_first_condition(msg, title, price, max_winners))
        return
    bot.send_message(message.chat.id, "❌ اكتب فقط نعم أو لا.")
    bot.register_next_step_handler(message, lambda msg: _ask_condition_channels(msg, title, price, max_winners))


def _get_first_condition(message: Message, title: str, price: int, max_winners: int):
    link1 = message.text.strip()
    if "t.me" not in link1 and not link1.startswith("http"):
        bot.send_message(message.chat.id, "❌ رابط غير صالح. حاول مرة أخرى.")
        return bot.register_next_step_handler(message, lambda msg: _get_first_condition(msg, title, price, max_winners))
    # ask if second
    bot.send_message(message.chat.id, "📢 هل تريد إضافة قناة شرط ثانية؟ اكتب نعم أو لا")
    bot.register_next_step_handler(message, lambda msg: _handle_second_cond_answer(msg, title, price, max_winners, link1))


def _handle_second_cond_answer(message: Message, title: str, price: int, max_winners: int, link1: str):
    a = message.text.strip().lower()
    if a in ["لا", "no", "0"]:
        _finish_roulette(message, title, price, max_winners, [link1])
        return
    # expect second link
    bot.send_message(message.chat.id, "📡 أرسل رابط قناة الشرط الثانية:")
    bot.register_next_step_handler(message, lambda msg: _get_second_condition(msg, title, price, max_winners, link1))


def _get_second_condition(message: Message, title: str, price: int, max_winners: int, link1: str):
    link2 = message.text.strip()
    if "t.me" not in link2 and not link2.startswith("http"):
        bot.send_message(message.chat.id, "❌ رابط غير صالح. تم إلغاء إضافة القناة الثانية.")
        return _finish_roulette(message, title, price, max_winners, [link1])
    _finish_roulette(message, title, price, max_winners, [link1, link2])


def _finish_roulette(message: Message, title: str, price: int, max_winners: int, cond_channels: list):
    """
    Create DB doc, then publish the roulette post.
    """
    owner_id = message.from_user.id
    # create in DB (create_roulette should return inserted id string)
    inserted_id = create_roulette(
        owner_id=owner_id,
        title=title,
        price=price,
        max_winners=max_winners,
        cond_channels=cond_channels
    )
    # create_roulette in your database.py returns inserted id as string (ensure that)
    bot.send_message(
        message.chat.id,
        f"✅ تم إنشاء الروليت بنجاح!\n📌 {title}\n💰 السعر: {price} نجمة\n🏆 الفائزين: {max_winners}"
    )

    try:
        # publish to channel (if DRAW_CHANNEL defined)
        publish_roulette(inserted_id)
    except Exception as e:
        # don't crash the flow if publish fails; inform owner
        bot.send_message(owner_id, f"⚠️ فشل نشر الروليت تلقائيًا: {e}")


# ---------------------------
# Conditions utilities & admin cmd to set conditions separately
# ---------------------------
@bot.message_handler(commands=['add_cond'])
def _cmd_add_cond(message: Message):
    # This command sets condition channels for the latest roulette of the user.
    bot.send_message(message.chat.id, "📢 أرسل رابط قناة الشرط الأولى:")
    bot.register_next_step_handler(message, _save_cond_first)


def _save_cond_first(message: Message):
    link1 = message.text.strip()
    if "t.me" not in link1 and not link1.startswith("http"):
        return bot.send_message(message.chat.id, "❌ لينك غير صالح.")
    # find last roulette by owner
    last = roulettes.find_one({"owner_id": message.from_user.id}, sort=[("_id", -1)])
    if not last:
        return bot.send_message(message.chat.id, "❌ مفيش روليت مسجلة.")
    # update
    update_roulette(str(last["_id"]), {"cond_channels": [link1]})
    bot.send_message(message.chat.id, "✅ تم حفظ قناة الشرط الأولى.\nاكتب نعم لو عايز تضيف الثانية.")
    bot.register_next_step_handler(message, lambda msg: _maybe_second_cond(msg, str(last["_id"]), link1))


def _maybe_second_cond(message: Message, rid: str, link1: str):
    ans = message.text.strip().lower()
    if ans in ["نعم", "yes", "اه", "ايوه", "أيوه"]:
        bot.send_message(message.chat.id, "📡 ارسل رابط القناة الثانية:")
        bot.register_next_step_handler(message, lambda msg: _save_cond_second(msg, rid, link1))
        return
    bot.send_message(message.chat.id, "✅ انتهينا.")


def _save_cond_second(message: Message, rid: str, link1: str):
    link2 = message.text.strip()
    if "t.me" not in link2 and not link2.startswith("http"):
        return bot.send_message(message.chat.id, "❌ لينك غير صالح.")
    r = get_roulette(rid)
    channels = r.get("cond_channels", []) if r else []
    channels.append(link2)
    update_roulette(rid, {"cond_channels": channels})
    bot.send_message(message.chat.id, "✅ تم حفظ القناة الثانية.")


# ---------------------------
# Publishing
# ---------------------------
def _format_conditions(cond_list):
    if not cond_list:
        return "لا توجد شروط."
    return "\n".join(f"🔗 {c}" for c in cond_list)


def publish_roulette(rid: str):
    """
    Publish a roulette post to DRAW_CHANNEL (config). Expects rid as string.
    """
    r = get_roulette(rid)
    if not r:
        raise ValueError("Roulette not found")

    title = r.get("title")
    price = r.get("price", 0)
    max_winners = r.get("max_winners", 1)
    channels = r.get("cond_channels", []) or []

    text = (
        f"🎉 *سحب جديد!*  \n"
        f"🎁 *{title}*  \n\n"
        f"💰 سعر الاشتراك: {'مجاني' if price==0 else str(price) + ' نجمة'}  \n"
        f"👥 عدد الفائزين: {max_winners}  \n\n"
        f"📌 شروط السحب:\n{_format_conditions(channels)}\n\n"
        f"اضغط على الزر للانضمام 👇"
    )

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🚀 ادخل السحب", callback_data=f"join_{rid}"))
    kb.add(InlineKeyboardButton("ℹ️ معلومات السحب", callback_data=f"rouinfo_{rid}"))

    # use DRAW_CHANNEL from config
    bot.send_message(DRAW_CHANNEL, text, reply_markup=kb, parse_mode="Markdown")


# ---------------------------
# Join flow
# ---------------------------
@bot.callback_query_handler(func=lambda c: c.data.startswith("join_"))
def _join_callback(call: CallbackQuery):
    user_id = call.from_user.id
    rid = call.data.split("_", 1)[1]

    r = get_roulette(rid)
    if not r or not r.get("active", True):
        return bot.answer_callback_query(call.id, "❌ السحب غير موجود أو مُغلق.", show_alert=True)

    # check conditions
    channels = r.get("cond_channels", []) or []
    for ch in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                btn = InlineKeyboardMarkup()
                btn.add(InlineKeyboardButton("🔗 اشترك ثم اضغط هنا", callback_data=f"join_{rid}"))
                return bot.send_message(user_id, f"❌ لازم تشترك في:\n{ch}", reply_markup=btn)
        except Exception:
            return bot.send_message(user_id, f"⚠️ مشكلة في التحقق من القناة: {ch}")

    # check balance
    user = get_user(user_id)
    price = r.get("price", 0)
    if user.get("stars", 0) < price:
        return bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ!", show_alert=True)

    # deduct and add participant
    update_stars(user_id, -price)
    join_roulette(rid, user_id)

    bot.answer_callback_query(call.id, "🎉 انضميت للسحب!", show_alert=True)
    bot.send_message(user_id, "🎉 تم انضمامك للسحب بنجاح.")


# ---------------------------
# Info
# ---------------------------
@bot.callback_query_handler(func=lambda c: c.data.startswith("rouinfo_"))
def _info_callback(call: CallbackQuery):
    rid = call.data.split("_", 1)[1]
    r = get_roulette(rid)
    if not r:
        return bot.answer_callback_query(call.id, "❌ السحب غير موجود!", show_alert=True)

    text = (
        f"🎉 *معلومات السحب*  \n\n"
        f"📌 العنوان: {r.get('title')}  \n"
        f"💰 السعر: {'مجاني' if r.get('price',0)==0 else str(r.get('price'))+' نجمة'}  \n"
        f"👥 عدد المشاركين: {len(r.get('participants',[]))}  \n"
        f"🏅 عدد الفائزين: {r.get('max_winners',1)}  \n"
    )
    bot.answer_callback_query(call.id, text, show_alert=True)


# ---------------------------
# Draw / finish
# ---------------------------
@bot.callback_query_handler(func=lambda c: c.data.startswith("draw_"))
def _draw_callback(call: CallbackQuery):
    rid = call.data.split("_", 1)[1]
    r = get_roulette(rid)
    if not r:
        return bot.answer_callback_query(call.id, "❌ السحب غير موجود.", show_alert=True)
    if not r.get("active", True):
        return bot.answer_callback_query(call.id, "⚠️ السحب مغلق!", show_alert=True)

    participants = r.get("participants", [])
    max_winners = r.get("max_winners", 1)
    price = r.get("price", 0)
    owner_id = r.get("owner_id")

    if len(participants) < max_winners:
        return bot.answer_callback_query(call.id, "⚠️ عدد المشتركين أقل من عدد الفائزين!", show_alert=True)

    winners = random.sample(participants, max_winners)

    total_stars = price * len(participants)
    stars_per_winner = total_stars // max_winners
    remaining = total_stars % max_winners

    for w in winners:
        update_stars(w, stars_per_winner)

    if remaining > 0:
        # remaining goes to bot owner (OWNER_ID)
        update_stars(OWNER_ID, remaining)

    update_roulette(rid, {"active": False, "winners": winners})

    result_text = "🎉 *نتيجة السحب:*  \n\n"
    for w in winners:
        result_text += f"🏆 الفائز: [{w}](tg://user?id={w})\n"

    bot.send_message(call.message.chat.id, result_text, parse_mode="Markdown")


# ---------------------------
# Claim earnings (for owner of roulette)
# ---------------------------
@bot.callback_query_handler(func=lambda c: c.data.startswith("earn_"))
def _earn_callback(call: CallbackQuery):
    rid = call.data.split("_", 1)[1]
    r = get_roulette(rid)
    if not r:
        return bot.answer_callback_query(call.id, "❌ السحب غير موجود.", show_alert=True)

    owner_id = call.from_user.id
    if r.get("owner_id") != owner_id:
        return bot.answer_callback_query(call.id, "❌ مش بتاعك!")

    if r.get("claimed", False):
        return bot.answer_callback_query(call.id, "✔️ تم استلام الأرباح بالفعل!")

    total = r.get("price", 0) * len(r.get("participants", []))
    update_stars(owner_id, total)
    update_roulette(rid, {"claimed": True})

    bot.answer_callback_query(call.id, "💰 تم إضافة أرباحك للمحفظة!", show_alert=True)
# handlers/start.py

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from config import OWNER_ID
from database import get_user
from handlers.booster.menu import booster_menu  # لاستدعاء القائمة مباشرة عند الضغط

@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    user_id = message.from_user.id

    # إنشاء المستخدم لو مش موجود
    user = get_user(user_id)

    # رسالة الترحيب
    text = (
        "👋 أهلاً بيك في بوت *Elnoor Bot*\n"
        "⚡ أقوى نظام روليت + صناديق هدايا + بوستر + هوت رول + إشعارات متقدمة!\n\n"
        "اختار من القائمة بالأسفل 👇"
    )

    # إنشاء الزرار
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎰 الروليت", callback_data="menu_roulette"))
    kb.add(InlineKeyboardButton("🎁 صناديق الهدايا", callback_data="menu_gifts"))
    kb.add(InlineKeyboardButton("🚀 Booster", callback_data="menu_booster"))
    kb.add(InlineKeyboardButton("🔥 Hot Roll", callback_data="menu_hot"))
    kb.add(InlineKeyboardButton("🔔 الإشعارات", callback_data="menu_notify"))

    # زر خاص بالمالك فقط
    if str(user_id) == str(OWNER_ID):
        kb.add(InlineKeyboardButton("👑 لوحة التحكم للمالك", callback_data="owner_panel"))

    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode="Markdown")

# استدعاء القائمة الفرعية للـ Booster عند الضغط على زر القائمة الرئيسية
@bot.callback_query_handler(func=lambda call: call.data == "menu_booster")
def open_booster_menu(call):
    # نعيد استخدام دالة booster_menu الموجودة في handlers/booster/menu.py
    booster_menu(call.message)
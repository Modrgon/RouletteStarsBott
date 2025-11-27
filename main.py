# main.py — الملف الرئيسي للبوت

from loader import bot

# استيراد الهاندلرز ليتم تسجيلهم عند الاستيراد
import handlers.start
import handlers.roulette
import handlers.gift.__init__  # يحمّل جميع handlers داخل مجلد gift
import handlers.booster.__init__  # لو ملف init موجود، يحمل كل ملفات البوستر

print("Bot is running...")
bot.infinity_polling()
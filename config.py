# config.py — إعدادات المشروع (حط القيم هنا)

TOKEN = "8359921719:AAHAFk6CvJJA_Q0IB7rtf7YXUdHnynEndOY"
OWNER_ID = 7531829463
SUPPORT_BOT = "@Tassgell_1bot"
DRAW_CHANNEL = "https://t.me/Hikam_Gold"

# MongoDB connection string
MONGO_URI = "mongodb+srv://rjbm29016_db_user:Xg0GT3VFrlaAPtTQ@cluster0.0eqx4tb.mongodb.net/?appName=Cluster0"
DB_NAME = "ElnoorBotDB"

# Booster settings (seconds)
BOOSTER_LEVELS = {
    1: {"duration": 10 * 60, "price": 5},    # 10 minutes
    2: {"duration": 25 * 60, "price": 15},   # 25 minutes
    3: {"duration": 60 * 60, "price": 30},   # 60 minutes
}

# Hot roll default price (stars)
HOTROLL_PRICE = 20

# Optional: provider token for Telegram payments (leave empty if unused)
PROVIDER_TOKEN = ""
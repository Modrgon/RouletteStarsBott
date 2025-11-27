# loader.py
from config import BOT_TOKEN
import telebot

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
import os
import threading
from flask import Flask
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "شغال 24 ساعة ✅")

@app.route('/')
def home():
    return "Bot is Running..."

def run_bot():
    print("Bot polling started...")
    bot.infinity_polling()

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()
    run_flask()

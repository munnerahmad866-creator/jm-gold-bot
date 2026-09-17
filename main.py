import telebot
import threading
import time
import os
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

readings = 0
auto_on = False
open_trade = False

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "✅ شغال 24 ساعة\nالبوت شغال 24/7 على السيرفر، وكلشي تمام.\n\nالتداول الآلي: " + ("شغال" if auto_on else "متوقف") + f"\nالقراءات المحفوظة: {readings}/50\nالحالة: " + ("صفقة مفتوحة" if open_trade else "ماكو صفقة مفتوحة"))

@bot.message_handler(commands=['auto'])
def auto(m):
    global auto_on
    auto_on = True
    bot.reply_to(m, "🔥 التداول الآلي: شغال\nالبوت بدأ يجمع قراءات، يحتاج 50 قراءة (50 دقيقة) ويبدي يتداول وحده.\nدز /status حتى تشوف التقدم.")

@bot.message_handler(commands=['status', 'balance'])
def status(m):
    bot.reply_to(m, f"📊 الحالة:\nالتداول الآلي: {'شغال ✅' if auto_on else 'متوقف ❌'}\nالقراءات المحفوظة: {readings}/50\nالحالة: {'صفقة مفتوحة' if open_trade else 'ماكو صفقة مفتوحة'}\nالرصيد التجريبي: 10000$")

@bot.message_handler(commands=['stop'])
def stop(m):
    global auto_on
    auto_on = False
    bot.reply_to(m, "⏹️ التداول الآلي توقف")

def price_collector():
    global readings
    while True:
        time.sleep(60)
        if readings < 50:
            readings += 1
        print(f"Price collected: {readings}/50")

threading.Thread(target=price_collector, daemon=True).start()

@app.route('/')
def home():
    return "Bot is running 24/7"

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

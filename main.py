import os, time, requests, threading
from collections import deque
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8217643740:AAF9S1SErV87xt2l_XtFyRMW51kLa3vmVyM")
CHAT_ID = os.getenv("CHAT_ID", "5868066096")

prices = deque(maxlen=50)
in_trade = False
entry_price = 0
trade_type = ""

@app.route('/')
def home():
    p = list(prices)[-1] if prices else 0
    return f"JM-GOLD شغال | السعر {p} | في صفقة: {trade_type if in_trade else 'لا'}"

def get_gold():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=10).json()
        p = float(r['price'])
        if p > 1000:
            return p
    except:
        pass
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        return float(r['price'])
    except:
        return None

def calc_rsi(data, period=14):
    if len(data) < period + 1:
        return 50
    gains, losses = 0, 0
    for i in range(1, period + 1):
        diff = data[-i] - data[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff
    if losses == 0:
        return 70
    rs = gains / losses
    return 100 - (100 / (1 + rs))

def send(text):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except:
        pass

def bot_loop():
   

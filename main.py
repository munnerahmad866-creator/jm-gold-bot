import os, time, requests, threading
from collections import deque
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8217643740:AAF9S1SErV87xt2l_XtFyRMW51kLa3vmVyM")
CHAT_ID = os.getenv("CHAT_ID", "5868066096")

prices = deque(maxlen=30)
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
       

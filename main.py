import os, time, requests, threading
from collections import deque
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8217643740:AAF9S1SErV87xt2l_XtFyRMW51kLa3vmVyM")
CHAT_ID = os.getenv("CHAT_ID", "5868066096")

prices = deque(maxlen=50)
balance = 11321.90
in_trade = False
entry_price = 0
trade_type = ""

@app.route('/')
def home():
    return "بوت JM-GOLD شغال - يحلل الذهب"

def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=15).json()
        p = float(r['price'])
        if p > 2000: return p
    except: pass
    try:
        r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=15).json()
        return float(r['items'][0]['xauPrice'])
    except: return None

def calc_rsi(data, period=14):
    if len(data) < period+1: return 50
    gains, losses = 0, 0
    for i in range(1, period+1):
        diff = data[-i] - data[-i-1]
        if diff > 0: gains += diff
        else: losses -= diff
    if losses == 0: return 70
    return 100 - (100 / (1 + gains/losses))

def send(text):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except: pass

def bot_loop():
    global in_trade, entry_price, trade_type, balance
    send("✅ تم اصلاح البوت\nالان مربوط على Railway بشكل صحيح\nيحلل الذهب ويگولك بيع/شراء")
    while True:
        price = get_gold()
        if not price:
            time.sleep(60)
            continue
        prices.append(price)
        if len(prices) < 20:
            time.sleep(120)
            continue
        rsi = calc_rsi(list(prices))
        ema5 = sum(list(prices)[-5:]) / 5
        ema20 = sum(list(prices)[-20:]) / 20
        if not in_trade:
            if rsi < 38 and ema5 > ema20:
                entry_price = price
                trade_type = "شراء"
                in_trade = True
                send(f"📈 فتحت صفقة شراء\nالسعر: {price:.2f} 💰\nالرصيد: {balance:.2f}$ 💼\nRSI: {rsi:.1f}\n➡️ روح افتح شراء هسه بـ JM")
            elif rsi > 62 and ema5 < ema20:
                entry_price = price
                trade_type = "بيع"
                in_trade = True
                send(f"📉 فتحت صفقة بيع\nالسعر: {price:.2f} 💰\nالرصيد: {balance:.2f}$ 💼\nRSI: {rsi:.1f}\n➡️ روح افتح بيع هسه بـ JM")
        else:
            profit = (price - entry_price)*10 if trade_type=="شراء" else (entry_price - price)*10
            if profit >= 12 or profit <= -8:
                balance += profit
                if profit > 0:
                    send(f"✅ سديت صفقة {trade_type} ربح +{profit:.2f}$\nالرصيد الجديد: {balance:.2f}$ 💼\nالصفقة الجاية بعد 10 دقايق ⏳")
                else:
                    send(f"❌ سديت صفقة {trade_type} خسارة {profit:.2f}$\nالرصيد الجديد: {balance:.2f}$ 💼\nالصفقة الجاية بعد 10 دقايق ⏳")
                in_trade = False
                time.sleep(600)
        time.sleep(180)

# شغل البوت بخلفية
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

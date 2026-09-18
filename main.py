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
    return f"بوت JM-GOLD شغال | يجمع {len(prices)}/20 | السعر {list(prices)[-1] if prices else 0}"

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
    send("✅ البوت اشتغل بنجاح\nدز /status حتى تشوف وين وصل")
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
                    send(f"✅ سديت صفقة {trade_type} ربح +{profit:.2f}$\nالرصيد الجديد: {balance:.2f}$ 💼")
                else:
                    send(f"❌ سديت صفقة {trade_type} خسارة {profit:.2f}$\nالرصيد الجديد: {balance:.2f}$ 💼")
                in_trade = False
                time.sleep(600)
        time.sleep(180)

def check_messages():
    last_id = 0
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_id+1}", timeout=20).json()
            for upd in r.get("result", []):
                last_id = upd["update_id"]
                msg = upd.get("message", {})
                text = msg.get("text", "")
                if "/status" in text or "وين" in text or "status" in text:
                    p = list(prices)[-1] if prices else 0
                    txt = f"📊 حالة البوت:\n📦 يجمع: {len(prices)}/20\n💰 السعر الحالي: {p:.2f}$\n💼 الرصيد: {balance:.2f}$\n📈 في صفقة: {trade_type if in_trade else 'لا يوجد'}"
                    send(txt)
                if "/start" in text:
                    send("اهلا شيخ 👋\nالبوت شغال يحلل الذهب\nدز /status حتى تشوف وين وصل")
        except: pass
        time.sleep(5)

threading.Thread(target=bot_loop, daemon=True).start()
threading.Thread(target=check_messages, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

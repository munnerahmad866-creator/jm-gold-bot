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
    return f"JM-GOLD Active | {p}"

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

def calc_rsi(data, period=7):
    if len(data) < period + 1:
        return 50
    gains=0
    losses=0
    for i in range(1, period+1):
        diff=data[-i]-data[-i-1]
        if diff>0:
            gains+=diff
        else:
            losses-=diff
    if losses==0:
        return 65
    rs=gains/losses
    return 100-(100/(1+rs))

def send(text):
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except:
        pass

def bot_loop():
    global in_trade, entry_price, trade_type
    time.sleep(5)
    send("✅ بوت JM جاهز\nراح يجمع 10 قراءات (10 دقايق) وكل ما تجي فرصة ابلغك اشتري او بيع على منصة JM")
    while True:
        price=get_gold()
        if not price:
            time.sleep(30)
            continue
        prices.append(price)
        if len(prices) < 10:
            time.sleep(60)
            continue
        rsi=calc_rsi(list(prices))
        ema5=sum(list(prices)[-5:])/5
        ema10=sum(list(prices)[-10:])/10
        
        if not in_trade:
            if rsi < 45 and ema5 > ema10:
                entry_price=price
                trade_type="شراء"
                in_trade=True
                send(f"📈 فرصة قوية - اشتري هسه على منصة JM\n💰 السعر: {price:.2f}$\n📊 RSI: {rsi:.1f}\nادخل شراء وارباح ان شاء الله")
            elif rsi > 55 and ema5 < ema10:
                entry_price=price
                trade_type="بيع"
                in_trade=True
                send(f"📉 فرصة قوية - بيع هسه على منصة JM\n💰 السعر: {price:.2f}$\n📊 RSI: {rsi:.1f}\nادخل بيع وارباح ان شاء الله")
        else:
            diff=price-entry_price if trade_type=="شراء" else entry_price-price
            if diff >= 1.5 or diff <= -1.0:
                send(f"🔒 سكر الصفقة هسه على منصة JM\nالنوع: {trade_type}\nالسعر: {price:.2f}$")
                in_trade=False
                time.sleep(300)
        time.sleep(90)

def check_messages():
    last_id=0
    time.sleep(10)
    try:
        r=requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1", timeout=10).json()
        if r.get("result"):
            last_id=r["result"][-1]["update_id"]
    except:
        pass
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_id+1}", timeout=25).json()
            for upd in r.get("result", []):
                last_id=upd["update_id"]
                msg=upd.get("message",{}).get("text","")
                if "/status" in msg:
                    if len(prices) < 2:
                        send("⏳ بعده يجمع... انتظر دقايق")
                    else:
                        p=list(prices)[-1]
                        rsi=calc_rsi(list(prices))
                        send(f"📊 الحالة: يجمع {len(prices)}/10\n💰 السعر: {p:.2f}$\n📈 RSI: {rsi:.1f}\nفي صفقة: {trade_type if in_trade else 'لا يوجد - ينتظر فرصة'}")
        except:
            pass
        time.sleep(5)

threading.Thread(target=bot_loop, daemon=True).start()
threading.Thread(target=check_messages, daemon=True).start()

if __name__ == "__main__":
    port=int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

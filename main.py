from flask import Flask
import threading, time, random, os
from datetime import datetime

app = Flask(__name__)
balance = 1000.0
trades = 0

def bot_loop():
    global balance, trades
    while True:
        profit = random.choice([5, 6, 7, -2, -1])
        balance += profit
        trades += 1
        print(f"Trade {trades} Profit {profit} Balance {balance} - {datetime.now()}")
        time.sleep(900)

@app.route('/')
def home():
    return f"<h1>JM GOLD BOT شغال ✅</h1><h2>Balance: {balance}$</h2><h2>Trades: {trades}</h2><p>{datetime.now()}</p>"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

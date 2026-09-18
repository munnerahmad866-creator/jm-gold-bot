            readings.append(p)
            if len(readings) > 100: readings.pop(0)
            now = time.time()
            
            if open_trade is None and (now - last_trade_time) >= TRADE_INTERVAL and len(readings) >= 2:
                open_trade = {"type": random.choice(["شراء","بيع"]), "price": p, "time": now}
                last_trade_time = now
                send(f"📈 فتحت صفقة {open_trade['type']}\n💰 السعر: {p:.2f}\n💼 الرصيد: ${balance:.2f}")
            
            if open_trade and (now - open_trade["time"]) >= 180:
                profit = random.uniform(10, 20)
                balance += profit
                send(f"✅ سديت صفقة {open_trade['type']} بربح +${profit:.2f}\n💼 الرصيد الجديد: ${balance:.2f}\n⏳ الصفقة الجاية بعد 10 دقايق")
                open_trade = None
            
            time.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(10)

threading.Thread(target=trading_loop, daemon=True).start()
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

@bot.message_handler(commands=['start'])
def start(m):
    global current_chat_id
    current_chat_id = m.chat.id
    bot.reply_to(m, f"🔥 هلا شيخ! البوت شغال كل 10 دقايق\n💼 رصيدك: ${balance:.2f}\nدز /status")

@bot.message_handler(commands=['status'])
def status(m):
    global current_chat_id
    current_chat_id = m.chat.id
    rem = int(TRADE_INTERVAL - (time.time() - last_trade_time)) if last_trade_time else 0
    if rem < 0: rem = 0
    t = f"📊 الرصيد: ${balance:.2f}\n"
    t += f"📈 مفتوحة: {open_trade['type'] if open_trade else 'ماكو'}\n"
    t += f"⏳ الجاية بعد: {rem//60} دقيقة و {rem%60} ثانية"
    bot.reply_to(m, t)

print("Bot starting polling...")
# هذا يحل مشكلة الخطأ الاحمر
bot.remove_webhook()
time.sleep(1)
bot.infinity_polling(skip_pending=True, timeout=30)

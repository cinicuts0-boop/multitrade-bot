import requests
import time

TOKEN = "8633538252:AAGIDwplfgtsGcGvZPCJmMrnX_R0dGOzOAc"
CHAT_ID = "8007854479"

COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "ripple"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        print("Telegram error")

def get_prices(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=1"
    try:
        res = requests.get(url, timeout=10).json()
        if 'prices' in res:
            return [p[1] for p in res['prices']]
    except:
        pass
    return None

def calculate_rsi(prices, period=14):
    gains, losses = [], []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    if len(gains) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period):
    ema = prices[0]
    k = 2 / (period + 1)

    for price in prices:
        ema = price * k + ema * (1 - k)

    return ema

last_signals = {}

while True:
    try:
        for coin in COINS:
            prices = get_prices(coin)

            if prices is None:
                continue

            current_price = prices[-1]
            rsi = calculate_rsi(prices)
            ema20 = calculate_ema(prices, 20)
            ema50 = calculate_ema(prices, 50)

            recent = prices[-20:]
            high = max(recent)
            low = min(recent)

            print(f"{coin.upper()} | Price: {current_price} | RSI: {rsi}")

            last_signal = last_signals.get(coin, "")

            # 🟢 BUY
            if (rsi > 50 and current_price > ema20 and ema20 > ema50 and current_price > high and last_signal != "BUY"):
                send_message(f"{coin.upper()} BUY 🚀\nPrice: {current_price:.2f}")
                last_signals[coin] = "BUY"

            # 🔴 SELL
            elif (rsi < 50 and current_price < ema20 and ema20 < ema50 and current_price < low and last_signal != "SELL"):
                send_message(f"{coin.upper()} SELL 🔻\nPrice: {current_price:.2f}")
                last_signals[coin] = "SELL"

        time.sleep(600)  # 10 minutes (safe)

    except Exception as e:
        print("Error:", e)
        time.sleep(600)

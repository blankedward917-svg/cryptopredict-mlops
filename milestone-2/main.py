import os
import requests
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# ----------------------------
# Binance API (USDT pairs only)
# ----------------------------
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def fetch_binance_data(symbol="BTCUSDT", interval="1h", lookback="200"):
    url = f"{BINANCE_API_URL}?symbol={symbol}&interval={interval}&limit={lookback}"
    response = requests.get(url)
    data = response.json()

    if not data or "code" in data:
        raise ValueError(f"Binance API error for {symbol}: {data}")

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "qav", "num_trades", "taker_base_vol",
        "taker_quote_vol", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)

    # Convert USD → INR
    usd_to_inr = 88.19  # static conversion, update as needed
    df["close"] = df["close"] * usd_to_inr

    return df[["timestamp", "close"]]

# ----------------------------
# Timeframe mapping
# ----------------------------
TIMEFRAMES = {}

# Hourly: Next 1h → Next 23h
for h in range(1, 24):
    TIMEFRAMES[f"Next {h} Hour" if h == 1 else f"Next {h} Hours"] = {
        "interval": "1h",
        "model_dir": "infosys/outputs/models/hourly"
    }

# Daily: Next 1d → Next 30d
for d in range(1, 31):
    TIMEFRAMES[f"Next {d} Day" if d == 1 else f"Next {d} Days"] = {
        "interval": "1d",
        "model_dir": "infosys/outputs/models/daily"
    }
# ----------------------------
# Coin symbol → Binance & Model mapping
# ----------------------------
MODEL_NAME_MAP = {
    "BTC": {"binance": "BTCUSDT", "model": "BITCOIN_INR.keras"},
    "ETH": {"binance": "ETHUSDT", "model": "ETHEREUM_INR.keras"},
    "DOGE": {"binance": "DOGEUSDT", "model": "DOGECOIN_INR.keras"},
    "LTC": {"binance": "LTCUSDT", "model": "LITECOIN_INR.keras"},
    "DOT": {"binance": "DOTUSDT", "model": "POLKADOT_INR.keras"},
    "MATIC": {"binance": "MATICUSDT", "model": "POLYGON_INR.keras"},
    "XRP": {"binance": "XRPUSDT", "model": "RIPPLE_INR.keras"},
    "LINK": {"binance": "LINKUSDT", "model": "CHAINLINK_INR.keras"},
    "BCH": {"binance": "BCHUSDT", "model": "BITCOIN_CASH_INR.keras"},
    "BNB": {"binance": "BNBUSDT", "model": "BINANCE_INR.keras"},
}

# ----------------------------
# Prediction
# ----------------------------
def get_live_prediction(coin="BTC", timeframe="Next 1 Hour"):
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"Invalid timeframe. Choose from: {list(TIMEFRAMES.keys())}")

    if coin.upper() not in MODEL_NAME_MAP:
        raise ValueError(f"No model mapping defined for {coin}")

    tf_info = TIMEFRAMES[timeframe]
    interval = tf_info["interval"]
    model_dir = tf_info["model_dir"]

    binance_symbol = MODEL_NAME_MAP[coin.upper()]["binance"]
    model_filename = MODEL_NAME_MAP[coin.upper()]["model"]
    model_path = os.path.join(model_dir, model_filename)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    # Load trained model
    model = tf.keras.models.load_model(model_path)

    # Fetch live data (from Binance in USDT, converted to INR)
    df = fetch_binance_data(symbol=binance_symbol, interval=interval, lookback="200")
    close_prices = df["close"].values.reshape(-1, 1)

    # Scale
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)

    # Prepare last 60 timesteps
    X_test = [scaled_data[-60:]]
    X_test = np.array(X_test).reshape((1, 60, 1))

    # Prediction
    predicted_scaled = model.predict(X_test)
    predicted_price = scaler.inverse_transform(predicted_scaled)[0][0]

    return {
        "coin": coin,
        "timeframe": timeframe,
        "last_price": float(close_prices[-1][0]),
        "predicted_price": float(predicted_price),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model_used": os.path.basename(model_path),
    }

# ----------------------------
# Example Run
# ----------------------------
if __name__ == "__main__":
    result = get_live_prediction("BTC", "Next 1 Hour")
    print(result)

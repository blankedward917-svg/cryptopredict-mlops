import yaml
import yfinance as yf
import os

# Map from Promptfoo coin names to Yahoo Finance symbols
COIN_MAP = {
    "Bitcoin": "BTC-INR",
    "Ethereum": "ETH-INR",
    "Solana": "SOL-INR",
    "Binance Coin": "BNB-INR",
    "Bitcoin Cash": "BCH-INR",
    "Litecoin": "LTC-INR",
    "Chainlink": "LINK-INR",
    "Avalanche": "AVAX-INR",
    "Ripple": "XRP-INR",
    "Polkadot": "DOT-INR",
    "Cardano": "ADA-INR",
    "Polygon": "POL-INR",
    "Dogecoin": "DOGE-INR"
}

CONFIG_PATH = "promptfooconfig.yaml"

def get_live_prices():
    print("Fetching live prices from Yahoo Finance...")
    prices = {}
    for name, symbol in COIN_MAP.items():
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.fast_info['last_price']
            prices[name] = round(current_price, 2)
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    return prices

def update_config(live_prices):
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: {CONFIG_PATH} not found.")
        return

    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    # Update each test case
    for test in config.get('tests', []):
        coin_name = test.get('vars', {}).get('coin')
        if coin_name in live_prices:
            actual_price = live_prices[coin_name]
            # Set previous price to current actual
            test['vars']['previous_price'] = f"{actual_price:,}"
            # Mock a 1.5% prediction for the demo
            predicted = round(actual_price * 1.015, 2)
            test['vars']['predicted_price'] = f"{predicted:,}"

    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Successfully updated {CONFIG_PATH} with real-time prices.")

if __name__ == "__main__":
    live_data = get_live_prices()
    update_config(live_data)

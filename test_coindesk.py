import requests
import json
import time

def test_endpoint(url, params):
    try:
        print(f"Testing URL: {url}")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Successfully fetched data!")
            # Print a small sample
            if 'Data' in data:
                print(f"Number of records: {len(data['Data'])}")
                if len(data['Data']) > 0:
                    print(f"Record keys: {data['Data'][0].keys()}")
                    print(f"Sample: {data['Data'][0]}")
            else:
                print(f"Keys in response: {data.keys()}")
            return True
        else:
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Base URLs to try
bases = [
    "https://production.api.coindesk.com/v2/tb/ohlcv",
    "https://data-api.coindesk.com"
]

params = {
    "market": "cadli",
    "instrument": "BTC-USD",
    "limit": "5",
    "aggregate": "1"
}

for base in bases:
    url = f"{base}/index/cc/v1/historical/hours"
    if test_endpoint(url, params):
        print(f"MATCH FOUND: {base}")
        break

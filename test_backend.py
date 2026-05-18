import requests
import json

def test_prediction():
    url = "http://127.0.0.1:5001/predict"
    payload = {
        "coin": "BTC",
        "timeframe": "hourly"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "predictedPrice" in data:
                print("\n✅ Backend test passed!")
            else:
                print("\n❌ Backend test failed: missing successful prediction data.")
        else:
            print(f"\n❌ Backend test failed: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Backend test failed with error: {e}")

if __name__ == "__main__":
    # Note: Backend must be running for this test to pass
    test_prediction()

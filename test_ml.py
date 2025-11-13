import requests

try:
    response = requests.get('http://localhost:5000/health', timeout=5)
    print(f"✅ ML Health: {response.json()}")
except Exception as e:
    print(f"❌ ML Health failed: {e}")

try:
    # Test prediction endpoint
    test_data = {
        "features": [100000, 0.5, 1000, 0.02, 0.01, 1.2, 0.8]
    }
    response = requests.post('http://localhost:5000/predict', json=test_data, timeout=10)
    print(f"✅ ML Predict: {response.json()}")
except Exception as e:
    print(f"❌ ML Predict failed: {e}")
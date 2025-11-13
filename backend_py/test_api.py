import requests

# Test health endpoint
try:
    response = requests.get("http://localhost:3000/health")
    print(f"Health endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test status endpoint
try:
    response = requests.get("http://localhost:3000/api/status")
    print(f"Status endpoint: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
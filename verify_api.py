import requests
import time
import sys

def verify_api():
    base_url = "http://127.0.0.1:8000"
    print(f"Connecting to {base_url}...")
    
    # Retry connection for a few seconds
    for _ in range(5):
        try:
            response = requests.get(f"{base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health check passed!")
                print(response.json())
                break
        except Exception as e:
            print(f"Waiting for server... ({e})")
            time.sleep(2)
    else:
        print("❌ Failed to connect to API")
        sys.exit(1)
        
    # Test Process (Mock if no keys)
    # We won't test full process if keys are missing from env, but we can try small input
    # Assuming keys are in env or we expect failure
    try:
        payload = {
            "input_type": "text",
            "input_data": "Artificial Intelligence is the simulation of human intelligence processes by machines.",
            "num_questions": 1,
            "difficulty": "easy"
        }
        print("Testing /api/process...")
        response = requests.post(f"{base_url}/api/process", json=payload)
        if response.status_code == 200:
            print("✅ Process endpoint passed!")
            data = response.json()
            print(f"Summary: {data.get('summary')[:50]}...")
        else:
            print(f"⚠️ Process endpoint returned {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error testing process: {e}")

if __name__ == "__main__":
    verify_api()

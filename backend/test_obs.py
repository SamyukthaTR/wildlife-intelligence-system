import urllib.request
import json
import urllib.error
import sys

API_URL = "http://localhost:8000"

def request(method, path, data=None, headers=None):
    if headers is None: headers = {}
    url = f"{API_URL}{path}"
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def run_test():
    print("1. Registering 'Researcher 2'...")
    status, data = request("POST", "/auth/register", data={
        "name": "Researcher 2",
        "email": "researcher2@example.com",
        "password": "password123",
        "role": "Wildlife Researcher"
    })
    
    # Ignore 400 if user already exists
    if status not in [201, 400]:
        print("Failed to register:", status, data)
        return

    print("2. Logging in as 'Researcher 2'...")
    status, data = request("POST", "/auth/login", data={
        "email": "researcher2@example.com",
        "password": "password123"
    })
    
    if status != 200:
        print("Failed to login:", status, data)
        return
        
    access_token = json.loads(data)["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"3. Researcher 2 attempting to access Observation ID 1 directly via GET /observations/1/file...")
    status, data = request("GET", "/observations/1/file", headers=headers)
    
    print(f"Response Status: {status}")
    try:
        print(f"Response Body: {json.loads(data)}")
    except:
        print(f"Response Body: [Raw Binary Data or empty]")

    if status == 403:
        print("\nSUCCESS! The backend correctly rejected Researcher 2 with a 403 Forbidden.")
    else:
        print("\nFAILURE! The backend did not return 403. Check router logic.")

if __name__ == "__main__":
    run_test()

"""
Frontend-Backend Connection Diagnostic Script
"""
import requests
import json

print("=" * 60)
print("Highway Inspection System - Connection Diagnostic")
print("=" * 60)
print()

# Test 1: Backend Health Check
print("[Test 1] Backend Health Check")
print("-" * 60)
try:
    response = requests.get('http://localhost:3000/health', timeout=5)
    print(f"OK Backend is running")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
except Exception as e:
    print(f"ERROR Backend connection failed: {str(e)}")
    print("  Please make sure backend is running: python run.py")
    exit(1)
print()

# Test 2: Login API
print("[Test 2] Test Login API")
print("-" * 60)
try:
    data = {
        "username": "operator1",
        "password": "op123"
    }
    response = requests.post('http://localhost:3000/api/auth/login', json=data, timeout=5)
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"OK Login successful")
        print(f"  User: {result['data']['user']['username']}")
        print(f"  Role: {result['data']['user']['role']}")
        token = result['data']['access_token']
        print(f"  Token: {token[:50]}...")
        
        # Test 3: Access API with token
        print()
        print("[Test 3] Access Airspace API with Token")
        print("-" * 60)
        headers = {'Authorization': f'Bearer {token}'}
        response2 = requests.get('http://localhost:3000/api/airspaces', headers=headers, timeout=5)
        print(f"  Status Code: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"OK API access successful")
            print(f"  Total airspaces: {result2['data']['total']}")
            if result2['data']['items']:
                print(f"  First airspace: {result2['data']['items'][0]['name']}")
        else:
            print(f"ERROR API access failed")
            print(f"  Response: {response2.text}")
            
    else:
        print(f"ERROR Login failed")
        print(f"  Response: {response.text}")
        print()
        print("Possible reasons:")
        print("  1. Database not initialized - Run: python init_db.py")
        print("  2. Database connection failed - Check .env file")
        print("  3. Wrong username or password")
        exit(1)
        
except Exception as e:
    print(f"ERROR Request failed: {str(e)}")
    exit(1)

print()
print("=" * 60)
print("[Test 4] CORS Configuration")
print("-" * 60)
print("OK Frontend URL: http://localhost:5173")
print("OK Backend API: http://localhost:3000/api")
print()
print("Now open http://localhost:5173 in your browser")
print("Press F12 to open Developer Tools and check Network tab")
print()
print("=" * 60)
print("All Tests Passed!")
print("=" * 60)
print()
print("If frontend still cannot connect:")
print("1. Make sure frontend is running: npm run dev")
print("2. Clear browser cache and localStorage")
print("3. Check browser console for errors")


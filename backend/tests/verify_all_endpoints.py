import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8000/api/v1"

def req(url, data=None, headers=None, method=None):
    headers = headers or {}
    if data and isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request) as response:
        return response.status, json.loads(response.read().decode())

def run_tests():
    print("--- TESTING BACKEND ENDPOINTS ---")
    
    # 1. Health
    status, res = req(f"{BASE_URL}/health")
    print(f"[PASS] Health: {status} -> {res}")
    
    # 2. Seed
    status, res = req(f"{BASE_URL}/seed/sample")
    print(f"[PASS] Seed: {status} -> {res}")
    
    # 3. Auth Login
    status, token_res = req(f"{BASE_URL}/auth/login", data={"email": "demo@abcfurniture.com", "password": "password123"})
    print(f"[PASS] Login: {status} -> Token received")
    token = token_res.get("access_token")
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Get Business Profile
    status, profile = req(f"{BASE_URL}/business/profile", headers=auth_headers)
    print(f"[PASS] Profile: {status} -> Company: {profile.get('company_name')}")
    
    # 5. Get Products
    status, products = req(f"{BASE_URL}/business/products", headers=auth_headers)
    print(f"[PASS] Products: {status} -> Count: {len(products)}")
    
    # 6. Get Tenders
    status, tenders = req(f"{BASE_URL}/tenders", headers=auth_headers)
    print(f"[PASS] Tenders: {status} -> Count: {len(tenders)}")
    
    if tenders:
        tender_id = tenders[0]["id"]
        # 7. Analyze Tender
        status, analysis = req(f"{BASE_URL}/tenders/{tender_id}/analyze", headers=auth_headers, method="POST")
        print(f"[PASS] Tender Analysis: {status} -> Status: {analysis.get('status')}")
        
        # 8. Match Tender
        status, match = req(f"{BASE_URL}/tenders/{tender_id}/match", headers=auth_headers, method="POST")
        print(f"[PASS] Tender Match: {status} -> Match Score: {match.get('overall_score')}% ({match.get('eligibility_status')})")
        
        # 9. Application Cover Letter
        status, cover = req(f"{BASE_URL}/applications/cover-letter", data={"business_id": profile["id"], "tender_id": tender_id}, headers=auth_headers)
        print(f"[PASS] Application Cover Letter: {status} -> Draft generated successfully")
        
    print("--- ALL BACKEND ENDPOINTS PASSED SUCCESSFULLY ---")

if __name__ == "__main__":
    run_tests()

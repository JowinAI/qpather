import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_dashboard_settings_flow():
    # 1. Login
    print("1. Logging in...")
    login_payload = {"email": "joise.alvin@gmail.com"} 
    # Try dev-login
    resp = requests.post(f"{BASE_URL}/auth/dev-login", json=login_payload)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("   Login successful.")

    # 2. Get User Settings (Should exist or be empty/null, handles 404/204 gracefully in frontend but backend returns 200/null or 404?)
    print("\n2. Getting User Default Settings...")
    resp = requests.get(f"{BASE_URL}/users/me/dashboard-settings", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   Settings found: {resp.json() is not None}")
    
    # 3. Create a Dummy Goal (or use existing if we know one, but better to create)
    # Actually, let's use a hardcoded goal ID 185 from the screenshot if it exists, or better, list goals and pick one.
    print("\n3. Listing Goals to pick one...")
    resp = requests.get(f"{BASE_URL}/mygoals?user_email=joise.alvin@gmail.com", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        goals = data.get("items", [])
        if goals and len(goals) > 0:
            goal_id = goals[0]["Id"]
            print(f"   Using Goal ID: {goal_id}")
        else:
            print("   No goals found via mygoals. Trying hardcoded ID 184.")
            goal_id = 184
    else:
        print(f"   Failed to list goals: {resp.text}")
        return

    # 4. Save Goal Specific Settings (Override)
    print(f"\n4. Saving Settings for Goal {goal_id}...")
    payload = {
        "lensName": "Growth & Revenue",
        "focusSignals": ["Revenue", "Churn"],
        "focusQuestions": ["Why is growth slow?", "What is the blocker?"],
        "sections": {
            "executiveSummary": True,
            "signalHealth": True,
            "topRisks": True,
            "conflicts": False,
            "patterns": False,
            "actions": True,
            "dataGaps": False,
            "evidence": False,
            "focusQna": True
        },
        "display": {
            "timeHorizon": "fy",
            "verbosity": "normal",
            "maxRisks": 7,
            "maxActions": 7
        },
        "focusQuestionRules": None
    }
    
    resp = requests.put(f"{BASE_URL}/goals/{goal_id}/dashboard-settings", headers=headers, json=payload)
    print(f"   Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"   Error: {resp.text}")
    else:
        print("   Save Successful.")
        saved = resp.json()
        print(f"   Saved Lens: {saved.get('lensName')}")

    # 5. Verify Retrieval
    print(f"\n5. Verifying Goal Settings Retrieval...")
    resp = requests.get(f"{BASE_URL}/goals/{goal_id}/dashboard-settings", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Retrieved Lens: {data.get('lensName')}")
        assert data.get('lensName') == "Growth & Revenue"
        print("   Verification Passed.")
    else:
        print(f"   Failed to retrieve: {resp.text}")

    # 6. Reset Settings
    print(f"\n6. Resetting Details...")
    resp = requests.delete(f"{BASE_URL}/goals/{goal_id}/dashboard-settings", headers=headers)
    print(f"   Status: {resp.status_code}")
    
    # 7. Verify Reset
    print(f"\n7. Verify Reset (Should return default or null)...")
    resp = requests.get(f"{BASE_URL}/goals/{goal_id}/dashboard-settings", headers=headers)
    # Backend implementation returns None (null) if not found, status 200? Or 404? 
    # Looking at code: if not settings_obj: return None. Response defaults to 200 OK with null body.
    print(f"   Status: {resp.status_code}")
    print(f"   Body: {resp.text}")

if __name__ == "__main__":
    test_dashboard_settings_flow()

#!/usr/bin/env python3
"""Oura OAuth2 token management."""
import json, sys, os, urllib.request, urllib.parse, time

CREDS_PATH = os.environ.get("OURA_CREDS", "/data/.clawdbot/credentials/oura.json")
CLIENT_ID = os.environ.get("OURA_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("OURA_CLIENT_SECRET", "")
TOKEN_URL = "https://api.ouraring.com/oauth/token"
AUTH_URL = "https://cloud.ouraring.com/oauth/authorize"
REDIRECT_URI = "http://localhost/oura/callback"

def load_creds():
    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH) as f: return json.load(f)
    return None

def save_creds(data):
    os.makedirs(os.path.dirname(CREDS_PATH), exist_ok=True)
    with open(CREDS_PATH, "w") as f: json.dump(data, f, indent=2)
    os.chmod(CREDS_PATH, 0o600)

def auth_url():
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "response_type": "code",
        "redirect_uri": REDIRECT_URI, "scope": "daily readiness sleep personal heartrate workout session tag"
    })
    print(f"{AUTH_URL}?{params}")

def exchange(code):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code", "code": code,
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": REDIRECT_URI
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as resp: result = json.loads(resp.read())
    result["obtained_at"] = time.time()
    save_creds(result)
    print(json.dumps({"ok": True}))

def get_token():
    creds = load_creds()
    if not creds: sys.exit(1)
    # Oura tokens expire after 24h, refresh if needed
    if creds.get("obtained_at", 0) + creds.get("expires_in", 86400) <= time.time() + 60:
        if "refresh_token" not in creds: print("Token expired, re-auth needed"); sys.exit(1)
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token", "refresh_token": creds["refresh_token"],
            "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET
        }).encode()
        req = urllib.request.Request(TOKEN_URL, data=data, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req) as resp: result = json.loads(resp.read())
        result["obtained_at"] = time.time()
        creds.update(result)
        save_creds(creds)
    print(creds["access_token"])

def set_pat(token):
    """Store a Personal Access Token directly."""
    save_creds({"access_token": token, "token_type": "Bearer", "expires_in": 999999999, "obtained_at": time.time()})
    print(json.dumps({"ok": True, "method": "pat"}))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "token"
    if cmd == "url": auth_url()
    elif cmd == "exchange": exchange(sys.argv[2])
    elif cmd == "token": get_token()
    elif cmd == "pat": set_pat(sys.argv[2])

#!/usr/bin/env python3
"""Strava OAuth2 token management."""
import json, sys, os, urllib.request, urllib.parse, time

CREDS_PATH = os.environ.get("STRAVA_CREDS", "/data/.clawdbot/credentials/strava.json")
CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET", "")
TOKEN_URL = "https://www.strava.com/oauth/token"

def load_creds():
    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH) as f: return json.load(f)
    return None

def save_creds(data):
    os.makedirs(os.path.dirname(CREDS_PATH), exist_ok=True)
    with open(CREDS_PATH, "w") as f: json.dump(data, f, indent=2)
    os.chmod(CREDS_PATH, 0o600)

def get_token():
    creds = load_creds()
    if not creds: sys.exit(1)
    if creds.get("expires_at", 0) <= time.time() + 60:
        data = urllib.parse.urlencode({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": creds["refresh_token"], "grant_type": "refresh_token"}).encode()
        req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req) as resp: result = json.loads(resp.read())
        creds.update(result)
        save_creds(creds)
    print(creds["access_token"])

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "token"
    if cmd == "token": get_token()
    elif cmd == "url": print(f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost&scope=read,activity:read_all,profile:read_all&approval_prompt=auto")
    elif cmd == "exchange":
        code = sys.argv[2]
        data = urllib.parse.urlencode({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code, "grant_type": "authorization_code"}).encode()
        req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
        with urllib.request.urlopen(req) as resp: result = json.loads(resp.read())
        save_creds(result)
        print(json.dumps({"ok": True, "athlete": result.get("athlete", {}).get("firstname", "unknown")}))

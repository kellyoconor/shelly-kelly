#!/usr/bin/env python3
"""Google Calendar OAuth reauthorization helper."""

import json
import os
import urllib.request
import urllib.parse
from secrets import token_urlsafe

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

def get_auth_url():
    """Generate OAuth authorization URL."""
    if not CLIENT_ID:
        print("❌ GOOGLE_CLIENT_ID not found in environment")
        return
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": "http://localhost:8080",
        "scope": "https://www.googleapis.com/auth/calendar.readonly",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": token_urlsafe(16)
    }
    
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    print("🔗 Go to this URL to authorize calendar access:")
    print()
    print(url)
    print()
    print("After you authorize, you'll be redirected to localhost:8080 with a 'code' parameter.")
    print("Copy just the code value and paste it here:")

def exchange_code_for_token(auth_code):
    """Exchange authorization code for refresh token."""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8080"
    }).encode()
    
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    
    try:
        with urllib.request.urlopen(req) as resp:
            response = json.loads(resp.read())
            
        if "refresh_token" in response:
            print("✅ Success! Got new refresh token:")
            print(f"GOOGLE_REFRESH_TOKEN={response['refresh_token']}")
            print()
            print("Copy this token and update your environment.")
            return response["refresh_token"]
        else:
            print("❌ No refresh token in response. Try again with prompt=consent")
            print("Full response:", json.dumps(response, indent=2))
            
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Code provided as argument
        auth_code = sys.argv[1]
        exchange_code_for_token(auth_code)
    else:
        # Generate auth URL
        get_auth_url()
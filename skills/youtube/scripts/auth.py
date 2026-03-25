#!/usr/bin/env python3
"""YouTube OAuth2 token management."""
import json, sys, os, urllib.request, urllib.parse, time, webbrowser
import http.server, socketserver, threading
from urllib.parse import urlparse, parse_qs

CREDS_PATH = os.environ.get("YOUTUBE_CREDS", "/data/.clawdbot/credentials/youtube.json")
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI", "http://localhost:8080")
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"

# YouTube API scopes
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback"""
    def do_GET(self):
        if self.path.startswith('/?'):
            # Parse the authorization code from callback
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authorization successful!</h1><p>You can close this window.</p></body></html>")
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html') 
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authorization failed!</h1></body></html>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

def load_creds():
    """Load stored credentials"""
    if os.path.exists(CREDS_PATH):
        try:
            with open(CREDS_PATH) as f: 
                return json.load(f)
        except:
            return None
    return None

def save_creds(data):
    """Save credentials securely"""
    os.makedirs(os.path.dirname(CREDS_PATH), exist_ok=True)
    with open(CREDS_PATH, "w") as f: 
        json.dump(data, f, indent=2)
    os.chmod(CREDS_PATH, 0o600)

def refresh_token(refresh_token):
    """Refresh access token using refresh token"""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode()
    
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urllib.request.urlopen(req) as resp: 
            result = json.loads(resp.read())
            return result
    except Exception as e:
        return {"error": f"Token refresh failed: {e}"}

def exchange_code(auth_code):
    """Exchange authorization code for tokens"""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }).encode()
    
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result
    except Exception as e:
        return {"error": f"Code exchange failed: {e}"}

def get_auth_url():
    """Generate OAuth authorization URL"""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{AUTH_URL}?" + urllib.parse.urlencode(params)

def run_auth_flow():
    """Run the complete OAuth flow"""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: YouTube credentials not set. Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET environment variables.")
        return False
    
    # Start local server to handle callback
    port = int(urlparse(REDIRECT_URI).port or 8080)
    
    with socketserver.TCPServer(("", port), CallbackHandler) as httpd:
        httpd.auth_code = None
        
        # Open authorization URL in browser
        auth_url = get_auth_url()
        print(f"Opening browser for YouTube authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)
        
        print(f"Waiting for authorization on http://localhost:{port}")
        
        # Handle one request (the callback)
        httpd.handle_request()
        
        if hasattr(httpd, 'auth_code') and httpd.auth_code:
            print("Authorization code received, exchanging for tokens...")
            
            # Exchange code for tokens
            result = exchange_code(httpd.auth_code)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                return False
            
            # Add expiration time
            result["expires_at"] = time.time() + result.get("expires_in", 3600)
            
            # Save credentials
            save_creds(result)
            print("YouTube authentication successful! Credentials saved.")
            return True
        else:
            print("Authorization failed or was cancelled.")
            return False

def get_valid_token():
    """Get a valid access token, refreshing if needed"""
    creds = load_creds()
    if not creds:
        print("No YouTube credentials found. Run 'python3 youtube.py auth' first.")
        sys.exit(1)
    
    # Check if token needs refresh
    if creds.get("expires_at", 0) <= time.time() + 60:
        if "refresh_token" not in creds:
            print("Token expired and no refresh token available. Re-run auth.")
            sys.exit(1)
            
        print("Refreshing YouTube access token...", file=sys.stderr)
        result = refresh_token(creds["refresh_token"])
        
        if "error" in result:
            print(f"Token refresh failed: {result['error']}")
            sys.exit(1)
            
        # Update stored credentials
        creds.update(result)
        creds["expires_at"] = time.time() + result.get("expires_in", 3600)
        save_creds(creds)
    
    return creds["access_token"]

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "token"
    
    if cmd == "token":
        # Just return the access token
        token = get_valid_token()
        print(token)
        
    elif cmd == "auth":
        # Run full OAuth flow
        success = run_auth_flow()
        sys.exit(0 if success else 1)
        
    elif cmd == "url":
        # Just print the auth URL
        print(get_auth_url())
        
    elif cmd == "exchange":
        # Exchange a provided code for tokens
        if len(sys.argv) < 3:
            print("Usage: python3 auth.py exchange <code>")
            sys.exit(1)
            
        code = sys.argv[2]
        result = exchange_code(code)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
            
        result["expires_at"] = time.time() + result.get("expires_in", 3600)
        save_creds(result)
        print("Tokens saved successfully!")
        
    else:
        print(f"Unknown command: {cmd}")
        print("Available commands: auth, token, url, exchange")
        sys.exit(1)

if __name__ == "__main__":
    main()
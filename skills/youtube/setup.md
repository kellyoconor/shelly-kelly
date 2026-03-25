# YouTube Skill Setup

## 1. Get YouTube Data API Credentials

1. **Go to Google Cloud Console:** https://console.cloud.google.com
2. **Create/Select Project:** Create a new project or select existing
3. **Enable YouTube Data API v3:**
   - Go to "APIs & Services" > "Library"
   - Search for "YouTube Data API v3" 
   - Click "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth 2.0 Client IDs"
   - Application Type: "Web application"
   - Authorized redirect URIs: Add `http://localhost:8080`
   - Click "Create"

5. **Download credentials** or copy Client ID and Client Secret

## 2. Set Environment Variables

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export YOUTUBE_CLIENT_ID="your_client_id_here"
export YOUTUBE_CLIENT_SECRET="your_client_secret_here"
export YOUTUBE_REDIRECT_URI="http://localhost:8080"
```

Or create a temporary script:
```bash
#!/bin/bash
export YOUTUBE_CLIENT_ID="your_client_id"
export YOUTUBE_CLIENT_SECRET="your_client_secret"
export YOUTUBE_REDIRECT_URI="http://localhost:8080"
cd /data/workspace/skills/youtube
python3 scripts/youtube.py auth
```

## 3. Authenticate

```bash
cd /data/workspace/skills/youtube
python3 scripts/youtube.py auth
```

This will:
- Open your browser to Google OAuth page
- Ask you to authorize YouTube access  
- Save credentials locally for future use

## 4. Test It Works

```bash
# Test basic access
python3 scripts/youtube.py subscriptions

# Test liked videos  
python3 scripts/youtube.py liked 5

# Search for something
python3 scripts/youtube.py search "running tips"
```

## Notes

- **Privacy:** Watch history requires special permissions (not available publicly anymore)
- **Rate Limits:** YouTube API has daily quotas (usually sufficient for personal use)
- **Scopes:** Currently requests read-only access to YouTube data
- **Storage:** Credentials saved to `/data/.clawdbot/credentials/youtube.json` (secure)

## Integration with Heartbeats

Once working, we can add YouTube context checking to heartbeats:
- "Noticed you've been watching a lot of [topic] videos lately"
- "Based on your subscriptions, you might like [recommendation]"
- Smart conversation starters based on actual interests
---
name: youtube
description: YouTube watch history, liked videos, subscriptions, and search data. Use when understanding Kelly's viewing habits, preferences, or providing video recommendations based on her actual interests.
metadata: { "openclaw": { "emoji": "📺", "requires": { "bins": ["python3"] } } }
---

# YouTube

Access YouTube Data API to understand viewing patterns and preferences. Scripts in `scripts/`.

## Commands

```bash
python3 scripts/youtube.py recent [count]      # Recent watch history
python3 scripts/youtube.py liked [count]       # Recently liked videos  
python3 scripts/youtube.py subscriptions       # Channel subscriptions
python3 scripts/youtube.py search [query]      # Search history
python3 scripts/youtube.py stats               # Overall viewing stats
python3 scripts/youtube.py trending            # What's trending
```

## Setup

1. **Get YouTube Data API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download client secrets

2. **Environment variables:**
   ```bash
   export YOUTUBE_CLIENT_ID="your_client_id"
   export YOUTUBE_CLIENT_SECRET="your_client_secret"  
   export YOUTUBE_REDIRECT_URI="http://localhost:8080"
   ```

3. **First run authentication:**
   ```bash
   python3 scripts/youtube.py auth
   ```
   This opens browser for OAuth flow and saves token locally.

## Data Sources

- **Watch History**: Recently watched videos, duration, timestamps
- **Liked Videos**: Videos you've liked, when liked
- **Subscriptions**: Channels you follow, activity
- **Search History**: What you've searched for
- **Playlists**: Created and saved playlists

Perfect for understanding interests, conversation starters, and personalized recommendations.
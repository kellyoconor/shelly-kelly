#!/usr/bin/env python3
"""YouTube Data API client."""
import json, sys, os, urllib.request, urllib.parse, subprocess
from datetime import datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://www.googleapis.com/youtube/v3"

def get_token():
    """Get valid access token from auth.py"""
    r = subprocess.run([sys.executable, os.path.join(SKILL_DIR, "auth.py"), "token"], capture_output=True, text=True)
    if r.returncode != 0: 
        print(json.dumps({"error": "YouTube auth failed - run 'python3 scripts/youtube.py auth' first"}))
        sys.exit(1)
    return r.stdout.strip()

def api_get(endpoint, params=None):
    """Make authenticated YouTube API request"""
    token = get_token()
    if params is None:
        params = {}
    params['access_token'] = token
    
    url = f"{API_BASE}{endpoint}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req) as resp: 
            return json.loads(resp.read())
    except Exception as e:
        return {"error": f"YouTube API error: {str(e)}"}

def format_duration(duration):
    """Convert YouTube duration (PT4M13S) to readable format"""
    if not duration or not duration.startswith('PT'):
        return "Unknown"
    
    duration = duration[2:]  # Remove PT
    hours = 0
    minutes = 0
    seconds = 0
    
    if 'H' in duration:
        hours = int(duration.split('H')[0])
        duration = duration.split('H')[1]
    if 'M' in duration:
        minutes = int(duration.split('M')[0])
        duration = duration.split('M')[1] if 'M' in duration else duration
    if 'S' in duration:
        seconds = int(duration.replace('S', ''))
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def format_view_count(count):
    """Format view count in readable way"""
    if count >= 1000000:
        return f"{count/1000000:.1f}M views"
    elif count >= 1000:
        return f"{count/1000:.1f}K views"
    else:
        return f"{count} views"

def recent_videos(count=10):
    """Get recently watched videos from history"""
    # Note: YouTube removed public access to watch history in 2022
    # This would need YouTube Analytics API (for channel owners) or user consent
    return {"error": "Watch history requires special permissions - checking liked videos instead"}

def liked_videos(count=10):
    """Get recently liked videos"""
    data = api_get("/videos", {
        "part": "snippet,statistics,contentDetails",
        "myRating": "like",
        "maxResults": count
    })
    
    if "error" in data:
        return data
    
    videos = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        details = item.get("contentDetails", {})
        
        videos.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"], 
            "duration": format_duration(details.get("duration", "")),
            "views": format_view_count(int(stats.get("viewCount", 0))),
            "published": snippet["publishedAt"][:10],
            "url": f"https://youtube.com/watch?v={item['id']}"
        })
    
    return videos

def subscriptions(count=50):
    """Get channel subscriptions"""
    data = api_get("/subscriptions", {
        "part": "snippet",
        "mine": "true",
        "maxResults": count,
        "order": "relevance"
    })
    
    if "error" in data:
        return data
        
    subs = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        subs.append({
            "channel": snippet["title"],
            "description": snippet["description"][:100] + "..." if len(snippet["description"]) > 100 else snippet["description"],
            "subscribed": snippet["publishedAt"][:10]
        })
    
    return subs

def search_videos(query, count=10):
    """Search for videos"""
    data = api_get("/search", {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": count,
        "order": "relevance"
    })
    
    if "error" in data:
        return data
        
    results = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        results.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "published": snippet["publishedAt"][:10],
            "description": snippet["description"][:150] + "..." if len(snippet["description"]) > 150 else snippet["description"],
            "url": f"https://youtube.com/watch?v={item['id']['videoId']}"
        })
    
    return results

def trending_videos(count=20):
    """Get trending videos in US"""
    data = api_get("/videos", {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "US",
        "maxResults": count
    })
    
    if "error" in data:
        return data
        
    trending = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        
        trending.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "views": format_view_count(int(stats.get("viewCount", 0))),
            "published": snippet["publishedAt"][:10],
            "url": f"https://youtube.com/watch?v={item['id']}"
        })
    
    return trending

def user_stats():
    """Get user channel statistics if available"""
    data = api_get("/channels", {
        "part": "snippet,statistics",
        "mine": "true"
    })
    
    if "error" in data:
        return data
        
    if not data.get("items"):
        return {"error": "No channel found - user doesn't have a YouTube channel"}
        
    item = data["items"][0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})
    
    return {
        "channel_name": snippet["title"],
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "created": snippet["publishedAt"][:10]
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 youtube.py <command> [args]")
        print("Commands: auth, recent, liked, subscriptions, search, trending, stats")
        return
        
    cmd = sys.argv[1]
    
    if cmd == "auth":
        # Trigger authentication flow
        subprocess.run([sys.executable, os.path.join(SKILL_DIR, "auth.py"), "auth"])
        return
        
    elif cmd == "recent":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = recent_videos(count)
        
    elif cmd == "liked":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10  
        result = liked_videos(count)
        
    elif cmd == "subscriptions":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        result = subscriptions(count)
        
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 youtube.py search <query>")
            return
        query = " ".join(sys.argv[2:])
        result = search_videos(query)
        
    elif cmd == "trending":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        result = trending_videos(count)
        
    elif cmd == "stats":
        result = user_stats()
        
    else:
        print(f"Unknown command: {cmd}")
        return
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
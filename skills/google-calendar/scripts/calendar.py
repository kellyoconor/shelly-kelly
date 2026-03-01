#!/usr/bin/env python3
"""Google Calendar read-only client using OAuth refresh token."""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", "")

def get_access_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]

def get_events(days=7, max_results=20):
    token = get_access_token()
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days)).isoformat()
    
    params = urllib.parse.urlencode({
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": max_results,
        "singleEvents": "true",
        "orderBy": "startTime"
    })
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def get_today():
    return get_events(days=1)

def get_week():
    return get_events(days=7)

def format_event(event):
    start = event.get("start", {})
    end = event.get("end", {})
    
    # All-day events use 'date', timed events use 'dateTime'
    if "dateTime" in start:
        start_dt = datetime.fromisoformat(start["dateTime"])
        end_dt = datetime.fromisoformat(end["dateTime"])
        time_str = f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
    else:
        time_str = "All day"
    
    summary = event.get("summary", "No title")
    location = event.get("location", "")
    loc_str = f" @ {location}" if location else ""
    
    return f"{time_str}: {summary}{loc_str}"

def format_events(data):
    events = data.get("items", [])
    if not events:
        return "No upcoming events."
    
    output = []
    current_date = None
    for event in events:
        start = event.get("start", {})
        dt_str = start.get("dateTime", start.get("date", ""))
        event_date = dt_str[:10]
        
        if event_date != current_date:
            current_date = event_date
            try:
                d = datetime.fromisoformat(event_date)
                output.append(f"\n{d.strftime('%A, %B %d')}:")
            except:
                output.append(f"\n{event_date}:")
        
        output.append(f"  {format_event(event)}")
    
    return "\n".join(output)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    if cmd == "today":
        data = get_today()
    elif cmd == "week":
        data = get_week()
    elif cmd == "raw":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        data = get_events(days=days)
        print(json.dumps(data, indent=2))
        sys.exit(0)
    else:
        print(f"Usage: {sys.argv[0]} [today|week|raw [days]]")
        sys.exit(1)
    
    print(format_events(data))

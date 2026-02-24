#!/usr/bin/env python3
"""Strava API client."""
import json, sys, os, urllib.request, urllib.parse, subprocess
from datetime import datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://www.strava.com/api/v3"

def get_token():
    r = subprocess.run([sys.executable, os.path.join(SKILL_DIR, "auth.py"), "token"], capture_output=True, text=True)
    if r.returncode != 0: print(json.dumps({"error": "Auth failed"})); sys.exit(1)
    return r.stdout.strip()

def api_get(path, params=None):
    token = get_token()
    url = f"{API_BASE}{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def fmt_dur(s):
    h, r = divmod(int(s), 3600); m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"

def fmt_pace_mi(mps):
    if mps <= 0: return "N/A"
    p = (1609.34 / mps) / 60; return f"{int(p)}:{int((p-int(p))*60):02d}/mi"

def activities(count=10, activity_type=None):
    data = api_get("/athlete/activities", {"per_page": count})
    if activity_type: data = [a for a in data if a.get("type","").lower() == activity_type.lower()]
    for a in data:
        a["_distance_mi"] = round(a.get("distance",0)/1609.34, 2)
        a["_duration"] = fmt_dur(a.get("moving_time",0))
        a["_pace_mi"] = fmt_pace_mi(a.get("average_speed",0))
        a["_date"] = a.get("start_date_local","")[:10]
    print(json.dumps(data, indent=2))

def weekly():
    today = datetime.now(); mon = today - timedelta(days=today.weekday())
    data = api_get("/athlete/activities", {"per_page": 50, "after": int(datetime.strptime(mon.strftime("%Y-%m-%d"),"%Y-%m-%d").timestamp())})
    runs = [a for a in data if a.get("type") == "Run"]
    print(json.dumps({
        "week_of": mon.strftime("%Y-%m-%d"), "total_runs": len(runs),
        "total_miles": round(sum(a.get("distance",0) for a in runs)/1609.34, 2),
        "total_time": fmt_dur(sum(a.get("moving_time",0) for a in runs)),
        "runs": [{"name": a.get("name"), "date": a.get("start_date_local","")[:10],
                  "miles": round(a.get("distance",0)/1609.34, 2), "pace": fmt_pace_mi(a.get("average_speed",0)),
                  "duration": fmt_dur(a.get("moving_time",0)), "hr_avg": a.get("average_heartrate")} for a in runs]
    }, indent=2))

def stats():
    ath = api_get("/athlete"); print(json.dumps(api_get(f"/athletes/{ath['id']}/stats"), indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "runs"
    if cmd == "athlete": print(json.dumps(api_get("/athlete"), indent=2))
    elif cmd == "stats": stats()
    elif cmd == "activities": activities(int(sys.argv[2]) if len(sys.argv)>2 else 10)
    elif cmd == "runs": activities(int(sys.argv[2]) if len(sys.argv)>2 else 10, "Run")
    elif cmd == "weekly": weekly()
    elif cmd == "activity": print(json.dumps(api_get(f"/activities/{sys.argv[2]}"), indent=2))

#!/usr/bin/env python3
"""Oura Ring API client."""
import json, sys, os, urllib.request, urllib.parse, subprocess
from datetime import datetime, timedelta

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://api.ouraring.com/v2/usercollection"

def get_token():
    r = subprocess.run([sys.executable, os.path.join(SKILL_DIR, "auth.py"), "token"], capture_output=True, text=True)
    if r.returncode != 0: print(json.dumps({"error": "Auth failed"})); sys.exit(1)
    return r.stdout.strip()

def api_get(path, params=None):
    token = get_token()
    url = f"{API_BASE}/{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp: return json.loads(resp.read())

def today_str(): return datetime.now().strftime("%Y-%m-%d")
def yesterday_str(): return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def sleep(date=None):
    d = date or yesterday_str()
    data = api_get("sleep", {"start_date": d, "end_date": d})
    for s in data.get("data", []):
        s["_hours"] = round(s.get("total_sleep_duration", 0) / 3600, 1)
        s["_deep_hrs"] = round(s.get("deep_sleep_duration", 0) / 3600, 1)
        s["_rem_hrs"] = round(s.get("rem_sleep_duration", 0) / 3600, 1)
        s["_light_hrs"] = round(s.get("light_sleep_duration", 0) / 3600, 1)
        s["_efficiency"] = s.get("efficiency")
    print(json.dumps(data, indent=2))

def daily_sleep(date=None):
    d = date or yesterday_str()
    data = api_get("daily_sleep", {"start_date": d, "end_date": d})
    print(json.dumps(data, indent=2))

def readiness(date=None):
    d = date or yesterday_str()
    data = api_get("daily_readiness", {"start_date": d, "end_date": d})
    print(json.dumps(data, indent=2))

def activity(date=None):
    d = date or today_str()
    data = api_get("daily_activity", {"start_date": d, "end_date": d})
    print(json.dumps(data, indent=2))

def heartrate(date=None):
    d = date or today_str()
    data = api_get("heartrate", {"start_date": d, "end_date": d})
    # Summarize instead of dumping all readings
    readings = data.get("data", [])
    if readings:
        bpms = [r["bpm"] for r in readings if "bpm" in r]
        summary = {"count": len(bpms), "min": min(bpms), "max": max(bpms), "avg": round(sum(bpms)/len(bpms), 1)}
        print(json.dumps({"date": d, "summary": summary}, indent=2))
    else:
        print(json.dumps({"date": d, "summary": None}, indent=2))

def personal_info():
    token = get_token()
    req = urllib.request.Request("https://api.ouraring.com/v2/usercollection/personal_info",
        headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp: print(json.dumps(json.loads(resp.read()), indent=2))

def daily_brief(date=None):
    """Combined sleep + readiness + activity summary."""
    d = date or today_str()
    today = today_str()
    brief = {"date": d}
    try:
        sl = api_get("daily_sleep", {"start_date": d, "end_date": d})
        if sl.get("data"):
            brief["sleep"] = sl["data"][0]
        elif d == today:
            # Fallback to yesterday if today hasn't synced yet
            yd = yesterday_str()
            sl = api_get("daily_sleep", {"start_date": yd, "end_date": yd})
            if sl.get("data"):
                brief["sleep"] = sl["data"][0]
                brief["sleep_fallback"] = yd
    except: pass
    try:
        rd = api_get("daily_readiness", {"start_date": d, "end_date": d})
        if rd.get("data"):
            brief["readiness"] = rd["data"][0]
        elif d == today:
            yd = yesterday_str()
            rd = api_get("daily_readiness", {"start_date": yd, "end_date": yd})
            if rd.get("data"):
                brief["readiness"] = rd["data"][0]
                brief["readiness_fallback"] = yd
    except: pass
    try:
        act = api_get("daily_activity", {"start_date": today, "end_date": today})
        if act.get("data"): brief["activity"] = act["data"][0]
    except: pass
    try:
        slp = api_get("sleep", {"start_date": d, "end_date": d})
        if slp.get("data"):
            s = slp["data"][-1]  # most recent sleep period
            brief["sleep_detail"] = {
                "total_hours": round(s.get("total_sleep_duration", 0) / 3600, 1),
                "deep_hours": round(s.get("deep_sleep_duration", 0) / 3600, 1),
                "rem_hours": round(s.get("rem_sleep_duration", 0) / 3600, 1),
                "efficiency": s.get("efficiency"),
                "avg_hr": s.get("average_heart_rate"),
                "lowest_hr": s.get("lowest_heart_rate"),
                "hrv_avg": s.get("average_hrv"),
            }
    except: pass
    print(json.dumps(brief, indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "brief"
    date = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "sleep": sleep(date)
    elif cmd == "daily_sleep": daily_sleep(date)
    elif cmd == "readiness": readiness(date)
    elif cmd == "activity": activity(date)
    elif cmd == "heartrate": heartrate(date)
    elif cmd == "info": personal_info()
    elif cmd == "brief": daily_brief(date)

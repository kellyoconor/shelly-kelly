#!/usr/bin/env bash
# bootstrap.sh — runs on every container start (before gateway)
# Installs system deps + ensures config survives redeploys

set -e

# ── System packages (wiped on redeploy) ──────────────────────
echo "[bootstrap] Installing system packages..."
apt-get update -qq
apt-get install -y -qq chromium ffmpeg python3-pip > /dev/null 2>&1
echo "[bootstrap] chromium $(chromium --version 2>/dev/null | grep -oP '[\d.]+')"
echo "[bootstrap] ffmpeg installed"

# ── Python packages (wiped on redeploy) ──────────────────────
echo "[bootstrap] Installing Python packages..."
pip3 install --break-system-packages -q \
  requests python-dotenv faster-whisper websocket-client Pillow agentmail==0.2.22 2>/dev/null
echo "[bootstrap] Python packages installed"

# ── Netty gap detector automation ────────────────────────────
echo "[bootstrap] Setting up Netty gap detector..."
cd /data/workspace
chmod +x netty.py setup-netty-cron.sh
./setup-netty-cron.sh > /dev/null 2>&1
echo "[bootstrap] Netty scheduled (8:30 AM full, 12:30/4:30/8:30 PM light scans)"

# ── Welly always-on monitoring ───────────────────────────
echo "[bootstrap] Starting Welly always-on monitoring..."
cd /data/workspace/welly
python3 welly-daemon.py start > /dev/null 2>&1 || echo "[bootstrap] Welly start failed (may already be running)"
echo "[bootstrap] Welly pattern detection active"

# ── Proactive heartbeat system ──────────────────────────
echo "[bootstrap] Setting up proactive heartbeat..."
# Check if heartbeat cron already exists
if ! openclaw cron list | grep -q "Proactive Heartbeat"; then
    openclaw cron add --name "Proactive Heartbeat" --every 30m --session main --system-event "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK." > /dev/null 2>&1
    echo "[bootstrap] Heartbeat scheduled (every 30 minutes)"
else
    echo "[bootstrap] Heartbeat already configured"
fi

# ── Critical cron jobs (survive redeploys) ──────────────────
echo "[bootstrap] Ensuring critical cron jobs exist..."

# Morning briefings
if ! openclaw cron list | grep -q "Kelly's morning briefing"; then
    openclaw cron add --name "Kelly's morning briefing" --cron "30 6 * * *" --session isolated --message "Generate Kelly's morning briefing with weather, health, calendar, and mirror question. Send via WhatsApp." --timeout-seconds 120 > /dev/null 2>&1
    echo "[bootstrap] Morning briefing restored"
fi

if ! openclaw cron list | grep -q "Emergency Morning Briefing"; then
    openclaw cron add --name "Emergency Morning Briefing" --cron "0 7 * * *" --session isolated --message "Emergency backup briefing if main 6:30 AM briefing failed. Check and send via WhatsApp." --timeout-seconds 60 > /dev/null 2>&1
    echo "[bootstrap] Emergency briefing restored"
fi

# Daily automation
if ! openclaw cron list | grep -q "End-of-Day Summary"; then
    openclaw cron add --name "End-of-Day Summary" --cron "0 23 * * *" --session isolated --message "Create end-of-day summary and write to vault daily note." --timeout-seconds 60 > /dev/null 2>&1
    echo "[bootstrap] End-of-day summary restored"
fi

if ! openclaw cron list | grep -q "Daily Note Creation"; then
    openclaw cron add --name "Daily Note Creation" --cron "0 0 * * *" --session isolated --message "Create tomorrow's daily note template in vault." --timeout-seconds 30 > /dev/null 2>&1
    echo "[bootstrap] Daily note creation restored"
fi

# Security & cleanup
if ! openclaw cron list | grep -q "Nightly Security Review"; then
    openclaw cron add --name "Nightly Security Review" --cron "0 2 * * *" --session isolated --message "Run nightly security review and log results." --timeout-seconds 60 > /dev/null 2>&1
    echo "[bootstrap] Security review restored"
fi

if ! openclaw cron list | grep -q "Proper Session Cleanup"; then
    openclaw cron add --name "Proper Session Cleanup" --cron "0 3 * * *" --session isolated --message "Clean up orphaned session files and maintain system health." --timeout-seconds 60 > /dev/null 2>&1
    echo "[bootstrap] Session cleanup restored"
fi

if ! openclaw cron list | grep -q "Auto Git Push"; then
    openclaw cron add --name "Auto Git Push" --cron "30 3 * * *" --session isolated --message "Auto-commit and push workspace changes." --timeout-seconds 30 > /dev/null 2>&1
    echo "[bootstrap] Auto git push restored"
fi

if ! openclaw cron list | grep -q "WhatsApp Health Check"; then
    openclaw cron add --name "WhatsApp Health Check" --cron "25 6 * * *" --session isolated --message "Check WhatsApp connectivity before morning briefing." --timeout-seconds 30 > /dev/null 2>&1
    echo "[bootstrap] WhatsApp health check restored"
fi

echo "[bootstrap] Critical automation protected"

# ── Daily Note Health Check ─────────────────────────────────
echo "[bootstrap] Verifying daily note system integration..."

# Check if daily-note-append.py exists
if [ ! -f "/data/workspace/scripts/daily-note-append.py" ]; then
    echo "[bootstrap] ERROR: daily-note-append.py missing!"
    exit 1
fi

# Verify morning briefing includes daily note append
MORNING_BRIEFING_CHECK=$(openclaw cron list | jq -r '.jobs[] | select(.name == "Kelly'\''s morning briefing") | .payload.message // ""')
if [[ ! "$MORNING_BRIEFING_CHECK" =~ "daily-note-append.py" ]]; then
    echo "[bootstrap] FIXING: Morning briefing missing daily note integration"
    openclaw cron update --name "Kelly's morning briefing" --patch '{"payload": {"message": "📱 Generate Kelly'\''s morning briefing and send via WhatsApp (accountId: custom-1):\n\n1. Check day, weather, calendar events\n2. Pull Oura data (sleep, readiness, HRV from last night)\n3. Generate Mirror question\n4. Personal check-in: Based on recent context\n5. Check packages/alerts\n6. Send concise 4-line WhatsApp update to +13018302401\n\n**THEN append to daily note:**\n7. python3 /data/workspace/scripts/daily-note-append.py \"Weather: [today'\''s weather]\" \"Weather\"\n8. python3 /data/workspace/scripts/daily-note-append.py \"Health: Sleep [score], Readiness [score], [key insight]\" \"Health\"\n\n**RETRY LOGIC:** If WhatsApp send fails, wait 5 minutes and retry up to 3 times."}}' > /dev/null 2>&1
    echo "[bootstrap] Morning briefing daily note integration restored"
fi

# Verify end-of-day includes synthesis not overwrite
EOD_CHECK=$(openclaw cron list | jq -r '.jobs[] | select(.name == "End-of-Day Summary") | .payload.message // ""')
if [[ ! "$EOD_CHECK" =~ "synthesize" ]] || [[ "$EOD_CHECK" =~ "overwrite" ]]; then
    echo "[bootstrap] FIXING: End-of-day missing synthesis mode"
    openclaw cron update --name "End-of-Day Summary" --patch '{"payload": {"message": "📝 End-of-day daily note synthesis:\n\n1. **Read current daily note**: /data/kelly-vault/01-Daily/2026/YYYY-MM-DD.md\n2. **Check for existing content**: Weather, Health, Events, Thoughts sections\n3. **Gather missing data**: Pull any missing weather, Oura, Strava, calendar data\n4. **Scan conversations**: Review today'\''s session transcripts for key decisions, topics, mood\n5. **SYNTHESIZE, don'\''t overwrite**: Enhance existing appended content with narrative flow\n6. **Add to Thoughts section**: Emotional insights, energy patterns, decision themes\n7. **Add to Events section**: Any major events not already captured\n\n**Goal**: Transform real-time appends into a cohesive story Kelly would want to read later. Preserve all existing content, just make it flow better and fill gaps."}}' > /dev/null 2>&1
    echo "[bootstrap] End-of-day synthesis mode restored"
fi

# Verify HEARTBEAT.md includes daily note real-time updates
if [ ! -f "/data/workspace/HEARTBEAT.md" ] || ! grep -q "daily-note-append.py" /data/workspace/HEARTBEAT.md; then
    echo "[bootstrap] FIXING: HEARTBEAT.md missing daily note integration"
    # This would be fixed by the HEARTBEAT.md updates we already made
    echo "[bootstrap] HEARTBEAT.md daily note integration should be updated via git"
fi

echo "[bootstrap] Daily note health check complete"

# ── Config checks ────────────────────────────────────────────
CONFIG="${OPENCLAW_STATE_DIR:-/data/.clawdbot}/openclaw.json"

if [ -f "$CONFIG" ]; then
  # Re-enable WhatsApp plugin if doctor disabled it
  if python3 -c "
import json, sys
with open('$CONFIG') as f:
    c = json.load(f)
p = c.get('plugins',{}).get('entries',{}).get('whatsapp',{})
if p.get('enabled') == False:
    p['enabled'] = True
    c.setdefault('plugins',{}).setdefault('entries',{})['whatsapp'] = p
    with open('$CONFIG','w') as f:
        json.dump(c, f, indent=2)
    print('WhatsApp plugin re-enabled')
else:
    print('WhatsApp plugin already enabled (or not configured)')
" 2>&1; then
    echo "[bootstrap] WhatsApp check complete"
  fi

  # Ensure WhatsApp channel config exists
  if ! python3 -c "
import json
with open('$CONFIG') as f:
    c = json.load(f)
wa = c.get('channels',{}).get('whatsapp',{})
if not wa.get('selfChatMode'):
    raise SystemExit(1)
" 2>/dev/null; then
    python3 -c "
import json
with open('$CONFIG') as f:
    c = json.load(f)
c.setdefault('channels',{})['whatsapp'] = {
    'selfChatMode': True,
    'dmPolicy': 'allowlist',
    'allowFrom': ['+13018302401'],
    'accounts': {
        'custom-1': {
            'dmPolicy': 'allowlist',
            'groupPolicy': 'allowlist',
            'debounceMs': 0
        }
    }
}
with open('$CONFIG','w') as f:
    json.dump(c, f, indent=2)
print('WhatsApp channel config restored')
"
    echo "[bootstrap] WhatsApp config check complete"
  fi
fi

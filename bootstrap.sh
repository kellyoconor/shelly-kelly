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

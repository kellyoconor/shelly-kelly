#!/usr/bin/env bash
# bootstrap.sh — runs on every container start (before gateway)
# Ensures WhatsApp plugin stays enabled after doctor/redeploy

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

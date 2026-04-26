#!/usr/bin/env bash
set -euo pipefail
OUT=/tmp/nightly-security-review-2026-04-26.txt
{
  echo '=== AUTO-REDACT ==='
  python3 /data/workspace/scripts/auto-redact-credentials.py || true

  echo
  echo '=== SECRET SCAN: sk- in workspace text files (excluding openclaw.json and .spotify_cache) ==='
  grep -RIn --include='*.md' --include='*.txt' --include='*.json' \
    --exclude='openclaw.json' --exclude='.spotify_cache' 'sk-' /data/workspace || true

  echo
  echo '=== GIT COMMITS LAST 24H ==='
  git -C /data/workspace log --since='24 hours ago' --stat --oneline || true

  echo
  echo '=== CLAWDBOT CONFIG PERMS ==='
  stat -c '%a %U %G %n' /data/.clawdbot/openclaw.json || true

  echo
  echo '=== CLAWDBOT CONFIG REDACTION CHECK (sensitive-looking values redacted in file preview) ==='
  python3 - <<'PY'
import json, re
p='/data/.clawdbot/openclaw.json'
try:
    with open(p) as f:
        data=json.load(f)
except Exception as e:
    print(f'ERROR reading {p}: {e}')
    raise SystemExit(0)
patterns=[re.compile(r'(api[_-]?key|token|secret|password)', re.I)]

def walk(obj, path=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            np=f'{path}.{k}' if path else k
            if any(p.search(k) for p in patterns):
                if isinstance(v, str):
                    red=v[:2]+'***REDACTED***'+v[-2:] if len(v)>4 else '***REDACTED***'
                else:
                    red='***REDACTED***'
                print(np, '=', red)
            else:
                walk(v, np)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            walk(v, f'{path}[{i}]')
walk(data)
PY

  echo
  echo '=== UNKNOWN PROCESSES / PROCESS LIST ==='
  ps aux || true

  echo
  echo '=== DISK USAGE ==='
  df -h || true

  echo
  echo '=== WHATSAPP ALLOWLIST CHECK ==='
  python3 - <<'PY'
import json
p='/data/.clawdbot/openclaw.json'
try:
    with open(p) as f:
        data=json.load(f)
except Exception as e:
    print(f'ERROR reading {p}: {e}')
    raise SystemExit(0)
results=[]

def walk(obj, path=''):
    if isinstance(obj, dict):
        for k,v in obj.items():
            np=f'{path}.{k}' if path else k
            if k.lower()=='allowlist':
                results.append((np,v))
            walk(v, np)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            walk(v, f'{path}[{i}]')
walk(data)
if not results:
    print('NO_ALLOWLIST_FOUND')
else:
    for p,v in results:
        print(p, '=', json.dumps(v))
PY

  echo
  echo '=== HARDCODED CREDENTIAL SCAN ==='
  python3 - <<'PY'
from pathlib import Path
import re
root=Path('/data/workspace')
exclude_names={'openclaw.json','.spotify_cache'}
exclude_dirs={'.git','node_modules','.venv','venv','__pycache__'}
patterns=[
    ('openai_sk', re.compile(r'sk-[A-Za-z0-9_-]{10,}')),
    ('ghp', re.compile(r'ghp_[A-Za-z0-9]{20,}')),
    ('github_pat', re.compile(r'github_pat_[A-Za-z0-9_]{20,}')),
    ('slack', re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}')),
    ('aws_access_key', re.compile(r'AKIA[0-9A-Z]{16}')),
    ('generic_assignment', re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{12,}")),
]
for path in root.rglob('*'):
    if not path.is_file():
        continue
    if path.name in exclude_names:
        continue
    if any(part in exclude_dirs for part in path.parts):
        continue
    if path.suffix.lower() not in {'.md','.txt','.json','.py','.js','.ts','.sh','.yaml','.yml','.env','.cfg','.ini'}:
        continue
    try:
        text=path.read_text(errors='ignore')
    except Exception:
        continue
    hits=[]
    for name,pat in patterns:
        m=pat.search(text)
        if m:
            hits.append(name)
    if hits:
        print(f'{path}: {", ".join(hits)}')
PY
} > "$OUT" 2>&1
printf '%s\n' "$OUT"

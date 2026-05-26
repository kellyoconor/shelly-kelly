#!/usr/bin/env python3
"""
Kelly follow-up tracker
Stores structured open loops so Shelly can circle back with continuity,
plus lightweight lifecycle management for surfaced/resolved/stale items.
"""

import json
import os
import sys
from datetime import datetime, timedelta

FOLLOWUPS_FILE = os.environ.get('KELLY_FOLLOWUPS_FILE', '/data/workspace/memory/kelly-followups.json')
STALE_AFTER_DAYS = int(os.environ.get('KELLY_FOLLOWUPS_STALE_DAYS', '14'))
RESURFACE_AFTER_HOURS = int(os.environ.get('KELLY_FOLLOWUPS_RESURFACE_HOURS', '18'))

ACTIVE_STATUSES = {'open', 'surfaced'}
PRIORITY_RANK = {
    'critical': 0,
    'high': 1,
    'medium': 2,
    'low': 3,
}


def now_iso():
    return datetime.now().isoformat()


def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_followups():
    try:
        with open(FOLLOWUPS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'items' in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {'updated_at': None, 'items': []}


def save_followups(data):
    os.makedirs(os.path.dirname(FOLLOWUPS_FILE), exist_ok=True)
    data['updated_at'] = now_iso()
    with open(FOLLOWUPS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def next_id(items):
    max_num = 0
    for item in items:
        item_id = item.get('id', '')
        if item_id.startswith('fu-'):
            try:
                max_num = max(max_num, int(item_id.split('-')[1]))
            except (ValueError, IndexError):
                pass
    return f'fu-{max_num + 1:03d}'


def normalize_topic(topic):
    return ' '.join((topic or '').strip().lower().split())


def find_existing_open_followup(items, topic):
    normalized = normalize_topic(topic)
    for item in items:
        if item.get('status') in ACTIVE_STATUSES and normalize_topic(item.get('topic')) == normalized:
            return item
    return None


def add_followup(topic, note, kind='general', priority='medium'):
    data = load_followups()
    existing = find_existing_open_followup(data['items'], topic)
    if existing:
        existing['note'] = note.strip()
        existing['kind'] = kind.strip()
        existing['priority'] = priority.strip()
        existing['last_seen'] = now_iso()
        save_followups(data)
        return existing

    item = {
        'id': next_id(data['items']),
        'topic': topic.strip(),
        'note': note.strip(),
        'kind': kind.strip(),
        'priority': priority.strip(),
        'status': 'open',
        'created_at': now_iso(),
        'last_seen': now_iso(),
        'last_surfaced': None,
        'times_surfaced': 0,
        'resolved_at': None,
        'stale_at': None,
    }
    data['items'].append(item)
    save_followups(data)
    return item


def touch_followup(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id:
            item['last_seen'] = now_iso()
            if item.get('status') == 'stale':
                item['status'] = 'open'
                item['stale_at'] = None
            save_followups(data)
            return item
    return None


def resolve_followup(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id:
            item['status'] = 'resolved'
            item['resolved_at'] = now_iso()
            save_followups(data)
            return item
    return None


def stale_followup(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id and item.get('status') != 'resolved':
            item['status'] = 'stale'
            item['stale_at'] = now_iso()
            save_followups(data)
            return item
    return None


def mark_surfaced(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id:
            item['status'] = 'surfaced'
            item['last_surfaced'] = now_iso()
            item['times_surfaced'] = int(item.get('times_surfaced', 0)) + 1
            save_followups(data)
            return item
    return None


def sort_seconds(value):
    dt = parse_dt(value)
    if not dt:
        return float('-inf')
    epoch = datetime(1970, 1, 1)
    return (dt - epoch).total_seconds()


def apply_lifecycle_rules(data):
    changed = False
    cutoff = datetime.now() - timedelta(days=STALE_AFTER_DAYS)

    for item in data['items']:
        status = item.get('status')
        if status == 'resolved':
            continue

        last_seen = parse_dt(item.get('last_seen')) or parse_dt(item.get('created_at'))
        last_surfaced = parse_dt(item.get('last_surfaced'))

        if last_seen and last_seen < cutoff and status in ACTIVE_STATUSES:
            item['status'] = 'stale'
            item['stale_at'] = now_iso()
            changed = True
            continue

        if status == 'surfaced' and last_surfaced:
            if datetime.now() - last_surfaced >= timedelta(hours=RESURFACE_AFTER_HOURS):
                item['status'] = 'open'
                changed = True

    return changed


def list_followups(status='open'):
    data = load_followups()
    changed = apply_lifecycle_rules(data)
    if changed:
        save_followups(data)

    items = data['items']
    if status != 'all':
        items = [item for item in items if item.get('status') == status]
    return items


def active_followups(limit=None):
    items = list_followups('all')
    active = [item for item in items if item.get('status') in ACTIVE_STATUSES]
    active.sort(key=lambda item: (
        item.get('status') != 'open',
        PRIORITY_RANK.get(item.get('priority', 'medium'), PRIORITY_RANK['medium']),
        -max(sort_seconds(item.get('last_seen')), sort_seconds(item.get('created_at'))),
        int(item.get('times_surfaced', 0)),
    ))
    return active[:limit] if limit else active


def summarize_followups(limit=3):
    items = active_followups(limit)
    if not items:
        return ''
    return '; '.join(f"{item['topic']} ({item['kind']})" for item in items)


def get_next_followup(limit=1):
    items = active_followups(limit)
    return items[0] if items else None


def print_usage():
    print('Usage:')
    print('  kelly-followups.py add <topic> <note> [kind] [priority]')
    print('  kelly-followups.py list [open|surfaced|resolved|stale|all]')
    print('  kelly-followups.py next')
    print('  kelly-followups.py touch <id>')
    print('  kelly-followups.py surfaced <id>')
    print('  kelly-followups.py resolve <id>')
    print('  kelly-followups.py stale <id>')
    print('  kelly-followups.py summary [limit]')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == 'add' and len(sys.argv) >= 4:
        item = add_followup(
            sys.argv[2],
            sys.argv[3],
            sys.argv[4] if len(sys.argv) >= 5 else 'general',
            sys.argv[5] if len(sys.argv) >= 6 else 'medium',
        )
        print(json.dumps(item, indent=2))
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) >= 3 else 'open'
        print(json.dumps(list_followups(status), indent=2))
    elif command == 'next':
        item = get_next_followup()
        if item:
            print(json.dumps(item, indent=2))
            sys.exit(0)
        sys.exit(1)
    elif command == 'touch' and len(sys.argv) >= 3:
        item = touch_followup(sys.argv[2])
        if item:
            print(json.dumps(item, indent=2))
            sys.exit(0)
        sys.exit(1)
    elif command == 'resolve' and len(sys.argv) >= 3:
        item = resolve_followup(sys.argv[2])
        if item:
            print(json.dumps(item, indent=2))
            sys.exit(0)
        sys.exit(1)
    elif command == 'stale' and len(sys.argv) >= 3:
        item = stale_followup(sys.argv[2])
        if item:
            print(json.dumps(item, indent=2))
            sys.exit(0)
        sys.exit(1)
    elif command == 'summary':
        limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
        print(summarize_followups(limit))
    elif command == 'surfaced' and len(sys.argv) >= 3:
        item = mark_surfaced(sys.argv[2])
        if item:
            print(json.dumps(item, indent=2))
            sys.exit(0)
        sys.exit(1)
    else:
        print_usage()
        sys.exit(1)

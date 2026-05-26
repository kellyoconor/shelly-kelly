#!/usr/bin/env python3
"""
Kelly follow-up tracker
Stores small structured open loops so Shelly can circle back with continuity.
"""

import json
import os
import sys
from datetime import datetime

FOLLOWUPS_FILE = '/data/workspace/memory/kelly-followups.json'


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
    data['updated_at'] = datetime.now().isoformat()
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


def add_followup(topic, note, kind='general', priority='medium'):
    data = load_followups()
    item = {
        'id': next_id(data['items']),
        'topic': topic.strip(),
        'note': note.strip(),
        'kind': kind.strip(),
        'priority': priority.strip(),
        'status': 'open',
        'created_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'last_surfaced': None,
    }
    data['items'].append(item)
    save_followups(data)
    return item


def list_followups(status='open'):
    data = load_followups()
    items = data['items']
    if status != 'all':
        items = [item for item in items if item.get('status') == status]
    return items


def resolve_followup(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id:
            item['status'] = 'resolved'
            item['resolved_at'] = datetime.now().isoformat()
            save_followups(data)
            return item
    return None


def summarize_followups(limit=3):
    items = list_followups('open')[:limit]
    if not items:
        return ''

    bits = []
    for item in items:
        bits.append(f"{item['topic']} ({item['kind']})")
    return '; '.join(bits)


def mark_surfaced(item_id):
    data = load_followups()
    for item in data['items']:
        if item.get('id') == item_id:
            item['last_surfaced'] = datetime.now().isoformat()
            save_followups(data)
            return item
    return None


def print_usage():
    print('Usage:')
    print('  kelly-followups.py add <topic> <note> [kind] [priority]')
    print('  kelly-followups.py list [open|resolved|all]')
    print('  kelly-followups.py resolve <id>')
    print('  kelly-followups.py summary [limit]')
    print('  kelly-followups.py surfaced <id>')


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
    elif command == 'resolve' and len(sys.argv) >= 3:
        item = resolve_followup(sys.argv[2])
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

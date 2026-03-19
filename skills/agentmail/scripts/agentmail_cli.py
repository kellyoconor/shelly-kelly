#!/usr/bin/env python3
"""
AgentMail client for Shelly's inbox (shelly@agentmail.to)
Updated for AgentMail's current message-based API (no more threads)
"""

import json
import os
import sys
from typing import Dict, List, Optional
from agentmail import AgentMail
from collections import defaultdict

def load_credentials() -> Dict:
    """Load AgentMail credentials from OpenClaw config."""
    creds_path = "/data/.clawdbot/credentials/agentmail.json"
    try:
        with open(creds_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"AgentMail credentials not found at {creds_path}")

def get_client():
    """Initialize AgentMail client with credentials."""
    creds = load_credentials()
    return AgentMail(api_key=creds["api_key"])

def list_messages(limit: int = 20) -> Dict:
    """List recent messages in Shelly's inbox, grouped by subject for thread-like view."""
    client = get_client()
    creds = load_credentials()
    
    try:
        response = client.inboxes.messages.list(
            inbox_id=creds["inbox"],
            limit=limit
        )
        
        # Group messages by subject to simulate thread behavior
        threads_map = defaultdict(list)
        for message in response.messages:
            subject = message.subject or "No Subject"
            threads_map[subject].append(message)
        
        # Convert to thread-like structure
        threads_data = []
        for subject, messages in threads_map.items():
            # Use the most recent message as the representative
            latest_msg = max(messages, key=lambda m: m.created_at)
            
            threads_data.append({
                "thread_id": f"subject-{hash(subject)}", # Fake thread ID for compatibility
                "subject": subject,
                "senders": list(set([msg.from_ for msg in messages])),
                "recipients": list(set([creds.get("email", "shelly@agentmail.to")])), 
                "preview": (getattr(latest_msg, 'preview', '') or "")[:200],
                "message_count": len(messages),
                "labels": latest_msg.labels if hasattr(latest_msg, 'labels') else [],
                "timestamp": latest_msg.timestamp.isoformat(),
                "updated_at": latest_msg.updated_at.isoformat()
            })
            
        # Sort by timestamp, most recent first
        threads_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            "count": len(threads_data),
            "limit": limit,
            "threads": threads_data
        }
    except Exception as e:
        return {"error": str(e)}

def get_message(message_id: str) -> Dict:
    """Get a specific message by ID."""
    client = get_client()
    creds = load_credentials()
    
    try:
        # Since there's no direct get by ID, we'll list and find it
        response = client.inboxes.messages.list(inbox_id=creds["inbox"], limit=50)
        
        for message in response.messages:
            if message.message_id == message_id:
                return {
                    "message_id": message.message_id,
                    "subject": message.subject,
                    "sender": message.from_,
                    "created_at": message.timestamp.isoformat(),
                    "preview": getattr(message, 'preview', ''),
                    "labels": getattr(message, 'labels', [])
                }
        
        return {"error": f"Message {message_id} not found"}
    except Exception as e:
        return {"error": str(e)}

def get_messages_by_subject(subject: str) -> Dict:
    """Get all messages with a specific subject (thread simulation)."""
    client = get_client()
    creds = load_credentials()
    
    try:
        response = client.inboxes.messages.list(inbox_id=creds["inbox"], limit=50)
        
        matching_messages = []
        for message in response.messages:
            if message.subject == subject:
                matching_messages.append({
                    "message_id": message.message_id,
                    "subject": message.subject,
                    "sender": message.from_,
                    "created_at": message.timestamp.isoformat(),
                    "preview": getattr(message, 'preview', ''),
                    "labels": getattr(message, 'labels', [])
                })
        
        return {"messages": matching_messages}
    except Exception as e:
        return {"error": str(e)}

def send_message(to: str, subject: str, text: str, html: str = None) -> Dict:
    """Send an email from Shelly's inbox."""
    client = get_client()
    creds = load_credentials()
    
    try:
        kwargs = {
            "inbox_id": creds["inbox"],
            "to": to,
            "subject": subject,
            "text": text
        }
        if html:
            kwargs["html"] = html
            
        message = client.inboxes.messages.send(**kwargs)
        return {"success": True, "message_id": getattr(message, 'message_id', None)}
    except Exception as e:
        return {"error": str(e)}

def inbox_status() -> Dict:
    """Get inbox status and recent activity."""
    client = get_client()
    creds = load_credentials()
    
    try:
        # Get recent messages
        response = client.inboxes.messages.list(inbox_id=creds["inbox"], limit=10)
        
        subjects = [msg.subject for msg in response.messages]
        
        return {
            "inbox": creds["inbox"],
            "status": "connected",
            "total_recent_messages": len(response.messages),
            "recent_subjects": subjects[:5]
        }
    except Exception as e:
        return {"error": str(e), "inbox": creds.get("inbox", "unknown"), "status": "error"}

def main():
    """CLI interface for AgentMail operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentMail CLI for Shelly's inbox")
    parser.add_argument("command", choices=[
        "status", "threads", "messages", "message", "send"
    ])
    parser.add_argument("--message-id", help="Message ID for message command")
    parser.add_argument("--subject", help="Subject for messages command or send command")
    parser.add_argument("--to", help="Recipient email for send command")
    parser.add_argument("--text", help="Message text for send command")
    parser.add_argument("--html", help="HTML content for send command")
    parser.add_argument("--limit", type=int, default=20, help="Limit for threads command")
    
    args = parser.parse_args()
    
    try:
        if args.command == "status":
            result = inbox_status()
        elif args.command == "threads":
            result = list_messages(limit=args.limit)
        elif args.command == "messages":
            if not args.subject:
                print("Error: --subject required for messages command")
                return
            result = get_messages_by_subject(args.subject)
        elif args.command == "message":
            if not args.message_id:
                print("Error: --message-id required for message command")
                return
            result = get_message(args.message_id)
        elif args.command == "send":
            if not all([args.to, args.subject, args.text]):
                print("Error: --to, --subject, and --text required for send command")
                return
            result = send_message(args.to, args.subject, args.text, args.html)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
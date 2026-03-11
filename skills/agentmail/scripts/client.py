#!/usr/bin/env python3
"""
AgentMail client for Shelly's inbox (shelly@agentmail.to)
"""

import json
import os
import sys
from typing import Dict, List, Optional
from agentmail import AgentMail

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

def list_threads(limit: int = 20) -> Dict:
    """List recent email threads in Shelly's inbox."""
    client = get_client()
    creds = load_credentials()
    
    try:
        response = client.inboxes.threads.list(
            inbox_id=creds["inbox"],
            limit=limit
        )
        
        # Convert thread objects to dictionaries for JSON serialization
        threads_data = []
        for thread in response.threads:
            threads_data.append({
                "thread_id": thread.thread_id,
                "subject": thread.subject,
                "senders": thread.senders,
                "recipients": thread.recipients,
                "preview": thread.preview[:200] + "..." if len(thread.preview) > 200 else thread.preview,
                "message_count": thread.message_count,
                "labels": thread.labels,
                "timestamp": thread.timestamp.isoformat(),
                "updated_at": thread.updated_at.isoformat()
            })
            
        return {
            "count": response.count,
            "limit": response.limit,
            "threads": threads_data
        }
    except Exception as e:
        return {"error": str(e)}

def get_thread(thread_id: str) -> Dict:
    """Get details for a specific thread."""
    client = get_client()
    creds = load_credentials()
    
    try:
        thread = client.inboxes.threads.retrieve(
            inbox_id=creds["inbox"],
            thread_id=thread_id
        )
        return {"thread": thread}
    except Exception as e:
        return {"error": str(e)}

def get_messages(thread_id: str) -> Dict:
    """Get messages in a thread."""
    client = get_client()
    creds = load_credentials()
    
    try:
        messages = client.inboxes.messages.list(
            inbox_id=creds["inbox"],
            thread_id=thread_id
        )
        return {"messages": messages}
    except Exception as e:
        return {"error": str(e)}

def send_message(to: str, subject: str, text: str) -> Dict:
    """Send an email from Shelly's inbox."""
    client = get_client()
    creds = load_credentials()
    
    try:
        message = client.inboxes.messages.send(
            inbox_id=creds["inbox"],
            to=to,
            subject=subject,
            text=text
        )
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}

def inbox_status() -> Dict:
    """Get inbox status and recent activity."""
    client = get_client()
    creds = load_credentials()
    
    try:
        # Get recent threads
        threads_response = client.inboxes.threads.list(
            inbox_id=creds["inbox"],
            limit=5
        )
        
        # Count unread threads
        unread_count = 0
        recent_subjects = []
        for thread in threads_response.threads:
            if 'unread' in thread.labels:
                unread_count += 1
            recent_subjects.append(thread.subject)
        
        return {
            "inbox": creds["inbox"],
            "status": "connected",
            "total_recent_threads": threads_response.count,
            "unread_count": unread_count,
            "recent_subjects": recent_subjects
        }
    except Exception as e:
        return {"error": str(e), "inbox": creds["inbox"], "status": "error"}

def main():
    """CLI interface for AgentMail operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentMail CLI for Shelly's inbox")
    parser.add_argument("command", choices=[
        "status", "threads", "thread", "messages", "send"
    ])
    parser.add_argument("--thread-id", help="Thread ID for thread/messages commands")
    parser.add_argument("--to", help="Recipient email for send command")
    parser.add_argument("--subject", help="Subject for send command")
    parser.add_argument("--text", help="Message text for send command")
    parser.add_argument("--limit", type=int, default=20, help="Limit for threads command")
    
    args = parser.parse_args()
    
    try:
        if args.command == "status":
            result = inbox_status()
        elif args.command == "threads":
            result = list_threads(limit=args.limit)
        elif args.command == "thread":
            if not args.thread_id:
                print("Error: --thread-id required for thread command")
                return
            result = get_thread(args.thread_id)
        elif args.command == "messages":
            if not args.thread_id:
                print("Error: --thread-id required for messages command")
                return
            result = get_messages(args.thread_id)
        elif args.command == "send":
            if not all([args.to, args.subject, args.text]):
                print("Error: --to, --subject, and --text required for send command")
                return
            result = send_message(args.to, args.subject, args.text)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
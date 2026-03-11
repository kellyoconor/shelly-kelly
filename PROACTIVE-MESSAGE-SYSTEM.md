# 📱 WhatsApp Proactive Message Reliability System

## Overview

This system solves the "Kelly doesn't see my important check-ins" problem by tracking proactive messages and automatically retrying them if no response is received within 35 minutes.

## Quick Start for Shelly

### When Sending Important Proactive Messages

Instead of just using the `message` tool directly, use the tracking system:

**Option 1: Use the helper script (easiest)**
```bash
./send-proactive "Hey! How are you feeling about tonight's NWSL game?" nwsl
./send-proactive "Quick wellness check - how's your energy today?" wellness  
./send-proactive "Any thoughts on Atlanta plans for this weekend?" atlanta
```

**Option 2: Manual tracking**
```bash
# Log the message first
node proactive-tracker.cjs log "Your message here" category

# Then send normally with message tool
# The system will track it automatically
```

### What Gets Tracked

**Track these types of messages:**
- ✅ NWSL feelings/reactions check-ins
- ✅ Atlanta weekend plans
- ✅ Wellness/energy check-ins  
- ✅ Important personal questions
- ✅ Emotional support messages

**Don't track these:**
- ❌ Casual responses to Kelly's messages
- ❌ Information delivery (news, schedules)
- ❌ Acknowledgments ("got it!", "sounds good")
- ❌ Follow-ups to active conversations

### Categories

Use these category tags to organize:
- `nwsl` - Soccer/NWSL related check-ins
- `wellness` - Health/energy/mood check-ins
- `atlanta` - Weekend plans and activities
- `support` - Emotional support messages
- `check-in` - General personal check-ins (default)

## How It Works

1. **Send a proactive message** → Gets logged with unique ID
2. **35 minutes pass** with no response → System flags for retry
3. **Heartbeat or cron runs** → Detects flagged message
4. **Retry sent automatically** → Original message + "Just making sure this got through! 📱"
5. **Kelly responds** → Auto-detected and marked as received

## Automation Setup

### In Heartbeats (Add to HEARTBEAT.md)

Add this to your heartbeat checklist:
```javascript
// Check for proactive message retries
exec('node /data/workspace/check-proactive-retries.cjs auto', {cwd: '/data/workspace'});
```

### As Cron Job (Alternative)

```bash
# Check every 20 minutes for retries
*/20 * * * * cd /data/workspace && node check-proactive-retries.cjs auto
```

## Commands Reference

### Logging Messages
```bash
# Log a new proactive message
node proactive-tracker.cjs log "message content" [category]

# Examples
node proactive-tracker.cjs log "How are you feeling about the game?" nwsl
node proactive-tracker.cjs log "Weekend plans?" atlanta
```

### Checking Status
```bash
# See recent message status
node proactive-tracker.cjs status

# Check what needs retries
node proactive-tracker.cjs check-retries
```

### Manual Response Marking
```bash
# Mark specific message as responded
node proactive-tracker.cjs respond <message_id>

# Auto-mark recent messages (when Kelly responds to anything)
node proactive-tracker.cjs auto-respond [minutes_back]
```

### Retry Management
```bash
# Check for needed retries (no action)
node check-proactive-retries.cjs check

# Auto-mark responses and send retries
node check-proactive-retries.cjs auto

# Just auto-mark recent responses
node check-proactive-retries.cjs auto-mark
```

## Files Created

- `proactive-messages.json` - Tracking database
- `proactive-tracker.cjs` - Main tracking script
- `send-proactive` - Helper script for easy sending
- `check-proactive-retries.cjs` - Retry automation

## Response Detection

The system automatically detects responses in two ways:

1. **Auto-marking**: When Kelly responds to anything, recent proactive messages (last 45 min) are marked as responded
2. **Manual marking**: You can specifically mark a message ID as responded

## Retry Logic

- **Timing**: 35 minutes after original message
- **Format**: Original message + "(Just making sure this got through! 📱)"
- **Limit**: Only one retry per message
- **Spacing**: 2 second delay between multiple retries to avoid spam

## Integration with Existing Workflow

### When Kelly Responds to Anything

If you notice Kelly responding, you can auto-mark recent proactive messages:
```bash
node proactive-tracker.cjs auto-respond
```

This prevents unnecessary retries when Kelly is clearly active and reading messages.

### In Message Handlers

You could add auto-marking to your message processing:
```javascript
// When Kelly sends any message, auto-mark recent proactive as responded
if (message.from === 'kelly') {
    exec('node proactive-tracker.cjs auto-respond 30');
}
```

## Monitoring and Stats

Check system health with:
```bash
node proactive-tracker.cjs status
```

This shows:
- Recent message history
- Response rates
- Retry statistics
- Message aging

## Best Practices

1. **Use categories** to organize different types of check-ins
2. **Don't track casual messages** - only important proactive outreach
3. **Check status daily** to monitor system health
4. **Auto-mark when Kelly is active** to prevent unnecessary retries
5. **Review retry patterns** to improve message timing

## Troubleshooting

### Message Not Tracking
- Check if `proactive-messages.json` exists and is writable
- Verify tracking script path in commands
- Check for syntax errors in message content

### Retries Not Sending  
- Verify WhatsApp message tool is working
- Check retry checker is running in heartbeats/cron
- Look for error messages in retry output

### False Positives
- Use auto-mark when Kelly is active
- Manually mark responses with specific message IDs
- Adjust auto-mark time window as needed

## Example Usage Session

```bash
# Send important check-in
./send-proactive "How are you feeling about tonight's NWSL game? Excited/nervous?" nwsl

# 40 minutes later, in heartbeat...
node check-proactive-retries.js auto
# → Detects no response, sends retry with gentle note

# Kelly responds 
# → Either auto-detected or manually marked

# Check status
node proactive-tracker.cjs status
# → See response rates and recent activity
```

This system ensures your important check-ins reach Kelly while avoiding spam! 🎯
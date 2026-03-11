# HEARTBEAT.md Integration Example

Add this to your `HEARTBEAT.md` to automatically check for proactive message retries:

```markdown
## Proactive Message Retries

Check for messages needing retry every few heartbeats (not every time to avoid spam):

```javascript
// Only check every 3rd heartbeat or so
const shouldCheck = Math.random() < 0.3; // ~30% chance
if (shouldCheck) {
    const result = exec('node check-proactive-retries.cjs auto', {cwd: '/data/workspace'});
    if (result.stdout.includes('Retries sent:')) {
        // Log retry activity if any happened
        console.log('🔄 Proactive message retry check completed');
    }
}
```

Or for simpler integration:

```javascript
// Check for retries every heartbeat, but less verbose
exec('node check-proactive-retries.cjs auto', {cwd: '/data/workspace', stdio: 'pipe'});
```

## Alternative: Dedicated Cron Check

Instead of heartbeats, you could set up a dedicated cron job:

```bash
# Every 20 minutes, check for retries
*/20 * * * * cd /data/workspace && node check-proactive-retries.cjs auto >> /tmp/proactive-retries.log 2>&1
```

This keeps retry checking separate from your main heartbeat loop.

## Auto-Mark on Kelly Activity

When you detect Kelly is active (sending messages), auto-mark recent proactive messages:

```javascript
// When Kelly sends any message
if (incomingMessage.from === 'kelly') {
    exec('node proactive-tracker.cjs auto-respond 45', {cwd: '/data/workspace'});
}
```

This prevents retries when Kelly is clearly active and reading messages.
#!/usr/bin/env node
/**
 * Proactive Message Tracker for Telegram-first Shelly messaging
 * Usage: node proactive-tracker.cjs <action> [args]
 */

const fs = require('fs');

const TRACKING_FILE = '/data/workspace/proactive-messages.json';
const RETRY_WINDOW_MINUTES = 35; // Retry if no response within 35 minutes

function loadTracking() {
    try {
        const data = fs.readFileSync(TRACKING_FILE, 'utf8');
        return JSON.parse(data);
    } catch (e) {
        return [];
    }
}

function saveTracking(data) {
    fs.writeFileSync(TRACKING_FILE, JSON.stringify(data, null, 2));
}

function generateMessageId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function logMessage(content, category = 'check-in', channel = 'telegram') {
    const messages = loadTracking();
    const messageId = generateMessageId();

    const newMessage = {
        id: messageId,
        content,
        category,
        channel,
        timestamp: new Date().toISOString(),
        responded: false,
        retried: false,
        retry_sent_at: null
    };

    messages.push(newMessage);
    saveTracking(messages);

    console.log(`✅ Logged proactive message: ${messageId}`);
    console.log(`📝 Content: ${content.substring(0, 50)}${content.length > 50 ? '...' : ''}`);
    console.log(`🏷️  Category: ${category}`);
    console.log(`📡 Channel: ${channel}`);

    return messageId;
}

function markResponse(messageId) {
    const messages = loadTracking();
    const message = messages.find(m => m.id === messageId);

    if (!message) {
        console.log(`❌ Message ID ${messageId} not found`);
        return false;
    }

    message.responded = true;
    message.response_time = new Date().toISOString();
    saveTracking(messages);

    console.log(`✅ Marked message ${messageId} as responded`);
    return true;
}

function autoMarkRecent(timeWindow = 60) {
    const messages = loadTracking();
    const cutoff = new Date(Date.now() - (timeWindow * 60 * 1000));
    let marked = 0;

    messages.forEach(message => {
        if (!message.responded && new Date(message.timestamp) > cutoff) {
            message.responded = true;
            message.response_time = new Date().toISOString();
            message.auto_marked = true;
            marked++;
        }
    });

    if (marked > 0) {
        saveTracking(messages);
        console.log(`✅ Auto-marked ${marked} recent message(s) as responded`);
    }

    return marked;
}

function checkRetries() {
    const messages = loadTracking();
    const now = new Date();
    const needsRetry = [];

    messages.forEach(message => {
        if (!message.responded && !message.retried) {
            const messageTime = new Date(message.timestamp);
            const minutesElapsed = (now - messageTime) / (1000 * 60);

            if (minutesElapsed >= RETRY_WINDOW_MINUTES) {
                needsRetry.push(message);
            }
        }
    });

    return needsRetry;
}

function markRetried(messageId) {
    const messages = loadTracking();
    const message = messages.find(m => m.id === messageId);

    if (message) {
        message.retried = true;
        message.retry_sent_at = new Date().toISOString();
        saveTracking(messages);
        return true;
    }
    return false;
}

function showStatus() {
    const messages = loadTracking();

    if (messages.length === 0) {
        console.log('📭 No proactive messages tracked yet');
        return;
    }

    console.log(`📊 Proactive Message Status (${messages.length} total):\n`);

    const recent = messages.filter(m => {
        const age = (new Date() - new Date(m.timestamp)) / (1000 * 60 * 60);
        return age < 24;
    });

    recent.slice(-10).forEach(message => {
        const age = Math.round((new Date() - new Date(message.timestamp)) / (1000 * 60));
        const status = message.responded ? '✅' : (message.retried ? '🔄' : '⏳');

        console.log(`${status} [${message.category}] ${age}m ago`);
        console.log(`   "${message.content.substring(0, 60)}${message.content.length > 60 ? '...' : ''}"`);
        console.log(`   ID: ${message.id}`);
        console.log(`   Channel: ${message.channel || 'telegram'}`);

        if (message.responded && message.response_time) {
            const responseDelay = Math.round((new Date(message.response_time) - new Date(message.timestamp)) / (1000 * 60));
            console.log(`   📬 Responded after ${responseDelay} minutes`);
        }
        console.log('');
    });

    const responded = messages.filter(m => m.responded).length;
    const retried = messages.filter(m => m.retried).length;
    const responseRate = messages.length > 0 ? Math.round((responded / messages.length) * 100) : 0;

    console.log(`📈 Stats: ${responseRate}% response rate | ${retried} retries sent`);
}

function main() {
    const args = process.argv.slice(2);
    const action = args[0];

    switch (action) {
        case 'log':
            if (args.length < 2) {
                console.log('Usage: node proactive-tracker.cjs log "message content" [category] [channel]');
                process.exit(1);
            }
            logMessage(args[1], args[2] || 'check-in', args[3] || 'telegram');
            break;

        case 'respond':
            if (args.length < 2) {
                console.log('Usage: node proactive-tracker.cjs respond <message_id>');
                process.exit(1);
            }
            markResponse(args[1]);
            break;

        case 'auto-respond': {
            const window = args[1] ? parseInt(args[1], 10) : 60;
            autoMarkRecent(window);
            break;
        }

        case 'check-retries': {
            const needsRetry = checkRetries();
            if (needsRetry.length > 0) {
                console.log(`🔄 ${needsRetry.length} message(s) need retry:`);
                needsRetry.forEach(msg => {
                    console.log(`   ${msg.id}: "${msg.content.substring(0, 40)}..."`);
                });
                process.exit(2);
            } else {
                console.log('✅ No messages need retry');
                process.exit(0);
            }
            break;
        }

        case 'mark-retried':
            if (args.length < 2) {
                console.log('Usage: node proactive-tracker.cjs mark-retried <message_id>');
                process.exit(1);
            }
            markRetried(args[1]);
            break;

        case 'status':
            showStatus();
            break;

        default:
            console.log(`
📱 Telegram-First Proactive Message Tracker

Usage:
  node proactive-tracker.cjs log "message content" [category] [channel]
  node proactive-tracker.cjs respond <message_id>
  node proactive-tracker.cjs auto-respond [minutes_window]
  node proactive-tracker.cjs check-retries
  node proactive-tracker.cjs mark-retried <message_id>
  node proactive-tracker.cjs status

Examples:
  node proactive-tracker.cjs log "Quick body read: readiness looks decent, but don't force it if your energy feels flat." wellness
  node proactive-tracker.cjs auto-respond 45
  node proactive-tracker.cjs status
            `);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    logMessage,
    markResponse,
    autoMarkRecent,
    checkRetries,
    markRetried,
    showStatus
};

#!/usr/bin/env node
/**
 * Proactive Message Tracker for WhatsApp
 * Usage: node proactive-tracker.js <action> [args]
 */

const fs = require('fs');
const path = require('path');

const TRACKING_FILE = '/data/workspace/proactive-messages.json';
const RETRY_WINDOW_MINUTES = 35; // Retry if no response within 35 minutes

// Load existing tracking data
function loadTracking() {
    try {
        const data = fs.readFileSync(TRACKING_FILE, 'utf8');
        return JSON.parse(data);
    } catch (e) {
        return [];
    }
}

// Save tracking data
function saveTracking(data) {
    fs.writeFileSync(TRACKING_FILE, JSON.stringify(data, null, 2));
}

// Generate unique message ID
function generateMessageId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Log a new proactive message
function logMessage(content, category = 'check-in') {
    const messages = loadTracking();
    const messageId = generateMessageId();
    
    const newMessage = {
        id: messageId,
        content: content,
        category: category,
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
    
    return messageId;
}

// Mark a message as responded to
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

// Auto-mark recent messages as responded (when Kelly responds to anything)
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

// Check for messages needing retry
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

// Mark message as retried
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

// Show status of all messages
function showStatus() {
    const messages = loadTracking();
    
    if (messages.length === 0) {
        console.log("📭 No proactive messages tracked yet");
        return;
    }
    
    console.log(`📊 Proactive Message Status (${messages.length} total):\n`);
    
    const recent = messages.filter(m => {
        const age = (new Date() - new Date(m.timestamp)) / (1000 * 60 * 60);
        return age < 24; // Last 24 hours
    });
    
    recent.slice(-10).forEach(message => {
        const age = Math.round((new Date() - new Date(message.timestamp)) / (1000 * 60));
        const status = message.responded ? '✅' : (message.retried ? '🔄' : '⏳');
        
        console.log(`${status} [${message.category}] ${age}m ago`);
        console.log(`   "${message.content.substring(0, 60)}${message.content.length > 60 ? '...' : ''}"`);
        console.log(`   ID: ${message.id}`);
        
        if (message.responded && message.response_time) {
            const responseDelay = Math.round((new Date(message.response_time) - new Date(message.timestamp)) / (1000 * 60));
            console.log(`   📬 Responded after ${responseDelay} minutes`);
        }
        console.log('');
    });
    
    // Statistics
    const responded = messages.filter(m => m.responded).length;
    const retried = messages.filter(m => m.retried).length;
    const responseRate = messages.length > 0 ? Math.round((responded / messages.length) * 100) : 0;
    
    console.log(`📈 Stats: ${responseRate}% response rate | ${retried} retries sent`);
}

// Command line interface
function main() {
    const args = process.argv.slice(2);
    const action = args[0];
    
    switch (action) {
        case 'log':
            if (args.length < 2) {
                console.log("Usage: node proactive-tracker.js log \"message content\" [category]");
                process.exit(1);
            }
            logMessage(args[1], args[2] || 'check-in');
            break;
            
        case 'respond':
            if (args.length < 2) {
                console.log("Usage: node proactive-tracker.js respond <message_id>");
                process.exit(1);
            }
            markResponse(args[1]);
            break;
            
        case 'auto-respond':
            const window = args[1] ? parseInt(args[1]) : 60;
            autoMarkRecent(window);
            break;
            
        case 'check-retries':
            const needsRetry = checkRetries();
            if (needsRetry.length > 0) {
                console.log(`🔄 ${needsRetry.length} message(s) need retry:`);
                needsRetry.forEach(msg => {
                    console.log(`   ${msg.id}: "${msg.content.substring(0, 40)}..."`);
                });
                process.exit(2); // Exit code 2 indicates retries needed
            } else {
                console.log("✅ No messages need retry");
                process.exit(0);
            }
            break;
            
        case 'mark-retried':
            if (args.length < 2) {
                console.log("Usage: node proactive-tracker.js mark-retried <message_id>");
                process.exit(1);
            }
            markRetried(args[1]);
            break;
            
        case 'status':
            showStatus();
            break;
            
        default:
            console.log(`
📱 WhatsApp Proactive Message Tracker

Usage:
  node proactive-tracker.js log "message content" [category]
  node proactive-tracker.js respond <message_id>
  node proactive-tracker.js auto-respond [minutes_window]
  node proactive-tracker.js check-retries
  node proactive-tracker.js mark-retried <message_id>
  node proactive-tracker.js status

Examples:
  node proactive-tracker.js log "Hey! How are you feeling about the NWSL game tonight?" nwsl
  node proactive-tracker.js auto-respond 45
  node proactive-tracker.js status
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
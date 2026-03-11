#!/usr/bin/env node
/**
 * Proactive Message Retry Checker
 * Checks for messages that need retries and sends them automatically
 * Can be run in heartbeats or cron jobs
 */

const { spawn } = require('child_process');
const fs = require('fs');

// Import our tracking functions
const tracker = require('./proactive-tracker.cjs');

async function sendWhatsAppMessage(target, message) {
    return new Promise((resolve, reject) => {
        const messageScript = `
const { message } = require('./message.js');
message({ 
    action: 'send', 
    channel: 'whatsapp', 
    target: '${target}', 
    message: '${message.replace(/'/g, "\\'")}' 
});
        `;
        
        const node = spawn('node', ['-e', messageScript], { 
            cwd: '/data/workspace',
            stdio: ['pipe', 'pipe', 'pipe'] 
        });
        
        let output = '';
        let error = '';
        
        node.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        node.stderr.on('data', (data) => {
            error += data.toString();
        });
        
        node.on('close', (code) => {
            if (code === 0) {
                resolve(output);
            } else {
                reject(new Error(error || `Process exited with code ${code}`));
            }
        });
    });
}

async function checkAndSendRetries() {
    console.log('🔍 Checking for messages that need retries...');
    
    const needsRetry = tracker.checkRetries();
    
    if (needsRetry.length === 0) {
        console.log('✅ No messages need retry');
        return { retriesSent: 0, errors: [] };
    }
    
    console.log(`🔄 Found ${needsRetry.length} message(s) needing retry`);
    
    const results = {
        retriesSent: 0,
        errors: []
    };
    
    for (const message of needsRetry) {
        try {
            // Create retry message with gentle note
            const retryMessage = `${message.content}\n\n(Just making sure this got through! 📱)`;
            
            console.log(`📤 Retrying message ${message.id}...`);
            console.log(`   Original: "${message.content.substring(0, 40)}..."`);
            
            // Send the retry
            await sendWhatsAppMessage('kelly', retryMessage);
            
            // Mark as retried
            tracker.markRetried(message.id);
            
            console.log(`✅ Retry sent for message ${message.id}`);
            results.retriesSent++;
            
            // Space out retries to avoid spam
            if (needsRetry.length > 1) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
            
        } catch (error) {
            console.log(`❌ Failed to retry message ${message.id}:`, error.message);
            results.errors.push({
                messageId: message.id,
                error: error.message
            });
        }
    }
    
    return results;
}

// Auto-mark responses for recent messages when Kelly has been active
function autoMarkRecentResponses() {
    console.log('🔍 Auto-checking for recent responses...');
    const marked = tracker.autoMarkRecent(45); // 45 minute window
    if (marked > 0) {
        console.log(`✅ Auto-marked ${marked} message(s) as responded`);
    }
    return marked;
}

async function main() {
    const mode = process.argv[2] || 'check';
    
    try {
        switch (mode) {
            case 'check':
                // Just check, don't send
                const needsRetry = tracker.checkRetries();
                if (needsRetry.length > 0) {
                    console.log(`🔄 ${needsRetry.length} message(s) need retry`);
                    needsRetry.forEach(msg => {
                        const age = Math.round((new Date() - new Date(msg.timestamp)) / (1000 * 60));
                        console.log(`   ${msg.id} (${age}m old): "${msg.content.substring(0, 50)}..."`);
                    });
                    process.exit(1); // Signal that retries are needed
                } else {
                    console.log('✅ No retries needed');
                }
                break;
                
            case 'auto':
                // Auto-mark recent responses first
                autoMarkRecentResponses();
                
                // Then check and send retries
                const results = await checkAndSendRetries();
                
                console.log(`\n📊 Summary:`);
                console.log(`   Retries sent: ${results.retriesSent}`);
                console.log(`   Errors: ${results.errors.length}`);
                
                if (results.errors.length > 0) {
                    console.log(`\n❌ Errors:`);
                    results.errors.forEach(err => {
                        console.log(`   ${err.messageId}: ${err.error}`);
                    });
                }
                break;
                
            case 'auto-mark':
                autoMarkRecentResponses();
                break;
                
            default:
                console.log(`
🔄 Proactive Message Retry Checker

Usage:
  node check-proactive-retries.js [mode]

Modes:
  check     - Check for retries needed (default)
  auto      - Auto-mark responses and send retries  
  auto-mark - Only auto-mark recent responses

For heartbeats: Use 'check' mode
For cron: Use 'auto' mode
                `);
        }
        
    } catch (error) {
        console.error('❌ Error in retry checker:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = {
    checkAndSendRetries,
    autoMarkRecentResponses
};
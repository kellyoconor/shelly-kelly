#!/usr/bin/env node
/**
 * Test script for the proactive message system
 * Verifies all components work correctly
 */

const fs = require('fs');
const { execSync } = require('child_process');

console.log('🧪 Testing WhatsApp Proactive Message System...\n');

// Test 1: Basic tracking
console.log('1. Testing message logging...');
try {
    const output = execSync('node proactive-tracker.cjs log "Test message for system check" test', {cwd: '/data/workspace'}).toString();
    const messageId = output.match(/Logged proactive message: (\w+)/)?.[1];
    
    if (messageId) {
        console.log(`✅ Message logged successfully: ${messageId}`);
        
        // Test 2: Status check
        console.log('\n2. Testing status display...');
        execSync('node proactive-tracker.cjs status', {cwd: '/data/workspace', stdio: 'inherit'});
        
        // Test 3: Response marking
        console.log('\n3. Testing response marking...');
        execSync(`node proactive-tracker.cjs respond ${messageId}`, {cwd: '/data/workspace', stdio: 'inherit'});
        
        // Test 4: Retry check (should find nothing since we marked as responded)
        console.log('\n4. Testing retry check...');
        execSync('node check-proactive-retries.cjs check', {cwd: '/data/workspace', stdio: 'inherit'});
        
        console.log('\n✅ All basic tests passed!');
        
    } else {
        console.log('❌ Failed to extract message ID from logging output');
    }
} catch (error) {
    console.log('❌ Test failed:', error.message);
}

// Test 5: File permissions
console.log('\n5. Testing file permissions...');
try {
    fs.accessSync('/data/workspace/send-proactive', fs.constants.X_OK);
    console.log('✅ send-proactive script is executable');
} catch (error) {
    console.log('❌ send-proactive script not executable');
}

// Test 6: JSON file integrity
console.log('\n6. Testing JSON file integrity...');
try {
    const data = JSON.parse(fs.readFileSync('/data/workspace/proactive-messages.json', 'utf8'));
    console.log(`✅ JSON file valid with ${data.length} messages`);
} catch (error) {
    console.log('❌ JSON file corrupted or missing');
}

console.log('\n🎉 System test complete!');
console.log('\n📚 Next steps:');
console.log('1. Add retry checker to HEARTBEAT.md (see HEARTBEAT-PROACTIVE-EXAMPLE.md)');
console.log('2. Start using ./send-proactive for important messages');
console.log('3. Monitor with: node proactive-tracker.cjs status');
console.log('4. Read PROACTIVE-MESSAGE-SYSTEM.md for full documentation');
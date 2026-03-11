#!/usr/bin/env node
/**
 * Alert Retry Processor
 * 
 * Handles retry logic and escalations for critical alerts.
 * Integrates with heartbeat system for automated processing.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class AlertRetryProcessor {
    constructor() {
        this.workspace = '/data/workspace';
        this.alertsFile = path.join(this.workspace, 'critical-alerts.json');
        this.logFile = path.join(this.workspace, 'alert-delivery-log.md');
        this.criticalEngine = path.join(this.workspace, 'critical-alert-engine.py');
        
        // Email configuration (placeholder)
        this.emailConfig = {
            enabled: false,  // Set to true when email service is configured
            service: 'gmail', // or other email service
            user: 'kelly@example.com',
            apiKey: process.env.EMAIL_API_KEY
        };
    }
    
    /**
     * Process all pending retries and escalations
     */
    async processRetries() {
        try {
            console.log('Processing critical alert retries...');
            
            // Use the Python engine to handle retry logic
            const result = await this.runCommand('python3', [this.criticalEngine, 'retry-check']);
            
            if (result.success) {
                console.log('Retry processing completed successfully');
                return { success: true, message: 'Retries processed' };
            } else {
                console.error('Retry processing failed:', result.error);
                return { success: false, error: result.error };
            }
        } catch (error) {
            console.error('Error processing retries:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Check for Kelly's recent activity and auto-mark alerts as seen
     */
    async autoMarkRecentAlerts(minutesBack = 60) {
        try {
            console.log(`Auto-marking alerts from last ${minutesBack} minutes...`);
            
            const result = await this.runCommand('python3', [
                this.criticalEngine, 'respond', minutesBack.toString()
            ]);
            
            if (result.success) {
                const marked = this.extractMarkedCount(result.output);
                if (marked > 0) {
                    console.log(`Auto-marked ${marked} alerts as seen`);
                    return { success: true, marked };
                }
                return { success: true, marked: 0 };
            } else {
                console.error('Auto-mark failed:', result.error);
                return { success: false, error: result.error };
            }
        } catch (error) {
            console.error('Error auto-marking alerts:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Get current alert system status
     */
    async getAlertStatus() {
        try {
            const result = await this.runCommand('python3', [this.criticalEngine, 'status']);
            
            if (result.success) {
                return {
                    success: true,
                    status: JSON.parse(result.output)
                };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Generate alert system report
     */
    async generateReport() {
        try {
            const result = await this.runCommand('python3', [this.criticalEngine, 'report']);
            
            if (result.success) {
                return {
                    success: true,
                    report: result.output
                };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Send email backup for failed WhatsApp alerts
     */
    async sendEmailBackup(alertContent, urgency, alertId) {
        if (!this.emailConfig.enabled) {
            console.log(`Email backup not configured for alert ${alertId}`);
            return { success: false, reason: 'Email not configured' };
        }
        
        try {
            // Placeholder for email implementation
            // This would integrate with actual email service like SendGrid, Gmail API, etc.
            
            const subject = `🚨 ${urgency} Alert - Response Needed`;
            const body = `
Alert ID: ${alertId}
Urgency Level: ${urgency}
Timestamp: ${new Date().toISOString()}

Message:
${alertContent}

This alert was sent via WhatsApp but no response was received.
Please respond to confirm you received this message.

--
Kelly's Critical Alert Safeguard System
            `;
            
            // TODO: Implement actual email sending
            console.log(`EMAIL BACKUP TRIGGERED for ${alertId}:`);
            console.log(`Subject: ${subject}`);
            console.log(`Body: ${body}`);
            
            // Log the email attempt
            this.logEmailAttempt(alertId, urgency, 'SIMULATED');
            
            return {
                success: true,
                method: 'simulated',
                message: 'Email backup logged (implementation pending)'
            };
        } catch (error) {
            console.error(`Email backup failed for ${alertId}:`, error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Check for escalated alerts requiring manual review
     */
    async checkEscalatedAlerts() {
        try {
            const escalatedFile = path.join(this.workspace, 'escalated-alerts.md');
            
            if (!fs.existsSync(escalatedFile)) {
                return { success: true, escalated: [] };
            }
            
            const content = fs.readFileSync(escalatedFile, 'utf8');
            const alertCount = (content.match(/## Alert/g) || []).length;
            
            if (alertCount > 0) {
                console.log(`Found ${alertCount} escalated alerts requiring manual review`);
                
                // Parse escalated alerts
                const escalatedAlerts = this.parseEscalatedAlerts(content);
                
                return {
                    success: true,
                    escalated: escalatedAlerts,
                    count: alertCount
                };
            }
            
            return { success: true, escalated: [], count: 0 };
        } catch (error) {
            console.error('Error checking escalated alerts:', error);
            return { success: false, error: error.message };
        }
    }
    
    /**
     * Parse escalated alerts from markdown file
     */
    parseEscalatedAlerts(content) {
        const alerts = [];
        const sections = content.split('## Alert ').slice(1);
        
        for (const section of sections) {
            const lines = section.split('\n');
            const header = lines[0];
            
            const match = header.match(/(\w+)\s*-\s*(\w+)/);
            if (match) {
                const alertId = match[1];
                const urgency = match[2];
                
                const alert = {
                    id: alertId,
                    urgency: urgency,
                    content: ''
                };
                
                // Extract content
                for (const line of lines) {
                    if (line.startsWith('**Content:**')) {
                        alert.content = line.replace('**Content:**', '').trim();
                        break;
                    }
                }
                
                alerts.push(alert);
            }
        }
        
        return alerts;
    }
    
    /**
     * Run heartbeat integration - called from HEARTBEAT.md
     */
    async runHeartbeatCheck() {
        console.log('Running critical alert heartbeat check...');
        
        const results = {
            retries: await this.processRetries(),
            autoMark: await this.autoMarkRecentAlerts(45), // Auto-mark last 45 min
            status: await this.getAlertStatus(),
            escalated: await this.checkEscalatedAlerts()
        };
        
        // Generate summary for heartbeat response
        let summary = [];
        
        if (results.status.success) {
            const status = results.status.status;
            
            if (status.active_alerts > 0) {
                summary.push(`${status.active_alerts} active critical alerts`);
            }
            
            if (status.pending_retries > 0) {
                summary.push(`${status.pending_retries} pending retries`);
            }
        }
        
        if (results.escalated.success && results.escalated.count > 0) {
            summary.push(`${results.escalated.count} alerts need manual review`);
        }
        
        if (results.autoMark.success && results.autoMark.marked > 0) {
            summary.push(`Auto-marked ${results.autoMark.marked} as seen`);
        }
        
        // Return summary for heartbeat
        if (summary.length > 0) {
            return `Critical Alert Status: ${summary.join(', ')}`;
        } else {
            return 'HEARTBEAT_OK';  // No critical alerts need attention
        }
    }
    
    /**
     * Integration with proactive message system for Kelly's activity detection
     */
    async detectKellyActivity() {
        try {
            // Check if Kelly has sent any recent messages (indicating she's active)
            const proactiveFile = path.join(this.workspace, 'proactive-messages.json');
            
            if (!fs.existsSync(proactiveFile)) {
                return false;
            }
            
            const proactiveData = JSON.parse(fs.readFileSync(proactiveFile, 'utf8'));
            
            // Look for recent responses in proactive system
            const now = new Date();
            const recentThreshold = new Date(now.getTime() - 30 * 60 * 1000); // 30 minutes
            
            for (const message of proactiveData) {
                if (message.response_time) {
                    const responseTime = new Date(message.response_time);
                    if (responseTime >= recentThreshold) {
                        return true;  // Kelly is recently active
                    }
                }
            }
            
            return false;
        } catch (error) {
            console.error('Error detecting Kelly activity:', error);
            return false;
        }
    }
    
    /**
     * Log email attempt
     */
    logEmailAttempt(alertId, urgency, status) {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] EMAIL BACKUP: Alert ${alertId} (${urgency}) - ${status}\\n`;
        
        fs.appendFileSync(this.logFile, logEntry);
    }
    
    /**
     * Extract marked count from Python output
     */
    extractMarkedCount(output) {
        const match = output.match(/marked (\\d+)/i);
        return match ? parseInt(match[1]) : 0;
    }
    
    /**
     * Run command and return result
     */
    runCommand(command, args = []) {
        return new Promise((resolve) => {
            const process = spawn(command, args, {
                cwd: this.workspace,
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            let stdout = '';
            let stderr = '';
            
            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            process.on('close', (code) => {
                resolve({
                    success: code === 0,
                    output: stdout.trim(),
                    error: stderr.trim()
                });
            });
            
            process.on('error', (error) => {
                resolve({
                    success: false,
                    error: error.message
                });
            });
        });
    }
}

// Command-line interface
async function main() {
    const processor = new AlertRetryProcessor();
    const command = process.argv[2];
    
    if (!command) {
        console.log('Usage:');
        console.log('  node alert-retry-processor.js heartbeat      # Run heartbeat check');
        console.log('  node alert-retry-processor.js retries       # Process retries only');
        console.log('  node alert-retry-processor.js auto-mark     # Auto-mark recent alerts');
        console.log('  node alert-retry-processor.js status        # Get system status');
        console.log('  node alert-retry-processor.js report        # Generate report');
        console.log('  node alert-retry-processor.js escalated     # Check escalated alerts');
        return;
    }
    
    let result;
    
    switch (command) {
        case 'heartbeat':
            result = await processor.runHeartbeatCheck();
            console.log(result);
            break;
            
        case 'retries':
            result = await processor.processRetries();
            console.log(JSON.stringify(result, null, 2));
            break;
            
        case 'auto-mark':
            const minutes = parseInt(process.argv[3]) || 60;
            result = await processor.autoMarkRecentAlerts(minutes);
            console.log(JSON.stringify(result, null, 2));
            break;
            
        case 'status':
            result = await processor.getAlertStatus();
            if (result.success) {
                console.log(JSON.stringify(result.status, null, 2));
            } else {
                console.error('Status check failed:', result.error);
            }
            break;
            
        case 'report':
            result = await processor.generateReport();
            if (result.success) {
                console.log(result.report);
            } else {
                console.error('Report generation failed:', result.error);
            }
            break;
            
        case 'escalated':
            result = await processor.checkEscalatedAlerts();
            if (result.success) {
                console.log(`Found ${result.count} escalated alerts`);
                if (result.escalated.length > 0) {
                    console.log(JSON.stringify(result.escalated, null, 2));
                }
            } else {
                console.error('Escalated check failed:', result.error);
            }
            break;
            
        default:
            console.log(`Unknown command: ${command}`);
            break;
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = AlertRetryProcessor;
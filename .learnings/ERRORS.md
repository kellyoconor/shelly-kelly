## [ERR-20260310-001] mini_monty_token_alerts

**Logged**: 2026-03-10T16:36:00-05:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Mini Monty sending repeated "200k/200k tokens" alerts inappropriately

### Error
```
🚨 **Mini Monty Alert**

Main session tokens: **200k/200k (100%)**
Threshold: 150k

Your chat session is at maximum context. You'll need to `/restart` to continue normal operation.

Current time: 4:27 PM ET
```

### Context
- Kelly getting this alert message repeatedly 
- Seems to be stuck on repeat or cached weirdly
- Previously had an issue where new sessions were starting with 200k tokens immediately (that was fixed)
- This appears to be alert system malfunction, not actual token counting issue

### Root Cause Found
**MASSIVE skills directory bloat:**
- `/data/workspace/skills/flightclaw/.venv` = **189MB** (Python virtual environment)
- 26 total skills = ~200k characters just in SKILL.md files  
- Total skills directory = 190MB

**Theory:** OpenClaw may be trying to index/load content from entire skills directory, causing massive context bloat

### Immediate Fixes Needed
1. **Remove .venv from flightclaw skill** - shouldn't be there
2. **Add .venv to .gitignore** in flightclaw skill
3. **Investigate if OpenClaw is indexing non-SKILL.md files** in skills directory
4. **Consider skill loading optimization** - 26 skills is a lot of context injection

### Metadata
- Reproducible: yes (happening repeatedly for user)
- Related Files: cron job configs, monty alert system
- Session Context: Fresh session after recent token fixes

## [ERR-20260312-001] agentmail_module_missing

**Logged**: 2026-03-12T16:00:00-05:00
**Priority**: medium
**Status**: pending
**Area**: email

### Summary
AgentMail skill is documented but agentmail Python module is not installed, preventing email access

### Error
```
ModuleNotFoundError: No module named 'agentmail'
```

### Context
- Kelly sent flight delay info to shelly@agentmail.to  
- Tried to check inbox using /data/workspace/skills/agentmail/scripts/client.py
- Skill documentation indicates email should be accessible
- Missing Python package prevents any email operations

### Suggested Fix
Install agentmail package or update skill to use different email access method

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/skills/agentmail/scripts/client.py
- Impact: Can't read emails sent to agent inbox

---
# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### Weekly OS Report Verification (Added Mar 29, 2026)
**MANDATORY DATA CHECK before writing any weekly summary:**
1. **Always run Strava weekly command first:** `python3 /data/workspace/skills/strava/scripts/strava.py weekly`
2. **Always run recent Strava runs:** `python3 /data/workspace/skills/strava/scripts/strava.py runs 10`
3. **Check Oura data trends:** Review HRV, sleep, readiness patterns
4. **Verify each pillar has actual data** before making claims
5. **Never write "no activity" without double-checking the source**

**Rule: If writing a Body section about running, MUST have concrete Strava data in front of me**

### Browser Automation Logging (Added Mar 29, 2026)
- **Always narrate browser steps out loud** as they happen
- Log: "🌐 Connecting to browser...", "✅ Connected to [URL]", "🔍 Looking for [element]"
- Report what you actually see on each page: "Page shows Google search box and logo" 
- Call out any errors immediately: "❌ Element not found, trying different approach"
- **Goal**: Kelly always knows what's happening, even if snapshots fail

### Git Push Strategy (Updated Mar 12, 2026)
- **Commit and push immediately** after each logical unit of work (feature, fix, config change)
- Railway auto-deploys on push to main — brief downtime is fine for immediate iteration
- **Commit message format**: One line, short and descriptive of what changed
- **Prompt Kelly to commit** whenever we finish meaningful work
- **Always ask before committing** — let Kelly approve the commit message and confirm she's happy with changes
- Use OpenClaw's git workflow commands

### Definition of Done (Updated Mar 12, 2026)
Before any task can be marked complete, it must include:
- **Repo and branch** (e.g., `kellyoconor/shelly-kelly:main`)
- **Commit hash** (full SHA or short hash)
- **What files changed** (list of modified/added/deleted files)
- **Verification that the changes actually work** (test output, functionality check)
- **Screenshot or artifact** if it's a UI change
- **No exceptions** — this is required for every development task

### File Creation Defaults (Updated Mar 18, 2026)

⚠️ **CRITICAL RULE: WORKSPACE IS THE EXCEPTION** ⚠️
- Default to VAULT for almost everything
- Only use workspace for: system logs, technical infrastructure, temporary files
- When in doubt → vault daily note

## **VAULT ORGANIZATION RULES**

### **📅 01-Daily/** - **DEFAULT FOR MOST CONTENT**
**Path:** `/data/kelly-vault/01-Daily/2026/YYYY-MM-DD.md`
**Use for:** 
- Personal reflections, conversations, decisions, emotional processing
- One-off insights, quick training thoughts, random ideas  
- Daily events, health data, meeting notes
- Anything that's timestamped and part of your day

**When to use daily notes vs standalone:**
- **Daily note:** "Had insight about running form during today's 5K"
- **Standalone:** Full training plan, detailed research, fleshed-out concepts

### **📋 02-Projects/** - **ACTIVE BUILDING WORK**
**Create standalone note when:**
- Building something specific (app, system, analysis)
- Multi-session work that needs its own space  
- Project planning, architecture docs, progress tracking
- **Examples:** `BelowTheFloorBot Project`, `Shelly Architecture Redesign`

**Daily note instead:** Quick project updates, today's coding progress, bugs fixed

### **🧠 03-Knowledge/** - **REFERENCE & LEARNING**  
**Create standalone note when:**
- Research worth referencing again (market analysis, technical deep-dive)
- Mental models, frameworks, methodologies you'll reuse
- Article summaries with actionable insights
- **Examples:** `AI Agent Architecture Patterns`, `Running Periodization Guide`

**Daily note instead:** "Read interesting article about X", quick learning moments

### **🏃‍♀️ 04-Life/** - **MAJOR LIFE AREAS**
**Health & Training/ - Create standalone when:**
- Training plans, race preparation strategies
- Major health insights from Welly/doctor visits  
- Injury prevention protocols, technique guides
- **Examples:** `Marathon Training Block 2026`, `ACL Recovery Protocol`

**Career/ - Create standalone when:**
- Job transition planning, salary negotiation prep
- Major career decisions, promotion strategies
- **Examples:** `Director Role Transition Plan`, `2026 Career Goals`

**Daily note instead:** Training insights, health data, work frustrations, career thoughts

### **🔍 05-Reflections/** - **PERIODIC REVIEWS**
**Create standalone note when:**
- Weekly/monthly/annual reviews worth keeping
- Major Choose Brave decisions that need documentation
- Goal-setting sessions, life planning
- **Examples:** `March 2026 Monthly Review`, `Choose Brave: Solo Scotland Trip`

**Daily note instead:** Daily reflection prompts, quick self-awareness moments

### **✈️ 06-Travel/** - **TRIP DOCUMENTATION**  
**Create standalone note when:**
- Trip planning (itineraries, research, packing lists)
- Major travel experiences worth detailed documentation  
- **Examples:** `Nantucket June 2026 Plan`, `Scotland Solo Adventure Memories`

**Daily note instead:** Travel thoughts, quick trip ideas, daily travel updates

### **💡 07-Ideas/** - **CREATIVE CONCEPTS**
**Create standalone note when:**
- Fleshed-out product concepts, startup ideas with detail
- App mockups, business model thoughts
- Writing projects, creative works in progress
- **Examples:** `Dating App for Marathon Runners`, `Personal AI Assistant Concept`

**Daily note instead:** Random shower thoughts, quick brainstorms, fleeting ideas

## **WORKSPACE MEMORY RULES**

**Workspace Memory:** `/data/workspace/memory/YYYY-MM-DD.md`  
- System logs, bug tracking, agent state, operational notes
- Technical debugging, automation logs, anything purely infrastructure
- Never include personal content here

**Mixed Content Days:** Create both files
- Vault daily note with personal stuff
- Workspace log with technical stuff
- Clean separation maintained

## **DECISION FRAMEWORK**

**Ask yourself:**
1. **Will I reference this again?** → Standalone note
2. **Is this >500 words of useful content?** → Standalone note  
3. **Does this need its own links/structure?** → Standalone note
4. **Is this just today's thought/event?** → Daily note

**Default to daily notes.** Only create standalone notes for substantial, referenceable content.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

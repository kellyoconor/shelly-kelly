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

**Vault:** `/data/kelly-vault/01-Daily/2026/YYYY-MM-DD.md`
- Personal reflections, life events, training logs, emotional processing
- Decisions, conversations, thoughts, anything Kelly would want in Obsidian
- Auto-syncs to Obsidian via git

**Workspace Memory:** `/data/workspace/memory/YYYY-MM-DD.md`  
- System logs, bug tracking, agent state, operational notes
- Technical debugging, automation logs, anything purely infrastructure
- Never include personal content here

**Mixed Content Days:** Create both files
- Vault daily note with personal stuff
- Workspace log with technical stuff
- Clean separation maintained

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

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

### File Creation Defaults (Updated Mar 12, 2026)
- **Operational logs, updates, agent state**: `/data/workspace/memory/` (workspace memory)
- **Personal documents when explicitly requested**: `/data/kelly-vault/` (Obsidian vault)
- **Don't offer both options** — make the call based on content type
- Auto-sync to git so Obsidian files appear in her vault immediately

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

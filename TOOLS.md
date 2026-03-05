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

### Git Push Strategy
- **Commit locally** throughout the day as normal
- **Push to GitHub once** during late-night heartbeat (~2-4 AM ET) when Kelly is sleeping
- Railway auto-deploys on push to main — so pushing = redeploy = brief downtime
- Exception: push immediately if Kelly asks or if there's a critical fix
- NEVER push multiple times in a short window
- **If 5+ commits stack up unpushed, nudge Kelly** to confirm a push (remind her it triggers a redeploy)

### File Creation Defaults
- **When Kelly asks for files**: Create in `/data/kelly-vault/` (Obsidian vault) by default
- She accesses documents through Obsidian, not as code files
- Auto-sync to git so they appear in her vault immediately

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

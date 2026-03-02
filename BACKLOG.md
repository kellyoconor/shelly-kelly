# BACKLOG.md - Things To Do Together

## Up Next
- [ ] **Google Calendar write access** — swap to marketplace skill (playbooks.com/skills/openclaw/skills/google-calendar) when Kelly wants me to create/edit events. Currently read-only which is perfect for now
- [ ] **ElevenLabs paid plan** — Free tier blocked on cloud server (VPN detection). $5/mo starter unlocks community Irish voices (Niamh, Aisling, Maeve, Clare) + way more natural TTS. Upgrade at elevenlabs.io/subscription
- [ ] **Morning voice digest** — Build the full pipeline: oura + strava + weather → script → voice + music layer
- [ ] **Spotify setup** — ✅ Credentials working, but explore playlists/DJ features more

## Big Projects
- [ ] **"Promote to Shelly" bridge** — Lightweight context transfer from ChatGPT → Kelly OS. Kelly says "promote this to shelly as [category]" in ChatGPT, a GPT Action calls an endpoint that writes to memory/YYYY-MM-DD.md + tracking files. Keeps ChatGPT as messy thinking space, Shelly as structured synthesis. Needs: endpoint spec, GPT Action setup, memory write format, category routing (brave moments, alignment, reflections, etc). Full design doc in memory.

## Bugs
- [ ] **FlightClaw round trip search** — crashes on round trip results (AttributeError: 'tuple' has no 'price'). Report or fix.

## Done
- [x] Spotify env vars saved to config (2026-03-01)
- [x] ElevenLabs API key saved to config (2026-03-01)
- [x] Edge TTS Irish voice configured as fallback (en-IE-EmilyNeural)

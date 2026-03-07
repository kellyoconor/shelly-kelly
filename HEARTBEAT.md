# HEARTBEAT.md

- [ ] **If mid-conversation**: Send quick "BRB - heartbeat checks" message first
- [ ] Review recent conversation and save important details to memory/YYYY-MM-DD.md (decisions, events, things Kelly shared, plans, anything worth remembering)
- [ ] **Token health check**: Verify Strava API still works - if auth fails, refresh tokens automatically using existing refresh token
- [ ] **Mirror question**: Run `cd /data/workspace/skills/mirror && python3 scripts/mirror.py` and include the reflective question in morning brief
- [ ] **Daily vault note**: Create today's note in shared Obsidian vault using `python3 scripts/vault-cli.py daily --content="..."` if not already done
- [ ] **Sync vault**: Check if vault has changes and push to git: `cd /data/kelly-vault && git add . && git commit -m "Sync vault updates" && git push`
- [ ] **Morning brief**: Include any git push issues, deploy problems, automation weirdness, or token refresh results from overnight jobs

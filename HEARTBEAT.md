# HEARTBEAT.md

- [ ] Review recent conversation and save important details to memory/YYYY-MM-DD.md (decisions, events, things Kelly shared, plans, anything worth remembering)
- [ ] **Daily vault note**: Create today's note in shared Obsidian vault using `python3 scripts/vault-cli.py daily --content="..."` if not already done
- [ ] **Sync vault**: Check if vault has changes and push to git: `cd /data/kelly-vault && git add . && git commit -m "Sync vault updates" && git push`
- [ ] Check if there are uncommitted changes in /data/workspace — if so, commit and push
- [ ] **Inbox scan**: Check shelly@agentmail.to for new unread emails. If any are shipping/order/delivery related, extract tracking info and update `/data/workspace/skills/package-tracker/data/packages.json`. Alert Kelly on WhatsApp if something new is found (accountId: custom-1, target: +13018302401).

# BACKLOG.md — Rainy Day Projects

## 1. Token Optimization — Stop Burning Money
**Priority:** High (saves real $$$)
**Effort:** ~1-2 hours

**Problem:** We're running Opus ($15/M input, $75/M output) for EVERYTHING — including heartbeats, cron jobs, and simple tasks that don't need a big brain. That's like taking a Ferrari to the grocery store.

**What to do:**
- Switch heartbeats to Sonnet (way cheaper, plenty smart for "check inbox, anything new?")
- Set cron jobs to use Sonnet by default (morning briefing, package tracker, etc.)
- Keep Opus for main session conversations where you need depth
- Audit MEMORY.md size — it loads every turn and it's growing. Trim outdated stuff, move historical details to daily logs
- Review bootstrap file sizes (AGENTS.md, SOUL.md, USER.md, TOOLS.md) — every character costs tokens every single message
- Consider context pruning settings (cache-ttl mode) to auto-trim old tool results from conversation history

**How to measure:** Check session_status before and after — compare token counts per message.

---

## 2. Lean Bootstrap Files
**Priority:** Medium (compounds over time)
**Effort:** ~1 hour

**Problem:** MEMORY.md is loaded into context every turn. It's getting long — marathon history, Scotland trip details, dating notes, NWSL interview details. All of that eats tokens even when it's not relevant to the current conversation.

**What to do:**
- Audit MEMORY.md — what MUST be in every conversation vs what can live in memory search only?
- Core identity stuff stays (mantras, preferences, Starbucks order, key rules)
- Historical events move to daily logs or a separate `memory/archive.md` that only gets pulled via semantic search
- Same audit for AGENTS.md — is every instruction still relevant?
- Measure before/after: count characters in all bootstrap files combined
- Goal: cut bootstrap size by 30-50% without losing anything important

---

## 3. Multi-Agent Setup
**Priority:** Low (cool but not urgent)
**Effort:** ~2-3 hours

**Problem:** Everything runs through one agent — morning briefings, casual chat, system maintenance, data analysis. The article suggests separate agents for different purposes, each with their own workspace and memory.

**What to do:**
- Consider splitting into 2 agents:
  - **Shelly** (personal) — daily chat, vibes, reflective questions, life stuff
  - **Ops** (system) — heartbeats, cron jobs, monitoring, maintenance tasks
- Each gets its own workspace, memory, and tool permissions
- Ops agent could run on Sonnet permanently (cheaper, faster for system tasks)
- Shelly stays on Opus for the real conversations
- Set up bindings so WhatsApp → Shelly, system tasks → Ops
- Could also add a dedicated research agent with browser access

**Tradeoffs:** More complex setup, agents can't easily share context. Start simple with 2, expand later.

---

## 4. Fix Browser Tool
**Priority:** Medium (unlocks X/Twitter, web research, Gmail checking)
**Effort:** ~30 min

**Problem:** Browser tool isn't starting after the v2026.3.2 update. Chromium is installed but CDP (Chrome DevTools Protocol) isn't connecting.

**What to do:**
- Debug why `browser start` fails — check if Chromium path is still correct after update
- Test with `openclaw browser status`
- May need to update browser config for new version
- Once working: can read tweets, browse web pages, interact with sites that block simple fetches
- Opens up possibilities like Gmail inbox checking via browser instead of API

---

## 5. Fix Image Tool (sharp package)
**Priority:** Medium (you send me photos and I can't see them)
**Effort:** ~15 min

**Problem:** `sharp` package missing after update. Needed to resize images before AI analysis. Install failed due to Railway memory limits during compilation.

**What to do:**
- Try `pnpm add sharp --config.platform=linuxmusl` (prebuilt binary, skips compilation)
- Or `npm install --os=linux --cpu=x64 sharp` 
- Or add sharp to the OpenClaw package.json so it survives future updates
- Test by sending a photo after install
- Add to bootstrap.sh so it reinstalls on redeploy

---

## 6. Set Up Brave Search API
**Priority:** Low (nice to have)
**Effort:** ~15 min

**Problem:** `web_search` tool doesn't work — needs a Brave Search API key. Currently I can only use `web_fetch` which doesn't work on sites that block scrapers (like X).

**What to do:**
- Sign up at https://brave.com/search/api/ (free tier: 2,000 queries/month)
- Add API key to OpenClaw config: `openclaw configure --section web`
- Or add to config: `tools.web.search.apiKey`
- Once set up: proper web search results, better research capability
- Pairs well with browser tool for full web access

---

## 7. Config Tuning for Cost
**Priority:** Medium (money savings)
**Effort:** ~1 hour

**Problem:** We haven't tuned any of the cost-related config settings. Running defaults everywhere.

**What to do:**
- **Context pruning:** Enable `cache-ttl` mode to auto-trim old tool results (they're huge and stick around forever)
- **Compaction settings:** Review `memoryFlush` — make sure important stuff gets saved to MEMORY.md before old messages get compressed
- **Heartbeat model:** Set `heartbeat.model` to Sonnet explicitly
- **Subagent model:** Set `subagents.model` to Sonnet (most sub-tasks don't need Opus)
- **Block streaming:** Consider enabling for WhatsApp to reduce back-and-forth API calls
- **Bootstrap max chars:** Review `bootstrapMaxChars` setting — cap how much of each file gets injected
- Run `session_status` to see current token usage as baseline, then compare after changes

---

*Last updated: 2026-03-03*
*Add new items as they come up. Tackle these when you've got time and energy — none are urgent.*

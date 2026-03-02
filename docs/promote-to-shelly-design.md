# Bridge Design: "Promote to Shelly"
### Lightweight Context Transfer from ChatGPT → Kelly OS

## Overview

This document defines a minimal-friction bridge between ChatGPT (raw processing layer) and Shelly (pattern + synthesis layer).

The goal is **not** to export full transcripts.

The goal is to selectively promote meaningful moments into Kelly OS memory so that weekly reports reflect real emotional signal — not just tracked metrics.

This preserves:
- ChatGPT = messy thinking space
- Shelly = structured synthesis + longitudinal pattern detection

---

# System Philosophy

Kelly processes in ChatGPT.
Shelly synthesizes what matters.

We do not aim for surveillance.
We aim for signal.

Only promoted moments enter the Kelly OS memory system.

---

# Architecture Overview

## Flow

1. Kelly has a meaningful moment inside ChatGPT.
2. She says:  
   **"Promote this to Shelly as [category]."**
3. A GPT Action calls an external endpoint.
4. The endpoint writes the entry to:
   - `memory/YYYY-MM-DD.md`
   - and optionally a category-specific tracking file.
5. Weekly report reads memory files + tracking files.
6. Weekly Kelly OS report includes real emotional context.

---

# Categories

- **brave** → tracking/brave-moments.md
- **alignment** → tracking/alignment.md
- **reflection** → memory/YYYY-MM-DD.md only
- **standard** → tracking/standards.md
- **insight** → memory/YYYY-MM-DD.md only

---

# Status: BACKLOGGED
Needs: endpoint build, GPT Action setup, auth, category routing

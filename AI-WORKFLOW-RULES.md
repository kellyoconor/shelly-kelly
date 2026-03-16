# AI Workflow Rules - Mandatory Processes

## 🚨 PROACTIVE MESSAGING TO KELLY - MANDATORY PIPELINE

**BEFORE any proactive message to Kelly (+13018302401), I MUST:**

### 1. UPDATE KELLY STATE (NO EXCEPTIONS)
```python
exec: python3 /data/workspace/scripts/update-kelly-state.py
```

### 2. READ UPDATED CONTEXT
The updated `/data/workspace/kelly-state.md` now contains current context that should inform my message.

### 3. COMPOSE CONTEXT-AWARE MESSAGE  
Base message on actual current state, not assumptions or generic questions.

---

## ENFORCEMENT MECHANISM

**OLD (BROKEN) WORKFLOW:**
1. AI decides to message Kelly
2. AI asks generic question: "How was your run this morning?"
3. Kelly frustrated: "You just fixed memory search and asked me that?"

**NEW (REQUIRED) WORKFLOW:**  
1. AI decides to message Kelly
2. AI runs: `exec: python3 /data/workspace/scripts/update-kelly-state.py`
3. AI reads updated kelly-state.md for current context
4. AI composes message based on actual current state
5. AI sends context-aware message

---

## SPECIFIC EXAMPLES

**❌ WRONG:** "How was your run this morning?" (generic assumption)

**✅ RIGHT:** "How are you feeling today after your rest day yesterday?" (based on actual context)

**❌ WRONG:** "What's your plan for today?" (no awareness)

**✅ RIGHT:** "Feeling ready to get back to moving after taking yesterday to rest?" (aware of recent context)

---

## NON-NEGOTIABLE RULE

I will **NEVER** send a proactive message to Kelly without first updating and reading Kelly State. This pipeline is **MANDATORY** and **AUTOMATIC** - not optional or dependent on memory.
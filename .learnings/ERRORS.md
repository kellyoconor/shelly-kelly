## [ERR-20260310-001] mini_monty_token_alerts

**Logged**: 2026-03-10T16:36:00-05:00
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Mini Monty sending repeated "200k/200k tokens" alerts inappropriately

### Error
```
🚨 **Mini Monty Alert**

Main session tokens: **200k/200k (100%)**
Threshold: 150k

Your chat session is at maximum context. You'll need to `/restart` to continue normal operation.

Current time: 4:27 PM ET
```

### Context
- Kelly getting this alert message repeatedly 
- Seems to be stuck on repeat or cached weirdly
- Previously had an issue where new sessions were starting with 200k tokens immediately (that was fixed)
- This appears to be alert system malfunction, not actual token counting issue

### Root Cause Found
**MASSIVE skills directory bloat:**
- `/data/workspace/skills/flightclaw/.venv` = **189MB** (Python virtual environment)
- 26 total skills = ~200k characters just in SKILL.md files  
- Total skills directory = 190MB

**Theory:** OpenClaw may be trying to index/load content from entire skills directory, causing massive context bloat

### Immediate Fixes Needed
1. **Remove .venv from flightclaw skill** - shouldn't be there
2. **Add .venv to .gitignore** in flightclaw skill
3. **Investigate if OpenClaw is indexing non-SKILL.md files** in skills directory
4. **Consider skill loading optimization** - 26 skills is a lot of context injection

### Metadata
- Reproducible: yes (happening repeatedly for user)
- Related Files: cron job configs, monty alert system
- Session Context: Fresh session after recent token fixes

## [ERR-20260312-001] agentmail_module_missing

**Logged**: 2026-03-12T16:00:00-05:00
**Priority**: medium
**Status**: pending
**Area**: email

### Summary
AgentMail skill is documented but agentmail Python module is not installed, preventing email access

### Error
```
ModuleNotFoundError: No module named 'agentmail'
```

### Context
- Kelly sent flight delay info to shelly@agentmail.to  
- Tried to check inbox using /data/workspace/skills/agentmail/scripts/client.py
- Skill documentation indicates email should be accessible
- Missing Python package prevents any email operations

### Suggested Fix
Install agentmail package or update skill to use different email access method

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/skills/agentmail/scripts/client.py
- Impact: Can't read emails sent to agent inbox

---## [ERR-20260409-001] openclaw-update-run

**Logged**: 2026-04-09T22:23:30Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`gateway.update.run` failed on a git checkout because it assumes a `main` branch exists.

### Error
```text
error: pathspec 'main' did not match any file(s) known to git
```

### Context
- Operation attempted: OpenClaw self-update after user approval
- Environment: `/openclaw` installed as git checkout in detached HEAD at tag `v2026.3.8`
- Local changes were successfully stashed before retrying update
- Update still failed during `git checkout main`

### Suggested Fix
Detect the repo's default branch dynamically (or handle detached-tag installs explicitly) instead of assuming `main` exists.

### Metadata
- Reproducible: yes
- Related Files: /openclaw

---
## [ERR-20260421-001] combined-context-check-heartbeat

**Logged**: 2026-04-21T19:53:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`combined-context-check.py` was terminated during heartbeat execution before producing output.

### Error
```text
Process exited with signal SIGTERM.
```

### Context
- Operation attempted: `python3 /data/workspace/scripts/combined-context-check.py`
- Trigger: scheduled heartbeat reminder after WhatsApp gateway connected
- Other heartbeat checks in the same run succeeded (`smart-context-check.py`, `alert-retry-processor.cjs`)
- No user-facing issue was surfaced from this run, but the heartbeat context pipeline did not complete cleanly

### Suggested Fix
Check whether the script is hanging on an external dependency, timing out, or being terminated by the runner; consider adding clearer logging or a bounded timeout path.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/combined-context-check.py

---
## [ERR-20260412-001] git_push_auth

**Logged**: 2026-04-12T07:30:30Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Auto git push cron failed because git push over HTTPS could not read GitHub credentials in non-interactive exec.

### Error
```
fatal: could not read Username for https://github.com: No such device or address
```

### Context
- Command/operation attempted: auto commit, pull --rebase, and push for /data/workspace and /data/kelly-vault
- Input or parameters used: non-interactive shell via exec tool
- Environment details if relevant: push attempted to https://github.com/kellyoconor/shelly-kelly from cron context

### Suggested Fix
Configure non-interactive GitHub auth for cron/exec context (credential helper, token-based remote, or SSH remote) before relying on automated pushes.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260413-001] git-push-workspace-auth

**Logged**: 2026-04-13T07:30:55.986514+00:00
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
Workspace repo auto-push failed at `git push origin main` because GitHub credentials were unavailable in this environment.

### Error
```text
fatal: could not read Username for 'https://github.com': No such device or address
```

### Context
- Operation attempted: cron-driven auto git push for `/data/workspace`
- Sequence used: commit → `git pull --rebase origin main` → `git push origin main`
- Commit created successfully: `374e676` (`Auto git push`)
- Remote: `https://github.com/kellyoconor/shelly-kelly.git`

### Suggested Fix
Configure non-interactive GitHub auth for the workspace repo remote (token, credential helper, or authenticated remote URL) before the next auto-push run.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.git/config

### Resolution
- **Resolved**: 2026-04-13T12:36:00Z
- **Commit/PR**: n/a (config change)
- **Notes**: Configured `/data/workspace` local git `credential.helper` to supply `x-access-token` plus `$KELLY_VAULT_TOKEN` for non-interactive HTTPS pushes; verified by successful push of commit `b046807` to `origin/main`.

---

## [ERR-20260413-002] whatsapp-message-target-resolution

**Logged**: 2026-04-13T07:30:55.986514+00:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Failure notification could not be sent because the WhatsApp target name `Kelly` was not resolvable by the messaging tool.

### Error
```text
Unknown target "Kelly" for WhatsApp. Hint: <E.164|group JID>
```

### Context
- Operation attempted: `message.send` on channel `whatsapp`
- Parameters included: `accountId=custom-1`, `target=Kelly`
- Cron instructions required a WhatsApp notification on push failure, but no E.164 number or group JID was provided.

### Suggested Fix
Store Kelly's WhatsApp target as an E.164 number or group JID in a stable note/config and use that exact value for automated notifications.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/TOOLS.md

---
## [ERR-20260415-001] exec_bash_quoting

**Logged**: 2026-04-15T00:04:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Initial vault auto-push exec failed because nested shell quoting broke the bash command substitution string.

### Error
```
%H:%M:%S: -c: line 2: unexpected EOF while looking for matching `)'
```

### Context
- Command/operation attempted: cron-driven vault git auto-push in `/data/kelly-vault`
- Input or parameters used: `bash -lc '... $(date '+%Y-%m-%d %H:%M:%S %Z') ...'`
- Environment details: OpenClaw `exec` with bash wrapper, but single-quote nesting terminated the command early

### Suggested Fix
Avoid nesting single quotes inside a single-quoted `bash -lc` string; use double quotes around the outer script or compute the timestamp separately.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260414-001] exec_shell_pipefail

**Logged**: 2026-04-14T06:00:49Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Initial security review command failed because `/bin/sh` in exec does not support `set -o pipefail`

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: multi-step `exec` shell script for nightly security review
- Environment details: OpenClaw `exec` default shell invoked as `sh`

### Suggested Fix
Use POSIX-compatible shell syntax by default in `exec`, or explicitly invoke `bash -lc` only when bash-specific options are needed.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260415-001] exec-shell

**Logged**: 2026-04-15T06:00:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Initial exec command failed because /bin/sh did not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: multiline shell audit via exec tool
- Input/parameters used: relied on default shell instead of explicit bash
- Environment details: OpenClaw exec defaulted to sh

### Suggested Fix
Wrap complex shell scripts with `bash -lc` when using bash-specific options like `pipefail`.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260415-001] exec-shell-option

**Logged**: 2026-04-15T07:31:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Git automation command failed because exec used /bin/sh, which does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: parallel repo git automation via exec
- Input or parameters used: shell script starting with `set -euo pipefail`
- Environment details if relevant: exec default shell is `/bin/sh`

### Suggested Fix
Use POSIX-safe `set -eu` or explicitly run `bash -lc` when pipefail is needed.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---

## [ERR-20260415-001] read

**Logged**: 2026-04-15T08:00:00Z
**Priority**: low
**Status**: pending
**Area**: docs

### Summary
Session bootstrap tried to read today/yesterday workspace memory files before checking whether they exist

### Error
```
ENOENT: no such file or directory, access /data/workspace/memory/2026-04-15.md
ENOENT: no such file or directory, access /data/workspace/memory/2026-04-14.md
```

### Context
- Operation attempted: bootstrap reads required by AGENTS.md
- Paths may legitimately not exist yet early in the day or if no technical log was created
- Better pattern: check existence first or tolerate missing memory files

### Suggested Fix
Treat missing daily memory files as optional during session bootstrap and avoid logging them as hard failures.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/AGENTS.md

---
## [ERR-20260416-001] exec-shell-pipefail

**Logged**: 2026-04-16T06:00:48+00:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Initial nightly security review command failed because `/bin/sh` does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: composite shell script via exec
- Input or parameters used: `set -euo pipefail` under default shell
- Environment details if relevant: exec uses `/bin/sh` by default in this environment

### Suggested Fix
Use `bash -lc` for scripts that rely on `pipefail` or other bash-specific shell options.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260417-001] alert-retry-processor heartbeat

**Logged**: 2026-04-17T05:53:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Heartbeat alert processor failed immediately with a syntax error when executed as instructed from HEARTBEAT.md.

### Error
```
File "/data/workspace/alert-retry-processor.cjs", line 53
    * Check for Kelly's recent activity and auto-mark alerts as seen
                     ^
SyntaxError: unterminated string literal (detected at line 53)
```

### Context
- Command attempted: `python3 /data/workspace/alert-retry-processor.cjs heartbeat`
- HEARTBEAT.md says to run this on every heartbeat
- The file has a `.cjs` extension, so invoking it with Python is likely wrong or the file contents are malformed for Python execution

### Suggested Fix
Verify the intended runtime for `alert-retry-processor.cjs` (likely `node`, not `python3`) and/or correct the file content so the documented heartbeat command matches the actual executable.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/alert-retry-processor.cjs

---
## [ERR-20260419-001] exec-shell-option

**Logged**: 2026-04-19T07:30:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Initial git automation command failed because exec runs under /bin/sh and does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: parallel auto git push shell scripts
- Input or parameters used: `set -euo pipefail` at top-level without invoking bash explicitly
- Environment details if relevant: OpenClaw `exec` default shell is `sh`

### Suggested Fix
Wrap shell scripts with `bash -lc` when using bash-specific options like `pipefail`.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---

## [ERR-20260421-001] exec-shell

**Logged**: 2026-04-21T07:31:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Initial git automation shell used bash-only pipefail under /bin/sh and failed before running repo sync

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: exec wrapper for auto git push across workspace and vault repos
- Input or parameters used: `set -euo pipefail` in default shell
- Environment details if relevant: exec default shell is /bin/sh, not bash

### Suggested Fix
Use `bash -lc` explicitly for bash features, or stick to POSIX `set -eu`

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---

## [ERR-20260421-001] combined-context-check.py

**Logged**: 2026-04-21T22:56:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Heartbeat combined-context-check.py hung and timed out after 25 seconds with no output

### Error
```
EXIT:124
```

### Context
- Command attempted: `python3 /data/workspace/scripts/combined-context-check.py`
- Trigger: heartbeat routine from /data/workspace/HEARTBEAT.md
- Behavior: initial run hung; second run with `timeout 25s` exited 124 with no stdout

### Suggested Fix
Inspect script for blocking network/tool call or missing timeout handling so heartbeat cannot stall indefinitely.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/combined-context-check.py, /data/workspace/HEARTBEAT.md

---
## [ERR-20260422-001] combined-context-check

**Logged**: 2026-04-22T04:28:44+00:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Heartbeat combined context check hung without producing output and had to be terminated.

### Error
```
python3 /data/workspace/scripts/combined-context-check.py
-> no output after repeated polls; process was still running and was killed
Earlier heartbeat also reported: Exec failed (sharp-at, signal SIGTERM)
```

### Context
- Operation attempted during mandatory heartbeat processing
- Alert retry processor completed successfully
- Combined context script produced no stdout/stderr within ~20 seconds and did not exit

### Suggested Fix
Investigate blocking calls or missing timeouts inside combined-context-check.py so heartbeats do not stall.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/combined-context-check.py

---

## [ERR-20260422-001] exec

**Logged**: 2026-04-22T01:54:34-04:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Heartbeat-related exec session was terminated with SIGTERM before completion

### Error
```
System: [2026-04-22 01:54:34 EDT] Exec failed (neat-bre, signal SIGTERM)
```

### Context
- Operation attempted: heartbeat workflow exec
- Environment: OpenClaw heartbeat session
- Follow-up: reran required heartbeat checks successfully in a new exec session

### Suggested Fix
Review why the original exec was terminated and prefer bounded commands/timeouts for heartbeat scripts that may hang.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/HEARTBEAT.md

---
## [ERR-20260422-001] exec-shell

**Logged**: 2026-04-22T06:00:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Initial security review command failed because /bin/sh did not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: multi-step `exec` script for nightly security review
- Input or parameters used: shell prologue with `set -euo pipefail`
- Environment details if relevant: `exec` default shell was `/bin/sh`, not bash

### Suggested Fix
Wrap multi-step scripts with `bash -lc` when relying on `pipefail`.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---

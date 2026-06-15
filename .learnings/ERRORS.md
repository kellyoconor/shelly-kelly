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

---

## [ERR-20260531-001] exec-heredoc-shell-script

**Logged**: 2026-05-31T02:05:00-04:00
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
A follow-up review command failed because the inline /bin/sh script had mismatched block quoting/braces.

### Error
```
sh: 44: Syntax error: end of file unexpected (expecting "}")
```

### Context
- Operation attempted: run a second-pass nightly security review summary command via `exec`
- Environment: OpenClaw `exec` using `/bin/sh`
- Likely cause: malformed heredoc / grouping in a long inline shell command

### Suggested Fix
Prefer shorter commands or write the inspection script to a temp file before execution when combining shell groups and Python heredocs under `/bin/sh`.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/TOOLS.md

---

## [ERR-20260409-001] openclaw-update-run

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

## [ERR-20260422-001] heartbeat_exec_failure

**Logged**: 2026-04-22T09:00:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
A heartbeat-related exec session (`glow-wil`) was terminated with SIGTERM.

### Error
```
System: [2026-04-22 05:00:02 EDT] Exec failed (glow-wil, signal SIGTERM)
```

### Context
- Operation attempted: scheduled heartbeat execution
- Environment: OpenClaw main session / heartbeat channel
- Follow-up action: rerunning heartbeat checks directly in a fresh turn

### Suggested Fix
If this recurs, inspect whether the prior heartbeat command is timing out or being cancelled by overlap with the next scheduled run.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/HEARTBEAT.md

---

## [ERR-20260422-002] combined-context-check-heartbeat

**Logged**: 2026-04-22T09:33:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`combined-context-check.py` was terminated with SIGTERM during heartbeat processing.

### Error
```text
python3 /data/workspace/scripts/combined-context-check.py
-> Process exited with signal SIGTERM.
```

### Context
- Operation attempted: mandatory heartbeat combined context check from `/data/workspace/HEARTBEAT.md`
- Other heartbeat checks in the same turn succeeded (`smart-context-check.py`, `alert-retry-processor.cjs`)
- This is another recurrence of the combined context script failing to complete cleanly during heartbeat execution

### Suggested Fix
Investigate blocking work or overlapping heartbeat runs inside `combined-context-check.py`; add internal timeouts or faster fail behavior so heartbeat does not get killed mid-run.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/combined-context-check.py, /data/workspace/HEARTBEAT.md
- See Also: ERR-20260421-001, ERR-20260422-001

---

## [ERR-20260422-003] combined-context-check-heartbeat

**Logged**: 2026-04-22T09:35:30Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
`combined-context-check.py` hung during heartbeat processing and required manual termination.

### Error
```text
python3 /data/workspace/scripts/combined-context-check.py
-> no output within 30s; process still running and was killed
```

### Context
- Operation attempted: mandatory heartbeat combined context check from `/data/workspace/HEARTBEAT.md`
- Alert retry processor completed successfully in the same turn
- This is another recurrence of the combined context script not exiting promptly during heartbeat

### Suggested Fix
Add bounded timeouts and better internal logging inside `combined-context-check.py`, and investigate any blocking dependency so heartbeat stays fast and reliable.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/combined-context-check.py, /data/workspace/HEARTBEAT.md
- See Also: ERR-20260421-001, ERR-20260422-001, ERR-20260422-002

---

## [ERR-20260422-003] heartbeat-checks-sigterm-burst

**Logged**: 2026-04-22T09:36:30Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Multiple heartbeat context checks were terminated with SIGTERM within a few minutes, preventing the normal heartbeat pipeline from completing cleanly.

### Error
```text
python3 /data/workspace/scripts/smart-context-check.py -> Process exited with signal SIGTERM
python3 /data/workspace/scripts/combined-context-check.py -> Process exited with signal SIGTERM
```

### Context
- Trigger: scheduled heartbeat reminder after system exec failure notice
- Alert retry processor still completed successfully
- This happened again minutes after earlier SIGTERM heartbeat failures, suggesting overlap, timeout pressure, or another runner-level interruption rather than a one-off script blip

### Suggested Fix
Inspect overlapping heartbeat scheduling or runner cancellation behavior, and add bounded execution / skip-if-already-running logic to the context scripts.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/scripts/smart-context-check.py, /data/workspace/scripts/combined-context-check.py
- See Also: ERR-20260421-001, ERR-20260422-001, ERR-20260422-002

---

## [ERR-20260423-001] exec-shell-default

**Logged**: 2026-04-23T06:03:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Initial security-review shell command failed because exec defaulted to /bin/sh, which does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: nightly security review batch script via exec
- Parameters used: shell snippet starting with `set -euo pipefail`
- Environment details: OpenClaw exec wrapper invoked `sh -c` unless explicitly wrapped with `bash -lc`

### Suggested Fix
Wrap pipefail-dependent scripts with `bash -lc` when using exec.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260425-001] exec-shell

**Logged**: 2026-04-25T07:30:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Shell command failed because `/bin/sh` does not support `set -o pipefail` in this exec environment.

### Error
```text
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: git automation script via `exec`
- Input/parameters used: inline shell script beginning with `set -euo pipefail`
- Environment details: `exec` default shell invoked `sh`, not `bash`

### Suggested Fix
Wrap shell scripts with `bash -lc` when relying on `pipefail` or bash-specific behavior.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260427-001] nightly-security-review-script

**Logged**: 2026-04-27T06:00:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Inline Python audit script failed due to an f-string expression containing a backslash while formatting allowlist debug output.

### Error
```text
SyntaxError: f-string expression part cannot include a backslash
```

### Context
- Command/operation attempted: consolidated nightly security review via `python3 - <<'PY' ... PY`
- Failure occurred while building a debug string for WhatsApp allowlist inspection
- Environment: OpenClaw main session on /data/workspace

### Suggested Fix
Avoid regex literals with backslashes inside f-string expressions; compute the value before formatting or use plain string concatenation / repr.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260429-001] exec-shell

**Logged**: 2026-04-29T07:30:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Initial git automation command failed because the default exec shell did not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: run a bash-style multi-repo git automation script via `exec`
- Input or parameters used: `set -euo pipefail` at script start without explicitly invoking bash
- Environment details if relevant: `exec` used default shell (`sh`), which rejected `pipefail`

### Suggested Fix
Invoke the script with `bash -lc` when relying on bash-only shell options.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260505-001] exec-shell-pipefail

**Logged**: 2026-05-05T07:31:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Git automation command failed because `exec` used `/bin/sh`, which does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: combined context check + git automation via `exec`
- Input/parameters used: shell script beginning with `set -euo pipefail`
- Environment details: OpenClaw `exec` default shell was `sh`, not `bash`

### Suggested Fix
Wrap shell scripts needing `pipefail` in `bash -lc '...'` when using `exec`.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/.learnings/ERRORS.md

---
## [ERR-20260506-001] exec-shell-pipefail

**Logged**: 2026-05-06T07:30:21Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
OpenClaw exec uses /bin/sh by default, so `set -o pipefail` failed and aborted a git automation command.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: parallel git automation for workspace and vault repos
- Input or parameters used: `set -euo pipefail` in `exec` shell command
- Environment details if relevant: OpenClaw `exec` launched `sh`, not bash

### Suggested Fix
Avoid bash-specific shell options in `exec` commands unless invoking `bash -lc ...` explicitly.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/TOOLS.md

---
## [ERR-20260512-001] alert-retry-processor-heartbeat

**Logged**: 2026-05-12T05:24:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Heartbeat alert processor failed immediately with a JavaScript syntax error, blocking the first required heartbeat check.

### Error
```
File "/data/workspace/alert-retry-processor.cjs", line 53
    * Check for Kelly's recent activity and auto-mark alerts as seen
                     ^
SyntaxError: unterminated string literal (detected at line 53)
```

### Context
- Command attempted: `python3 /data/workspace/alert-retry-processor.cjs heartbeat`
- Triggered while handling scheduled heartbeat instructions from HEARTBEAT.md
- Failure occurred before any alert processing could run

### Suggested Fix
Run the file with Node instead of Python if it is valid JavaScript, or repair the file contents if the script itself is malformed.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/alert-retry-processor.cjs

---
## [ERR-20260512-001] exec-shell-printf

**Logged**: 2026-05-12T06:24:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Portable /bin/sh `printf` treated a leading `---` format string as an illegal option.

### Error
```
sh: 6: printf: Illegal option --
```

### Context
- Command/operation attempted: heartbeat multi-step shell command via OpenClaw `exec`
- Used `printf '---SMART---\n'` under `/bin/sh`
- Existing guidance already notes exec uses `/bin/sh` by default

### Suggested Fix
Use `echo` for plain section headers or `printf '%s\n' '---SMART---'` to avoid option parsing on portable shells.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/TOOLS.md

---
## [ERR-20260526-001] test-script-invocation

**Logged**: 2026-05-26T15:48:10+00:00
**Priority**: low
**Status**: pending
**Area**: tests

### Summary
A shell test script was accidentally invoked with Python, producing a misleading syntax error.

### Error
```text
File "/data/workspace/scripts/test-proactive-presence.sh", line 49
    python3 scripts/kelly-followups.py surfaced fu-001 >/dev/null || fail "mark surfaced"
                                                   ^^
SyntaxError: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers
```

### Context
- Operation attempted: test run for proactive presence status check
- Incorrect invocation used: `python3 /data/workspace/scripts/test-proactive-presence.sh`
- Correct invocation: `sh /data/workspace/scripts/test-proactive-presence.sh`
- The underlying test suite passed when run with the proper interpreter

### Suggested Fix
Match interpreter to script type before execution; `.sh` scripts should be run with `sh`/`bash`, not `python3`.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/scripts/test-proactive-presence.sh, /data/workspace/TOOLS.md

---
## [ERR-20260527-001] heartbeat-exec-sigterm

**Logged**: 2026-05-27T11:56:32Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Scheduled heartbeat reported an exec session terminated with SIGTERM before completion.

### Error
```text
System: [2026-05-27 07:56:32 EDT] Exec failed (brisk-nu, signal SIGTERM)
```

### Context
- Operation attempted: scheduled heartbeat workflow
- Follow-up heartbeat checks were rerun manually in a fresh turn
- `smart-context-check.py` and `alert-retry-processor.cjs` completed; bounded rerun of `combined-context-check.py` exited cleanly
- Likely a runner interruption or overlap rather than a confirmed user-facing issue

### Suggested Fix
Inspect whether overlapping heartbeat jobs or long-running follow-up commands are causing the runner to terminate prior exec sessions.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/HEARTBEAT.md
- See Also: ERR-20260422-001, ERR-20260422-002, ERR-20260422-003

---
## [ERR-20260527-001] check-and-log-conversation.py

**Logged**: 2026-05-27T08:05:00-04:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Heartbeat session summary script appeared to hang with no output during routine heartbeat processing

### Error
```
python3 /data/workspace/scripts/check-and-log-conversation.py "Heartbeat ran: alert retry processor completed; combined context check produced no actionable output."
Process remained running with no output until manually killed.
```

### Context
- Operation attempted during mandatory heartbeat flow from HEARTBEAT.md
- alert-retry-processor completed successfully
- combined-context-check.py returned no actionable output
- summary script was launched via exec and required manual kill after poll/log showed no output

### Suggested Fix
Inspect check-and-log-conversation.py for blocking waits or dependencies that stall in non-interactive heartbeat runs; consider adding timeout-safe logging or a heartbeat mode.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/check-and-log-conversation.py, /data/workspace/HEARTBEAT.md

---
## [ERR-20260527-002] heartbeat-command-runtime

**Logged**: 2026-05-27T12:08:30Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
I initially invoked the heartbeat alert processor with Python instead of Node, causing an avoidable syntax error.

### Error
```text
python3 /data/workspace/alert-retry-processor.cjs heartbeat
File "/data/workspace/alert-retry-processor.cjs", line 53
    * Check for Kelly's recent activity and auto-mark alerts as seen
                     ^
SyntaxError: unterminated string literal (detected at line 53)
```

### Context
- Operation attempted: required heartbeat alert retry processor from /data/workspace/HEARTBEAT.md
- The documented command uses `node`, but I used `python3` by mistake
- Follow-up: reran with `node /data/workspace/alert-retry-processor.cjs heartbeat` and the heartbeat pipeline completed successfully

### Suggested Fix
Follow HEARTBEAT.md command runtimes exactly; `.cjs` heartbeat scripts should be run with Node, not Python.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/alert-retry-processor.cjs
- See Also: ERR-20260512-001, ERR-20260417-001

---
## [ERR-20260528-001] heartbeat-alert-retry-processor

**Logged**: 2026-05-28T06:54:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Tried to run a `.cjs` heartbeat script with `python3`, causing an immediate syntax error.

### Error
```
File "/data/workspace/alert-retry-processor.cjs", line 53
    * Check for Kelly's recent activity and auto-mark alerts as seen
                     ^
SyntaxError: unterminated string literal (detected at line 53)
```

### Context
- Command attempted: `python3 /data/workspace/alert-retry-processor.cjs heartbeat`
- The target file is a CommonJS `.cjs` script and should be run with `node`, not `python3`.
- This happened during a scheduled heartbeat check.

### Suggested Fix
Run `.cjs` scripts with `node` and keep Python invocations only for `.py` scripts.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/alert-retry-processor.cjs, /data/workspace/HEARTBEAT.md

---
## [ERR-20260528-002] morning-briefing-cron-reminder-instead-of-execution

**Logged**: 2026-05-28T10:35:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
The 6:30 AM morning briefing schedule delivered reminder text into chat instead of actually running the morning briefing script and sending its output.

### Error
```
System: [2026-05-28 06:30:00 EDT] Run the morning briefing: `python3 /data/workspace/scripts/morning-briefing.py` — send the exact output to Kelly via WhatsApp (accountId: custom-1, target: +13018302401). Then run `python3 /data/workspace/scripts/morning-briefing.py --append-daily-note` to update the vault. Keep it fast — no extra commentary, just send the briefing output as-is.
```

### Context
- A scheduled reminder fired at 6:30 AM.
- Instead of executing the briefing workflow, the system surfaced the reminder text back into the chat.
- Manual verification showed `python3 /data/workspace/scripts/morning-briefing.py` itself works and returns a valid briefing.
- This indicates the scheduled job/reminder wiring is broken or configured as a reminder relay instead of an execution path.

### Suggested Fix
Inspect the cron/job configuration for the 6:30 AM morning briefing and convert it from a reminder-style payload to an execution path that actually runs the script, sends the output via `message`, and appends to the daily note.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/scripts/morning-briefing.py, cron job config
- Source: user_feedback

---
## [ERR-20260606-001] exec-shell-summary-redirection

**Logged**: 2026-06-06T06:01:45Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
A /bin/sh summary step failed because input-redirection paths were over-escaped inside command substitution.

### Error
```
sh: cannot open "/tmp/security-review-.../auto_redact.txt": No such file
```

### Context
- Command/operation attempted: nightly security review summary generation via `exec`
- Used `wc -l < \"$TMPDIR/file\"` inside a shell block
- OpenClaw `exec` runs under `/bin/sh`

### Suggested Fix
Use portable forms like `wc -l "$file" | awk '{print $1}'` or unescaped redirection paths.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/TOOLS.md

---

## [ERR-20260607-001] smart-context-check-strava

**Logged**: 2026-06-07T07:13:38Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Strava check failed during smart-context-check heartbeat runs

### Error
```
smart-context-check reported: Running: ❌ Don't ask - ❌ Strava check failed
```

### Context
- Command attempted: `python3 /data/workspace/scripts/smart-context-check.py`
- Trigger: scheduled heartbeat context validation
- Impact: running context became unavailable, so avoid run-related prompts

### Suggested Fix
Inspect the underlying Strava check used by smart-context-check and harden failure handling/logging so the root cause is visible.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/scripts/smart-context-check.py

---

## [ERR-20260608-001] alert-retry-processor

**Logged**: 2026-06-08T00:54:00-04:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Heartbeat alert retry processor failed with a JavaScript syntax error instead of running normally.

### Error
```
File "/data/workspace/alert-retry-processor.cjs", line 53
    * Check for Kelly's recent activity and auto-mark alerts as seen
                     ^
SyntaxError: unterminated string literal (detected at line 53)
```

### Context
- Command/operation attempted: `python3 /data/workspace/alert-retry-processor.cjs heartbeat`
- Trigger: scheduled heartbeat reminder after WhatsApp gateway connected
- Environment: OpenClaw main session on host Linux

### Suggested Fix
Inspect `/data/workspace/alert-retry-processor.cjs` around line 53 for malformed quoting or a broken comment/string; use the correct runtime if the file is intended for Node instead of Python.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/alert-retry-processor.cjs

---
## [ERR-20260608-001] openclaw-logs-cli

**Logged**: 2026-06-08T12:27:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Attempted to use unsupported `--lines` flag with `openclaw logs`

### Error
```
error: unknown option '--lines'
```

### Context
- Command attempted: `openclaw logs --lines 120`
- Goal: inspect recent runtime logs while diagnosing a Railway downtime alert
- Environment: OpenClaw v2026.3.8 on Linux

### Suggested Fix
Use `openclaw logs --help` first when log CLI flags are uncertain; avoid assuming common flag names.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/TOOLS.md

---

## [ERR-20260611-001] git_commit_identity_missing

**Logged**: 2026-06-11T11:53:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
Git commit in /openclaw failed because user.name/user.email were not configured in this environment.

### Error
```
Author identity unknown
fatal: unable to auto-detect email address
```

### Context
- Command attempted: git commit -m "Suppress WhatsApp gateway status reminders"
- Repo: /openclaw
- Fix: set repo-local git user.name and user.email before retrying

### Suggested Fix
Configure repo-local git identity for automated commits in this environment.

### Metadata
- Reproducible: yes
- Related Files: /openclaw/.git/config

---

## [ERR-20260611-003] openclaw_cron_config_invalid

**Logged**: 2026-06-12T03:02:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
OpenClaw cron job creation failed because local CLI config referenced a missing plugin manifest at /openclaw/extensions/openclaw.plugin.json.

### Error
```
Invalid config at /data/.clawdbot/openclaw.json
- plugins: plugin: plugin manifest not found: /openclaw/extensions/openclaw.plugin.json
```

### Context
- Command attempted: openclaw cron add --json ...
- Goal: create 4-day follow-up reminder/check-in
- User explicitly wants reminder scheduling to work reliably

### Suggested Fix
Repair /data/.clawdbot/openclaw.json plugin path(s) or run openclaw doctor --fix, then retry cron creation.

### Metadata
- Reproducible: yes
- Related Files: /data/.clawdbot/openclaw.json

---
## [ERR-20260612-001] message.whatsapp_send_no_listener

**Logged**: 2026-06-12T06:01:17Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
WhatsApp alert delivery failed during nightly security review because account `custom-1` had no active WhatsApp Web listener.

### Error
```
Error: No active WhatsApp Web listener (account: custom-1). Start the gateway, then link WhatsApp with: openclaw channels login --channel whatsapp --account custom-1.
```

### Context
- Operation attempted: `message.send` to WhatsApp account `custom-1`
- Purpose: alert Kelly about non-workspace secret-bearing files found during the 2026-06-12 nightly security review
- Environment: gateway running, but WhatsApp listener for `custom-1` unavailable

### Suggested Fix
Verify WhatsApp account linkage/listener health before relying on `message.send` for security alerts, or add a fallback channel when WhatsApp is disconnected.

### Metadata
- Reproducible: unknown
- Related Files: /data/workspace/memory/security-log.md

---
## [ERR-20260615-001] whatsapp_message_send

**Logged**: 2026-06-15T01:01:35Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
Weekly Kelly OS Report could not be delivered via WhatsApp because account `custom-1` had no active WhatsApp Web listener.

### Error
```
Error: No active WhatsApp Web listener (account: custom-1). Start the gateway, then link WhatsApp with: openclaw channels login --channel whatsapp --account custom-1.
```

### Context
- Operation attempted: `message.send` to WhatsApp
- Account: `custom-1`
- Target: `+13018302401`
- Payload: weekly Kelly OS report for 2026-06-08 through 2026-06-14
- Report was successfully written to `/data/workspace/tracking/reports/2026-06-14.md`
- A related listener failure had already been noted on 2026-06-14 in workspace memory.

### Suggested Fix
Re-link or restore the WhatsApp listener for `custom-1` before relying on WhatsApp delivery from cron jobs. If weekly reports must remain reliable, consider a Telegram-first fallback or a preflight listener check before long message sends.

### Metadata
- Reproducible: yes
- Related Files: /data/workspace/tracking/reports/2026-06-14.md, /data/workspace/memory/2026-06-14.md
- See Also: none

---

# Feature Requests

## [FEAT-20260505-001] whoop_integration

**Logged**: 2026-05-05T14:13:42Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Requested Capability
Integrate with Kelly's WHOOP data so Shelly can use it in conversations and recovery/training context.

### User Context
Kelly asked whether Shelly can integrate with WHOOP, likely to improve health/recovery awareness beyond current run and sleep signals.

### Complexity Estimate
medium

### Suggested Implementation
Investigate whether WHOOP offers an accessible API, export path, or webhook/auth flow that can be wrapped in a workspace skill similar to Oura/Strava.

### Metadata
- Frequency: first_time
- Related Features: oura,strava

---
## [FEAT-20260616-001] whoop-integration

**Logged**: 2026-06-16T12:27:30Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Requested Capability
Integrate Kelly's WHOOP data into Shelly/OpenClaw so WHOOP becomes a first-class data source alongside Oura and Strava.

### User Context
Kelly considers WHOOP an important data source and wants help using it for recovery/load interpretation instead of relying on screenshots.

### Complexity Estimate
medium

### Suggested Implementation
Prefer official WHOOP Developer Platform OAuth integration if feasible for a single-user app; fallback to WHOOP data export CSV ingestion if OAuth setup is too heavy. Avoid collecting raw credentials in chat.

### Metadata
- Frequency: first_time
- Related Features: oura,strava,context-check

---

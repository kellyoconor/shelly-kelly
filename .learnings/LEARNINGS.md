# LEARNINGS.md

Log of corrections, knowledge gaps, and best practices for continuous improvement.

---

## [LRN-20260407-001] date_time_verification

**Logged**: 2026-04-07T12:48:00Z
**Priority**: high  
**Status**: pending
**Area**: behavioral

### Summary
Repeatedly getting days of week wrong despite having access to current date/time data

### Details
Kelly has corrected me "quite a bit recently" for mixing up what day it is. Most recent example: called Tuesday morning a "Monday morning" when talking about her run. I have access to time stamps in every message and session_status tool but keep making assumptions instead of checking.

### Suggested Action
1. Always verify current day/date when referencing "today," "this morning," etc.
2. Use session_status or check message timestamps before making time references
3. Stop making assumptions about days/dates

### Metadata
- Source: user_feedback 
- Related Files: N/A
- Tags: date_time, behavioral_correction, recurring_issue
- Recurrence-Count: Multiple times per Kelly's feedback
- Pattern-Key: behavioral.verify_datetime

---
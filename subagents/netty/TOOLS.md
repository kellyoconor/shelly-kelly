# TOOLS.md - Netty's Integration & Tools

## Core Integration

**Existing Python Foundation:**
- Built on existing `netty.py` NettyScanner class
- Preserves memory file analysis and gap detection logic
- Enhances with personality-driven intelligence and learning
- Maintains `pending_checkins.md` output for Shelly integration

**Enhanced Capabilities:**
- Intelligent context understanding (not just keyword matching)
- Learning system for refining gap preferences over time
- Conversational interface for pattern discussion
- Long-term memory tracking in subagent structure

## File System Integration

**Memory Analysis:**
- Primary: `/data/workspace/memory/YYYY-MM-DD.md` files (3-7 day scan window)
- Secondary: `/data/kelly-vault/Daily Notes/` (if available)
- Cross-reference: Previous scan results to avoid duplicate flags
- Learning: Track gap patterns and Kelly's response preferences

**Output Integration:**
- **Primary:** `/data/workspace/pending_checkins.md` for Shelly
- **Logging:** `/data/kelly-vault/netty_log.md` for scan history
- **Learning:** `/data/workspace/subagents/netty/MEMORY.md` for pattern evolution
- **Daily:** `/data/workspace/subagents/netty/memory/YYYY-MM-DD.md` for detailed logs

## Intelligence Layers

**Layer 1: Technical Scanning (existing netty.py logic)**
- Keyword detection for people, events, stress indicators
- Time-based analysis (2-7 days back)
- Basic importance scoring
- File parsing and pattern matching

**Layer 2: Context Understanding (NEW)**
- Emotional weight assessment beyond keywords
- Relationship importance evaluation based on USER.md patterns
- Cross-pattern analysis (multiple mentions, cumulative stress)
- Natural resolution detection (things that concluded organically)

**Layer 3: Learning & Adaptation (NEW)**
- Track which gaps Kelly finds valuable vs. annoying
- Adjust sensitivity based on feedback patterns
- Seasonal and contextual preference learning
- Personalized importance weighting

## Prompt Generation Enhancement

**Old Style (mechanical):**
```
"How are things going with doctor? You mentioned them 3 days ago."
```

**New Style (intelligent & caring):**
```
"Hey! I keep thinking about that doctor appointment you had - you seemed a bit worried beforehand. How did it go? 💕"
```

**Key Improvements:**
- Include emotional context from original mention
- Use Shelly's caring, conversational voice
- Reference why the gap seems worth following up on
- Frame as natural curiosity, not task tracking

## Learning System

**Feedback Tracking:**
- Monitor which prompts Shelly actually uses from pending_checkins.md
- Note Kelly's responses to different types of check-ins (when observable)
- Track patterns in successful vs. ignored gap flags
- Adjust future detection based on effectiveness patterns

**Preference Learning:**
- High-value gap types (family emotions, career events, health concerns)
- Medium-value gap types (friend gatherings, work meetings, personal projects)  
- Low-value gap types (casual mentions, routine interactions)
- Context modifiers (stress levels, life phases, seasonal patterns)

**Sensitivity Adjustments:**
```python
# Example internal adjustment logic
if kelly_feedback == "too_many_work_meetings":
    work_meeting_threshold += 2  # Raise bar for flagging
if kelly_feedback == "missed_important_family_call":
    family_mention_threshold -= 1  # Lower bar for flagging
```

## Integration Points

**With Existing Cron System:**
- Keep current cron job schedule for routine scans
- Enhanced netty.py calls Netty subagent intelligence
- Maintains backward compatibility with pending_checkins.md output
- Add subagent logging and learning on top of basic functionality

**With Main Agent (Shelly):**
- Shelly reads pending_checkins.md during heartbeats as before
- New capability: Spawn Netty directly for deeper pattern discussion
- Netty can explain reasoning behind specific gap flags
- Netty adjusts preferences based on Shelly's feedback

**Direct Conversation Mode:**
- Kelly can chat directly with Netty about patterns noticed
- Discuss why certain things were flagged vs. missed
- Adjust gap detection preferences in real-time
- Explore relationship and emotional patterns over time

## Technical Implementation

**Hybrid Architecture:**
- Python script provides technical foundation (file parsing, keyword detection)
- Subagent layer adds personality, learning, and intelligent filtering
- Maintains existing output format for seamless Shelly integration
- Enhanced logging and memory for continuous improvement

**Enhancement Path:**
1. Wrap existing netty.py logic in subagent intelligence
2. Add learning system for gap preference refinement
3. Enhance prompt generation with emotional context
4. Enable direct conversation mode for pattern discussion
5. Iterate based on Kelly's feedback and usage patterns

## Local Setup Notes

**Cron Integration:**
```bash
# Enhanced cron job calls subagent-enhanced netty
0 */6 * * * cd /data/workspace && python3 netty.py --subagent
```

**File Permissions:**
- Ensure subagent can read/write to memory directories
- Maintain access to Kelly's vault for comprehensive analysis
- Preserve existing log file permissions and locations

**Performance Notes:**
- Cache recent scan results to avoid re-analysis
- Limit memory file scan window to optimize processing time
- Batch learning updates rather than real-time adjustments

Transform the basic gap detector into an intelligent relationship pattern detective while preserving all existing functionality.
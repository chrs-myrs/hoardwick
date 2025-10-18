---
criticality: USEFUL
failure_mode: Without learning from decisions, cleanup recommendations don't improve
constrained_by: specs/workspace/patterns.spec.md
---

# Preference Learning System

## Requirements

### Classification System

**Project Activity Classification:**
- System classifies projects based on modification time and user overrides
- Three categories: active (<90 days), semi-active (<365 days), stale (>365 days)
- User-marked projects treated as active regardless of modification time
- Classification considers both filesystem timestamps and git activity

**User Preference Storage:**
- Stores classification rules in `.hoardwick-preferences.json`
- Tracks known active projects list
- Defines activity thresholds (configurable)
- Records cleanup rules (safe to remove, always keep)

### Learning from Decisions

**Pattern Recognition:**
- When user overrides age-based rules (keeps old project), system learns exception
- When user confirms removal pattern, system reinforces safe_to_remove rule
- Preferences evolve based on actual cleanup decisions

**Observable Outcomes:**
- User can classify all projects with single command
- System highlights projects marked in preferences (visual distinction)
- User can add/remove projects from active list
- Classification query runs in <5 seconds for large datasets

### Data Separation

**Classification vs Logging:**
- Preferences JSON contains: rules, thresholds, active projects list
- Preferences JSON does NOT contain: cleanup history, session logs, detailed decisions
- Cleanup history belongs in database tables or markdown files
- This prevents JSON bloat and maintains clean architecture

### Non-Requirements

- Does not automatically update preferences (user controls classification)
- Does not analyze git history (uses filesystem timestamps only)
- Does not integrate with external tools (works offline)
- Does not require machine learning (rule-based system sufficient)

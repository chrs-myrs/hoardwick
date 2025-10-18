---
criticality: USEFUL
failure_mode: Without preference tracking, cleanup decisions don't improve over time
satisfies: specs/3-behaviors/preference-learning.spec.md
---

# Preferences Script Specification

## Requirements

### Observable Behavior

**Command: `python3 scripts/preferences.py classify`**
- Reads scan data from generated/hoardwick.db (most recent complete scan)
- Reads preferences from .hoardwick-preferences.json
- Classifies projects into three categories:
  - Active: Modified within 90 days OR in known_active_projects list
  - Semi-active: Modified within 365 days
  - Stale: Not modified in >365 days
- Displays rich table showing project name, file count, size, age, preference status
- Shows summary counts for each category

**Command: `python3 scripts/preferences.py mark-active PROJECT_NAME`**
- Adds project to known_active_projects list in preferences.json
- Saves updated preferences
- Reports success

**Command: `python3 scripts/preferences.py mark-inactive PROJECT_NAME`**
- Removes project from known_active_projects list
- Saves updated preferences
- Reports success

**Command: `python3 scripts/preferences.py show`**
- Displays current preferences from .hoardwick-preferences.json
- Shows active projects list
- Shows activity thresholds
- No database access required

### Input/Output

**Inputs:**
- `generated/hoardwick.db`: SQLite database with scan data
- `.hoardwick-preferences.json`: User preferences and classification rules

**Outputs:**
- Rich formatted terminal tables and text
- Updated .hoardwick-preferences.json (for mark-active/mark-inactive commands)

**Exit codes:**
- 0: Success
- 1: Error (missing database, invalid preferences file, etc.)

### Key Classes

**PreferenceManager:**
- Loads/saves .hoardwick-preferences.json
- Manages known_active_projects list
- Provides is_active_project() check

**ProjectAnalyser:**
- Connects to hoardwick.db
- Queries files table for project-level statistics
- Applies threshold rules from PreferenceManager
- Returns classified project dictionaries

### Performance

- classify command: <5 seconds for 600k file database
- mark-active/mark-inactive: <1 second
- show command: <1 second (no database access)

### Non-Requirements

- Does not modify scan database
- Does not perform cleanup operations
- Does not log cleanup history (preferences.json is for classification only)
- Does not require network access

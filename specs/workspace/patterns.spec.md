---
criticality: IMPORTANT
failure_mode: Inconsistent patterns make codebase harder to understand and maintain
governed-by: .livespec/standard/metaspecs/workspace.spec.md
---

# Hoardwick Development Patterns

## Requirements

**Specification Patterns:**
- All .spec.md files follow MSL format (YAML frontmatter, Requirements section)
- Apply MSL minimalism: justify each requirement's existence
- Each spec declares dependencies via frontmatter (derives_from, constrained_by, satisfies)
- One spec per behavior or component

**Naming Conventions:**
- Specs: `descriptive-name.spec.md`
- Script specs: `script-name.spec.md` (matches Python file name)
- Python scripts: `snake_case.py`
- CLI commands: `kebab-case` flags

**Code Organization:**
- Executable scripts in `scripts/` directory
- Each Python script has matching `.spec.md` file in same directory
- Generated outputs in `generated/` (gitignored)
- Working files in `.tmp/` and `.scratch/` (gitignored)
- Archive old files to `.archive/` (gitignored) if needed
- Database: `generated/hoardwick.db`

**Data Storage Patterns:**
- JSON files for classification and configuration only
- Never use JSON for operational logging or history
- Logs and history go to: markdown files, database tables, or dedicated log files
- JSON bloat indicates architectural smell (wrong abstraction layer)

**Python Patterns:**
- Type hints for function signatures
- Docstrings for public functions and classes
- Use `pathlib.Path` for path handling (never string concatenation)
- Use `click` for CLI interfaces with rich help text
- Use `rich` for terminal output (tables, progress, colors)
- Explicit `python3` and `pip3` in documentation

**Testing Patterns:**
- Manual testing on safe directories first
- Test cross-platform path handling (WSL + Windows)
- Verify `--dry-run` modes work correctly
- No pytest required initially (manual validation sufficient)

**Safety Patterns:**
- All destructive operations require explicit flags
- Preview-before-action for cleanup commands
- Confirmation prompts for irreversible operations
- Read-only by default

**Performance Patterns:**
- Aggregate large repetitive directories (node_modules, .cache, .git)
- Treat aggregates as single units in scans and reports
- Lazy computation: hash files only when duplicate detection needed
- Missing aggregate patterns cause exponential performance degradation (437k files → 1 aggregate)

**Cross-Platform Performance:**
- Scanning Windows from WSL is 10-100x slower than native Windows tools
- Large database files (>500 MB) cause performance issues and "disk full" errors
- For Windows: use native PowerShell/TreeSize or scan focused chunks
- Monitor database growth; warn or stop scans approaching 1 GB
- Multiple VHDXs may exist (Ubuntu, Docker, other distros) - check all

**Database Size Management:**
- SQLite databases >700 MB cause crashes and corruption risks
- Scan in focused chunks for large filesystems (by directory, not entire drive)
- Archive completed scan databases before starting new large scans
- Provide progress indicators during long scans (user communication)

**Database Staleness Patterns:**
- Store metadata: scan timestamps, completion status, data version in scans table
- Check freshness before analysis: compare scan.completed timestamp to current time
- Warning thresholds: >6 hours = notice, >24 hours = strong warning, >7 days = require rescan
- Archive old databases by date: `mv hoardwick.db hoardwick.db.YYYY-MM-DD`
- Show scan age in all reports: "Based on scan from 2025-10-16 14:30 (25 hours ago)"
- After major cleanup: Mark database stale or rescan affected areas

**Rationale**: Session 2 used yesterday's database showing 43.9 GB UV cache. Already cleaned, only 964 MB remained. Recommendations 90% wrong due to stale data.

**PowerShell Integration Pattern:**
- Use native Windows tools from WSL for Windows filesystem operations
- Path: `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "..."`
- Performance gain: 10-100x faster than WSL cross-filesystem access
- Always prefer native tools over WSL accessing /mnt/c/ paths
- Example: `Get-ChildItem -Recurse -File -Force` for directory scanning
- Fallback: If PowerShell fails, use WSL filesystem access

**Rationale**: Python scan from WSL: 45+ mins, incomplete. PowerShell scan: 3 mins, complete. Native tools dramatically faster.

**Validation:**
  - All Python scripts have matching .spec.md files
  - Scripts use pathlib for paths
  - CLI uses click + rich
  - Generated content goes to generated/
  - No duplicate files (evolve existing instead)

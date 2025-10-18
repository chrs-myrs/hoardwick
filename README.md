# Hoardwick

**LLM-first data management system for comprehensive storage analysis and cleanup**

## Overview

Hoardwick is a production-ready storage management tool designed for large, complex filesystems across WSL, Windows, and network drives. Unlike traditional cleanup tools, it combines comprehensive scanning with LLM-assisted classification to provide intelligent, actionable cleanup recommendations.

### Key Features

- **Resumable Scanning**: Checkpoint-based scanning handles timeouts on large filesystems
- **Aggregate Patterns**: Treats `node_modules`, `.git`, and similar directories as single units for performance
- **Symlink Loop Detection**: Safely handles complex directory structures with circular symlinks
- **Lazy Hashing**: Only hashes files when needed for duplicate detection (< 100MB)
- **Multi-Root Support**: Scan WSL, Windows, and network drives separately with labeled scans
- **Built-in Cleanup**: Docker pruning, WSL compaction, cache clearing, build artifact removal

## Quick Start

```bash
# Scan WSL home directory
python3 scripts/scan.py /home/chris --label wsl-home

# Scan Windows user directory (limited depth to avoid timeout)
python3 scripts/scan.py /mnt/c/Users/Chris --label windows-user --max-depth 4

# Analyse for duplicates
python3 scripts/analyse.py --report duplicates

# Clear Docker waste
python3 scripts/cleanup.py docker-prune

# Clear package caches
python3 scripts/cleanup.py clear-cache --type all
```

## Architecture

### Data Storage

**SQLite Database** (`generated/hoardwick.db`):
- `files`: All indexed files with metadata, hashes, aggregation flags
- `directory_stats`: Pre-computed directory statistics
- `scans`: Scan metadata with labels and timestamps
- `scan_progress`: Resumable scan checkpoints

**Markdown Classifications** (`classifications/`):
- LLM-generated hierarchical classifications
- Human-readable action plans
- Structured by storage category and utility

### Scanning Strategy

**Aggregate Patterns** (treated as single units):
- `node_modules/` - npm packages
- `.git/objects/` - git objects
- `__pycache__/` - Python cache
- `.next/`, `dist/`, `target/` - Build outputs
- `venv/`, `.venv/` - Python virtual environments
- `Cache/`, `cache2/` - Browser caches

**Skip Patterns** (excluded entirely):
- `.Trash`, `$RECYCLE.BIN`
- `System Volume Information`
- `.DS_Store`

**Features**:
- Checkpoints every 1000 files (configurable)
- Resumes from last checkpoint on interruption
- Detects symlink loops via inode tracking
- Lazy hashing (only files < 100MB)
- Directory stats computed incrementally

## Commands

### Scanning

```bash
# Basic scan
python3 scripts/scan.py /path/to/scan

# Labeled scan (recommended for multiple roots)
python3 scripts/scan.py /home/chris --label wsl-home

# Resume interrupted scan
python3 scripts/scan.py /home/chris  # Automatically resumes

# Fresh scan (ignore checkpoint)
python3 scripts/scan.py /home/chris --no-resume

# Custom checkpoint frequency
python3 scripts/scan.py /path --checkpoint-every 5000

# Additional exclusions
python3 scripts/scan.py /path --exclude "*.tmp" --exclude "temp"
```

### Analysis

```bash
# Summary report
python3 scripts/analyse.py

# Find duplicates
python3 scripts/analyse.py --report duplicates

# Find stale files (not accessed in N days)
python3 scripts/analyse.py --report stale --stale-days 180

# Export to JSON
python3 scripts/analyse.py --report duplicates --output json > dup.json
```

### Cleanup Operations

```bash
# Docker cleanup
python3 scripts/cleanup.py docker-prune              # Remove dangling
python3 scripts/cleanup.py docker-prune --all        # Remove all unused
python3 scripts/cleanup.py docker-prune --volumes    # Include volumes
python3 scripts/cleanup.py docker-prune --dry-run    # Preview

# WSL disk compaction
python3 scripts/cleanup.py wsl-compact               # Shows manual steps

# Cache clearing
python3 scripts/cleanup.py clear-cache --type npm
python3 scripts/cleanup.py clear-cache --type pip
python3 scripts/cleanup.py clear-cache --type cargo
python3 scripts/cleanup.py clear-cache --type all    # All caches

# Build artifacts
python3 scripts/cleanup.py clear-build-artifacts --root /home/chris/projects
python3 scripts/cleanup.py clear-build-artifacts target dist build  # Custom patterns
```

## Common Workflows

### Initial System Scan

```bash
# Scan each major storage zone separately
python3 scripts/scan.py /home/chris --label wsl-home
python3 scripts/scan.py /mnt/c/Users/Chris --label windows-user
python3 scripts/scan.py /mnt/d --label archive-drive

# Analyse for quick wins
python3 scripts/analyse.py --report duplicates
python3 scripts/analyse.py --report stale --stale-days 365
```

### Project Cleanup

```bash
# Scan project directory
python3 scripts/scan.py /home/chris/projects --label dev-projects

# Clear build artifacts
python3 scripts/cleanup.py clear-build-artifacts --root /home/chris/projects

# Clear npm cache (separate from node_modules)
python3 scripts/cleanup.py clear-cache --type npm
```

### Docker Maintenance

```bash
# Check current usage
docker system df

# Safe cleanup (dangling only)
python3 scripts/cleanup.py docker-prune

# Aggressive cleanup (all unused)
python3 scripts/cleanup.py docker-prune --all --volumes
```

## Database Schema

### files table
```sql
id, path, size, hash, modified, accessed,
parent_dir, depth, extension, file_type,
is_aggregate, aggregate_type, scan_id
```

**Key fields**:
- `is_aggregate`: Boolean, true if this represents aggregated directory
- `aggregate_type`: Type (e.g., "npm packages", "git objects")
- `hash`: NULL for large files or aggregated directories
- `scan_id`: Links to specific scan run

### directory_stats table
```sql
path, file_count, total_size, descendant_count,
oldest_access, pattern, scan_id
```

### scans table
```sql
id, root_path, label, started, completed,
files_found, total_size, status
```

### scan_progress table
```sql
root_path, last_path, files_scanned, status,
started, updated, visited_inodes
```

## Configuration

### Default Exclusions

See `AGGREGATE_PATTERNS` and `SKIP_PATTERNS` in `scripts/scan.py`.

To add custom exclusions:
```bash
python3 scripts/scan.py /path --exclude "pattern1" --exclude "pattern2"
```

### Checkpoint Frequency

Default: Every 1000 files

```bash
python3 scripts/scan.py /path --checkpoint-every 5000  # Less frequent
```

## Troubleshooting

### Scan Times Out

**Solution**: Use labeled scans with checkpoints (default behavior)
```bash
python3 scripts/scan.py /large/path --label big-scan
# If interrupted, just run again - it will resume
```

### Too Many Small Files

**Solution**: Aggregate patterns handle this automatically
- `node_modules/` → single database entry
- `.git/` → single aggregated entry
- Build dirs → aggregated

### Symlink Loops

**Solution**: Automatic inode-based loop detection
- Loops detected and skipped
- Warning printed to console
- Scan continues safely

### Database Too Large

**Solution**: Scan storage zones separately
```bash
python3 scripts/scan.py /home/chris --label wsl
python3 scripts/scan.py /mnt/c/Users --label windows
# Each gets own scan_id, can be analysed separately
```

## Future Enhancements

- **classify.py**: LLM-assisted classification with iterative dialog
- **Markdown action execution**: Automated execution from classification files
- **WSL auto-compact**: Automated diskpart/optimize-vhd integration
- **Duplicate auto-resolve**: Safe automatic deduplication
- **Scheduled scans**: Cron/Task Scheduler integration
- **Web UI**: Browser-based classification and cleanup

## Requirements

- Python 3.10+
- click
- rich

```bash
pip3 install -r requirements.txt
```

## Project Structure

```
hoardwick/
├── PURPOSE.md              # Project vision
├── README.md               # This file
├── CLAUDE.md               # Development guide
├── specs/                  # LiveSpec specifications
│   ├── mission/            # Outcomes and constraints
│   ├── workspace/          # Development practices
│   ├── strategy/           # Architecture decisions
│   └── behaviors/          # Component specifications
├── scripts/                # Executable utilities
│   ├── scan.py             # Production scanner
│   ├── analyse.py          # Duplicate/stale detection
│   ├── cleanup.py          # Built-in cleanup operations
│   └── *.spec.md          # Script specifications
├── generated/              # SQLite database (gitignored)
│   └── hoardwick.db
├── classifications/        # LLM classifications (future)
└── .livespec/              # LiveSpec framework (gitignored)
```

## License

MIT

## Acknowledgments

Built to replace the over-engineered `pc-disk-analyser` with a focused, production-ready tool that solves real storage management problems.

# Hoardwick Development Guide

Hoardwick uses LiveSpec methodology for development.

## Quick Reference

### Cleanup Operations

See [CLEANUP.md](CLEANUP.md) for comprehensive cleanup recipes and scenarios.

**Emergency space recovery:**
```bash
# Clear UV cache (often 50-200GB)
python3 scripts/cleanup.py uv-cache

# Or use uv directly
uv cache clean
```

**Common cleanup commands:**
```bash
# UV cache management
python3 scripts/cleanup.py uv-cache                # Clear all
python3 scripts/cleanup.py uv-cache --prune-only   # Remove unreachable only
python3 scripts/cleanup.py uv-cache --dry-run      # Preview

# Docker cleanup
python3 scripts/cleanup.py docker-prune            # Basic
python3 scripts/cleanup.py docker-prune --all      # Aggressive

# Package caches
python3 scripts/cleanup.py clear-cache --type all  # All caches
python3 scripts/cleanup.py clear-cache --type npm  # Specific

# Build artifacts
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects
```

### Scanning Storage

```bash
# Fast scan (no hashing) - RECOMMENDED
python3 scripts/scan.py /home/chris

# Scan with duplicate detection (slower, hashes files)
python3 scripts/scan.py /home/chris --hash-files

# Scan multiple locations
python3 scripts/scan.py /home/chris /mnt/c/Users/Chris/Documents

# Scan with exclusions
python3 scripts/scan.py /home/chris --exclude "*.tmp" --exclude "temp"

# Resume interrupted scan
python3 scripts/scan.py /home/chris

# Fresh scan (ignore previous progress)
python3 scripts/scan.py /home/chris --no-resume
```

**Performance expectations:**
- Default (no hashing): 30-60 min for 500k files
- With hashing: 2-6 hours for 500k files

**Note:** By default, scans do NOT compute file hashes (much faster). Use `--hash-files` only when you need duplicate detection.

### Analysing Storage

```bash
# Summary report
python3 scripts/analyse.py

# Find duplicates
python3 scripts/analyse.py --report duplicates

# Find stale files (not accessed in 180 days)
python3 scripts/analyse.py --report stale --stale-days 180

# Export to JSON
python3 scripts/analyse.py --report duplicates --output json > duplicates.json
```

## Common Scan Targets

### WSL Home
```bash
python3 scripts/scan.py /home/chris
```

### Windows User Directories
```bash
python3 scripts/scan.py /mnt/c/Users/Chris/Documents /mnt/c/Users/Chris/Downloads
```

### Screenshots
```bash
python3 scripts/scan.py /mnt/c/Users/Chris/Pictures/Screenshots
```

### Shared Drives
```bash
# Example - adjust paths to your actual mounts
python3 scripts/scan.py /mnt/share
```

## Development

### Project Structure
```
hoardwick/
├── PURPOSE.md              # Why this exists
├── specs/                  # LiveSpec specifications
│   ├── mission/            # Outcomes and constraints
│   ├── workspace/          # How we build
│   ├── strategy/           # Architecture
│   └── behaviors/          # What system does
├── scripts/                # Executable Python scripts
│   ├── scan.py             # Storage scanner
│   ├── scan.spec.md        # Scanner specification
│   ├── analyse.py          # Storage analyser
│   └── analyse.spec.md     # Analyser specification
├── .livespec/              # LiveSpec framework (gitignored)
└── generated/              # Generated outputs (gitignored)
    └── hoardwick.db        # SQLite database
```

### Dependencies
```bash
pip3 install -r requirements.txt
```

### Adding New Features

1. Create spec in `specs/behaviors/`
2. Create script spec in `scripts/`
3. Implement script
4. Test on safe directories first
5. Use dry-run mode to verify behaviour

### Safety Principles

- All scripts read-only by default
- Destructive operations require explicit flags + confirmation
- Always test with `--dry-run` first
- Never follow symlinks during scanning
- Preserve file metadata

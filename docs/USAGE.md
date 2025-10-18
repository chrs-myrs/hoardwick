# Hoardwick Usage Guide

Comprehensive command reference and workflows for storage analysis and cleanup.

## Table of Contents

- [Scanning](#scanning)
- [Analysis](#analysis)
- [Cleanup Operations](#cleanup-operations)
- [Common Workflows](#common-workflows)
- [Database Schema](#database-schema)
- [Troubleshooting](#troubleshooting)

## Scanning

### Basic Scans

```bash
# Scan directory
python3 scripts/scan.py /path/to/scan

# Labeled scan (recommended for multiple roots)
python3 scripts/scan.py /home/chris --label wsl-home

# Scan with file hashing for duplicate detection
python3 scripts/scan.py /home/chris --hash-files

# Multiple roots
python3 scripts/scan.py /home/chris --label wsl-home
python3 scripts/scan.py /mnt/c/Users/Chris --label windows-user
python3 scripts/scan.py /mnt/d --label archive-drive
```

### Resumable Scans

```bash
# Resume interrupted scan (automatic)
python3 scripts/scan.py /home/chris

# Fresh scan (ignore checkpoint)
python3 scripts/scan.py /home/chris --no-resume

# Custom checkpoint frequency
python3 scripts/scan.py /path --checkpoint-every 5000
```

### Scan Options

```bash
# Additional exclusions
python3 scripts/scan.py /path --exclude "*.tmp" --exclude "temp"

# Custom database location
python3 scripts/scan.py /path --database /custom/path/hoardwick.db
```

### Scan Performance

**Expected timing:**
- Default (no hashing): 30-60 min for 500k files
- With hashing: 2-6 hours for 500k files

**Windows filesystem from WSL:**
- Extremely slow (10-100x slower than native tools)
- Use PowerShell for Windows scans when possible
- See [Cleanup Guide](CLEANUP.md) for PowerShell integration

## Analysis

### Summary Reports

```bash
# Overall summary
python3 scripts/analyse.py

# Summary with specific scan
python3 scripts/analyse.py --scan-id 1
```

### Duplicate Detection

```bash
# Find all duplicates
python3 scripts/analyse.py --report duplicates

# Export to JSON
python3 scripts/analyse.py --report duplicates --output json > duplicates.json

# Terminal output (default)
python3 scripts/analyse.py --report duplicates --output terminal
```

### Stale File Identification

```bash
# Find files not accessed in 180 days (default)
python3 scripts/analyse.py --report stale

# Custom threshold
python3 scripts/analyse.py --report stale --stale-days 90   # 90 days
python3 scripts/analyse.py --report stale --stale-days 365  # 1 year
python3 scripts/analyse.py --report stale --stale-days 730  # 2 years
```

## Cleanup Operations

### UV Cache

```bash
# Clear all UV cache
python3 scripts/cleanup.py uv-cache

# Prune unreachable only (safer)
python3 scripts/cleanup.py uv-cache --prune-only

# Preview only
python3 scripts/cleanup.py uv-cache --dry-run

# Or use uv directly
uv cache clean
uv cache prune
```

### Docker Cleanup

```bash
# Remove dangling images/containers
python3 scripts/cleanup.py docker-prune

# Remove all unused images
python3 scripts/cleanup.py docker-prune --all

# Include volumes (destructive)
python3 scripts/cleanup.py docker-prune --volumes

# Aggressive cleanup (all + volumes)
python3 scripts/cleanup.py docker-prune --all --volumes

# Preview only
python3 scripts/cleanup.py docker-prune --dry-run

# Check current usage
docker system df
```

### Package Caches

```bash
# Clear specific cache
python3 scripts/cleanup.py clear-cache --type npm
python3 scripts/cleanup.py clear-cache --type pip
python3 scripts/cleanup.py clear-cache --type cargo
python3 scripts/cleanup.py clear-cache --type go

# Clear all caches
python3 scripts/cleanup.py clear-cache --type all

# Preview
python3 scripts/cleanup.py clear-cache --type all --dry-run
```

### Build Artifacts

```bash
# Clear in project directory
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects

# Custom patterns
python3 scripts/cleanup.py clear-build-artifacts target dist build

# Preview
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects --dry-run
```

## Common Workflows

### Initial System Scan

```bash
# 1. Scan each major storage zone
python3 scripts/scan.py /home/chris --label wsl-home
python3 scripts/scan.py /mnt/c/Users/Chris --label windows-user
python3 scripts/scan.py /mnt/d --label archive-drive

# 2. Analyse for quick wins
python3 scripts/analyse.py --report duplicates
python3 scripts/analyse.py --report stale --stale-days 365

# 3. Execute cleanup based on findings
python3 scripts/cleanup.py clear-cache --type all
python3 scripts/cleanup.py docker-prune
```

### Project Cleanup

```bash
# 1. Scan project directory
python3 scripts/scan.py /home/chris/projects --label dev-projects

# 2. Clear build artifacts
python3 scripts/cleanup.py clear-build-artifacts --root /home/chris/projects

# 3. Clear npm cache (separate from node_modules)
python3 scripts/cleanup.py clear-cache --type npm
```

### Docker Maintenance

```bash
# 1. Check current usage
docker system df

# 2. Safe cleanup (dangling only)
python3 scripts/cleanup.py docker-prune

# 3. If more space needed, aggressive cleanup
python3 scripts/cleanup.py docker-prune --all --volumes
```

### Windows Scan from WSL

```bash
# WARNING: Extremely slow from WSL (10-100x slower)
python3 scripts/scan.py /mnt/c/Users/Chris --label windows

# BETTER: Use native PowerShell from WSL
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "
Get-ChildItem C:\Users\Chris -Recurse -File -Force -ErrorAction SilentlyContinue
"

# See CLEANUP.md for complete PowerShell integration examples
```

## Database Schema

### files table

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT,
    size INTEGER,
    hash TEXT,
    modified REAL,
    accessed REAL,
    parent_dir TEXT,
    depth INTEGER,
    extension TEXT,
    file_type TEXT,
    is_aggregate BOOLEAN,
    aggregate_type TEXT,
    scan_id INTEGER
);
```

**Key fields:**
- `is_aggregate`: True if represents aggregated directory (e.g., node_modules)
- `aggregate_type`: Type ("npm packages", "git objects", etc.)
- `hash`: NULL for large files (>100MB) or aggregated directories
- `scan_id`: Links to specific scan run

### directory_stats table

```sql
CREATE TABLE directory_stats (
    path TEXT,
    file_count INTEGER,
    total_size INTEGER,
    descendant_count INTEGER,
    oldest_access REAL,
    pattern TEXT,
    scan_id INTEGER
);
```

### scans table

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    root_path TEXT,
    label TEXT,
    started REAL,
    completed REAL,
    files_found INTEGER,
    total_size INTEGER,
    status TEXT
);
```

### scan_progress table

```sql
CREATE TABLE scan_progress (
    root_path TEXT PRIMARY KEY,
    last_path TEXT,
    files_scanned INTEGER,
    status TEXT,
    started REAL,
    updated REAL,
    visited_inodes TEXT
);
```

## Aggregate Patterns

**Treated as single database entries:**
- `node_modules/` → "npm packages"
- `.git/objects/` → "git objects"
- `__pycache__/` → "python cache"
- `.next/` → "nextjs cache"
- `target/` → "rust build"
- `dist/` → "build output"
- `.venv/`, `venv/` → "python virtualenv"
- `Cache/`, `cache2/` → "browser cache"

**Skipped entirely:**
- `.Trash`, `$RECYCLE.BIN`
- `System Volume Information`
- `.DS_Store`

**Rationale:** Aggregation reduces database size by ~90% and prevents timeouts on large directory trees.

## Troubleshooting

### Scan Times Out

**Symptoms:** Scan exits after long period without completing

**Solution:** Use labeled scans with checkpoints (default behavior)
```bash
python3 scripts/scan.py /large/path --label big-scan
# If interrupted, just run again - it will resume from checkpoint
```

### Too Many Small Files

**Symptoms:** Scan slow, database grows large with node_modules, .git directories

**Solution:** Aggregate patterns handle this automatically
- `node_modules/` → single database entry
- `.git/objects/` → aggregated
- Build directories → aggregated

No configuration needed - built into scanner.

### Symlink Loops Detected

**Symptoms:** Warning about symlink loops in output

**Solution:** Automatic inode-based detection handles this
- Loops detected and skipped automatically
- Warning printed for visibility
- Scan continues safely
- No action needed

### Database Too Large

**Symptoms:** Database file >500MB, queries slow

**Solution:** Scan storage zones separately
```bash
# Instead of scanning entire C: drive:
python3 scripts/scan.py /mnt/c/Users --label windows-users
python3 scripts/scan.py /mnt/c/Program\ Files --label windows-programs

# Each gets own scan_id, can be analysed separately or together
```

### Database Stale

**Symptoms:** Analysis shows files/directories already cleaned

**Solution:** Rescan after major cleanup operations (>5GB freed)
```bash
# After cleanup, rescan affected areas
python3 scripts/scan.py /home/chris --label wsl-home --no-resume

# Or archive old database and start fresh
mv generated/hoardwick.db generated/hoardwick.db.$(date +%Y-%m-%d)
python3 scripts/scan.py /path --label new-scan
```

**Warning thresholds:**
- >6 hours: Notice in analysis output
- >24 hours: Strong warning
- >7 days: Recommend rescan

### Windows Scan Very Slow

**Symptoms:** Scan from WSL to Windows paths (
/mnt/c/) takes hours, appears stuck

**Solution:** Use native PowerShell for Windows filesystem
- WSL cross-filesystem access is 10-100x slower
- PowerShell native scan: 3 minutes vs 45+ minutes for Python
- See [Cleanup Guide](CLEANUP.md) PowerShell Integration Pattern

### Permission Denied Errors

**Symptoms:** Scanner reports permission errors for certain directories

**Solution:** Either skip or use sudo
```bash
# Let scanner skip (it will warn and continue)
python3 scripts/scan.py /path

# Or use sudo for system directories
sudo python3 scripts/scan.py /var

# For automated sudo with GUI password prompt:
SUDO_ASKPASS=scripts/zenity-askpass.sh sudo -A python3 scripts/scan.py /var
```

## Configuration

### Default Exclusions

Defined in `scripts/scan.py`:
- See `AGGREGATE_PATTERNS` for aggregated directories
- See `SKIP_PATTERNS` for completely excluded paths

### Custom Exclusions

```bash
python3 scripts/scan.py /path --exclude "pattern1" --exclude "pattern2"
```

### Checkpoint Frequency

Default: Every 1000 files

```bash
# Less frequent (faster, but larger gaps if interrupted)
python3 scripts/scan.py /path --checkpoint-every 5000

# More frequent (slower, but smaller gaps if interrupted)
python3 scripts/scan.py /path --checkpoint-every 500
```

### Database Location

Default: `./generated/hoardwick.db`

```bash
python3 scripts/scan.py /path --database /custom/path/db.sqlite
python3 scripts/analyse.py --database /custom/path/db.sqlite
```

## Next Steps

- See [Cleanup Guide](CLEANUP.md) for comprehensive cleanup recipes
- See [Architecture](ARCHITECTURE.md) for specification relationships
- See [CLAUDE.md](../CLAUDE.md) for development guide

---
criticality: CRITICAL
failure_mode: Cannot scan storage without working scanner
governed-by: .livespec/standard/metaspecs/behavior.metaspec.md
satisfies:
  - specs/1-requirements/strategic/outcomes.spec.md
guided-by:
  - specs/2-strategy/architecture.spec.md
---

# Storage Scanner Behavior (Production)

## Requirements

- [!] Scanner recursively walks specified directory trees with resumable checkpoints
  - Checkpoints every N files (default: 1000)
  - Resumes from last checkpoint on interruption
  - Marks scan complete when finished

- [!] Scanner aggregates high-volume directories
  - `node_modules/` → single entry with total size
  - `.git/objects/` → aggregated as "git objects"
  - `__pycache__/`, `.next/`, `target/`, `dist/` → build artifacts
  - `venv/`, `.venv/` → Python virtual environments
  - Browser caches → aggregated cache entries

- [!] Scanner detects and skips symlink loops
  - Tracks visited inodes
  - Skips if inode already seen
  - Warns user of loop detection

- [!] Scanner uses lazy hashing strategy
  - Only hashes files < 100MB (configurable)
  - NULL hash for large files
  - NULL hash for aggregated directories
  - Enables duplicate detection without slowdown

- [!] Scanner stores enhanced metadata
  - Path, size, hash (lazy), modified, accessed
  - Parent directory, depth from root
  - File extension, type (file|aggregate)
  - Aggregation flags and type
  - Scan ID for multi-scan support

- [!] Scanner computes directory statistics
  - File count, total size per directory
  - Descendant count
  - Oldest access time
  - Pattern detection (node_modules, .git, etc.)

- [!] Scanner supports multi-root labeled scans
  - Each scan gets unique ID and label
  - Timestamps: started, completed
  - Status tracking: running, complete, failed
  - Total files found, total size

- [!] Scanner shows progress during operation
  - Files scanned count
  - Aggregates found count
  - Current file/directory
  - Elapsed time

## Inputs

- `paths`: List of root directories to scan
- `--label`: Optional scan label (e.g., "wsl-home", "windows-user")
- `--exclude`: Additional exclusion patterns
- `--no-resume`: Start fresh (ignore checkpoints)
- `--checkpoint-every`: Checkpoint frequency (default: 1000)
- `--database`: Path to SQLite database (default: ./generated/hoardwick.db)

## Outputs

- SQLite database with:
  - files table (all indexed files and aggregates)
  - directory_stats table (pre-computed statistics)
  - scans table (scan metadata)
  - scan_progress table (resumable checkpoints)
- Console output:
  - Files indexed count
  - Aggregated directories count
  - Skipped files count
  - Database path

## Aggregate Patterns

**Treated as single units**:
- `node_modules` → "npm packages"
- `.git/objects` → "git objects"
- `__pycache__` → "python cache"
- `.next` → "nextjs cache"
- `target` → "rust build"
- `dist` → "build output"
- `.venv`, `venv` → "python virtualenv"
- `Cache`, `cache2` → "browser cache"

**Skipped entirely**:
- `.Trash`, `$RECYCLE.BIN`
- `System Volume Information`
- `.DS_Store`

## Database Schema

### files table
```sql
id, path, size, hash, modified, accessed,
parent_dir, depth, extension, file_type,
is_aggregate, aggregate_type, scan_id
```

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

## Performance Characteristics

- Large filesystems: Handles 100GB+ with checkpointing
- Timeout resilient: Resumes automatically
- Memory efficient: Aggregates reduce entry count by ~90%
- Symlink safe: Loop detection prevents infinite traversal
- Hash performance: Lazy strategy avoids hashing large files

## Database Staleness Detection

- [!] Scanner stores scan completion timestamp in scans table
- [!] Analysis tools check database age before reporting
- [!] Warn if database >24 hours old: "Data may be outdated, consider rescanning"
- [!] Show scan age in summary output: "Based on scan from YYYY-MM-DD HH:MM (X hours ago)"
- [!] Multiple scans may have different ages - report per-scan timestamps

**Rationale**: Session 2 showed 43.9 GB UV cache in database, but was already cleaned. Analysis recommended freeing 9.5 GB that didn't exist. Actual cache: 964 MB. Database staleness caused 90% error in recommendations.

## Windows Filesystem Scanning

- [!] For Windows paths (/mnt/c/): Prefer native PowerShell when available
- [!] Use `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command`
- [!] Fallback to WSL filesystem access if PowerShell fails
- [!] Document 10-100x performance improvement in scan output
- [!] PowerShell recursion: `Get-ChildItem -Recurse -File -Force`

**Rationale**: Python scan from WSL: 45 mins, incomplete. PowerShell scan: 3 mins, complete. Cross-filesystem access from WSL is extremely slow.

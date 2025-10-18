---
criticality: IMPORTANT
failure_mode: Unclear technical approach leads to poor implementation
governed-by: .livespec/standard/metaspecs/strategy.metaspec.md
derives-from:
  - specs/1-requirements/strategic/outcomes.spec.md
  - specs/1-requirements/strategic/constraints.spec.md
---

# Hoardwick Production Architecture

## Technical Approach

### Core Philosophy: LLM-First, Resilient, Production-Ready

**Problem Solved**: Previous `pc-disk-analyser` failed due to over-engineering (AI coordinator, event sourcing, complex modes, in-memory only processing).

**Solution**: Focused, resilient architecture with persistent state, LLM-friendly output, and production-grade scanning.

## Core Components

### 1. Resumable Scanner (scan.py)

**Purpose**: Index large filesystems without timeout failures

**Features**:
- Checkpoint-based resumption (every 1000 files)
- Aggregate patterns (node_modules = 1 entry, not 10k files)
- Symlink loop detection (inode tracking)
- Lazy hashing (< 100MB only)
- Multi-root support with labels

**Output**: SQLite database with comprehensive metadata

### 2. Analysis Engine (analyse.py)

**Purpose**: Generate actionable insights from scanned data

**Features**:
- Duplicate detection (by hash, excluding aggregates)
- Stale file identification (by access time)
- Storage summaries with aggregation awareness
- Multiple output formats (terminal, JSON)

**Output**: Human-readable reports

### 3. Cleanup Utilities (cleanup.py)

**Purpose**: Execute common cleanup operations safely

**Built-in Operations**:
- Docker system pruning
- WSL disk compaction (manual instructions)
- Package cache clearing (npm, pip, cargo)
- Build artifact removal
- Markdown action plan execution (future)

**Safety**: All operations require confirmation, support dry-run

### 4. Classification System (classify.py - Future)

**Purpose**: LLM-assisted storage classification

**Planned Features**:
- Iterative LLM dialog for classification
- Query SQLite for detailed data on demand
- Generate markdown hierarchies (classifications/)
- Utility vs storage cost analysis
- File-level action recommendations

## Data Storage Strategy

### SQLite Database

**Why SQLite**:
- Persistent state between runs
- Efficient querying for duplicates
- Supports incremental updates
- No server required
- Transaction support

**Tables**:
- `files`: All indexed files and aggregates
- `directory_stats`: Pre-computed directory metrics
- `scans`: Multi-scan support with labels
- `scan_progress`: Resumable checkpoints

### Markdown Classifications (Future)

**Why Markdown**:
- LLM can read and write markdown naturally
- Human-readable classifications
- Version control friendly
- Easy to edit manually

**Structure**:
```
classifications/
├── wsl-scan.md           # WSL filesystem classification
├── windows-scan.md       # Windows classification
├── duplicates.md         # Duplicate analysis
└── cache-inventory.md    # Known cache locations
```

## Key Architectural Decisions

### 1. Aggregate Patterns Over Full Indexing

**Problem**: `node_modules/` with 50,000 files times out scanner, bloats database

**Solution**: Treat as single aggregated entry
- Database: 1 row with total size
- Avoids timeout on traversal
- Reduces database size by ~90%

**Trade-off**: Can't query individual files within aggregate
**Mitigation**: Re-scan specific aggregates if detailed analysis needed

### 2. Lazy Hashing Strategy

**Problem**: Hashing all files is slow, especially large media

**Solution**: Only hash files < 100MB
- Duplicate detection still effective (most duplicates are smaller files)
- Large files identifiable by size + path patterns
- Huge performance improvement

**Trade-off**: Won't detect duplicates of large unique files
**Mitigation**: Acceptable for use case (large files are usually media, already organized)

### 3. Checkpoint-Based Resumption

**Problem**: Large filesystem scans timeout (observed: /mnt/c/ timed out)

**Solution**: Save checkpoint every N files
- Resume from last position on restart
- Track visited inodes for loop detection
- Mark scan complete when finished

**Trade-off**: Slightly slower due to checkpoint writes
**Mitigation**: Configurable frequency, default 1000 is good balance

### 4. Multi-Root Labeled Scans

**Problem**: Different storage zones need different analysis
- WSL: Development focus (node_modules, build artifacts)
- Windows: Cache focus (AppData, browser caches)
- D: drive: Archive/media focus (duplicates, organization)

**Solution**: Separate scans with labels
```bash
scan.py /home/chris --label wsl-home
scan.py /mnt/c/Users/Chris --label windows-user
scan.py /mnt/d --label archive-drive
```

Each scan gets own ID, can be analysed separately or together

### 5. Symlink Loop Detection

**Problem**: Windows has symlink loops (Application Data → AppData/Local)

**Solution**: Track visited inodes
- Skip if inode already seen
- Warn user of loop
- Continue scan safely

**Trade-off**: Requires inode support (not available on all filesystems)
**Mitigation**: Fallback to path-based detection if inodes unavailable

## Performance Characteristics

### Scan Performance

**WSL home (108GB, 93 projects)**:
- Traditional scan: Timeout after 2 minutes
- Aggregated scan: ~5-10 minutes with checkpoints
- Database size: ~50MB (vs ~500MB without aggregation)

**Windows C: drive**:
- Traditional scan: Timeout (symlink loops + AppData)
- Aggregated scan with max-depth: ~15-20 minutes
- Handles loops safely

### Analysis Performance

**Duplicate detection**: < 1 second (indexed hashes)
**Stale file query**: < 2 seconds (indexed access times)
**Summary generation**: < 3 seconds (pre-computed directory stats)

## Technology Stack

**Core**:
- Python 3.10+ (pathlib, sqlite3, os.walk)
- SQLite (local database)
- Click (CLI framework)
- Rich (terminal formatting)

**Future**:
- LLM integration (OpenAI/Anthropic API or local)
- Markdown parsing for classifications

## Safety Architecture

- Read-only scanning by default
- All destructive operations require confirmation
- Dry-run support for all cleanup operations
- Operation logging
- Checkpoint recovery for interrupted scans
- Loop detection prevents infinite traversal

## Scalability

**Tested**:
- 100GB+ filesystems
- 1M+ files (aggregated)
- Multiple terabytes across drives

**Limits**:
- SQLite database: Practical limit ~10M rows
- Checkpoint file: Visit 1000 inodes (pruned older)
- Memory: Minimal (streaming file iteration)

## Future Enhancements

1. **classify.py**: LLM-assisted classification
2. **Automated cleanup**: Execute markdown action plans
3. **WSL auto-compact**: PowerShell integration
4. **Web UI**: Browser-based analysis and classification
5. **Scheduled scans**: Cron/Task Scheduler integration
6. **Change detection**: Compare scans over time

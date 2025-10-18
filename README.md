# Hoardwick

**Storage analysis and cleanup system for cross-platform filesystems**

Scan WSL, Windows, and network drives to identify duplicates, stale files, and cleanup opportunities. Built for large filesystems with resumable scans, aggregate patterns, and LLM-friendly output.

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Scan your storage
python3 scripts/scan.py /home/chris --label wsl-home
python3 scripts/scan.py /mnt/c/Users/Chris --label windows-user

# Analyse for quick wins
python3 scripts/analyse.py --report duplicates
python3 scripts/analyse.py --report stale --stale-days 365

# Execute cleanup
python3 scripts/cleanup.py docker-prune
python3 scripts/cleanup.py clear-cache --type npm
```

## Key Features

- **Resumable scanning** - Checkpoint-based scans handle timeouts on large filesystems
- **Aggregate patterns** - Treats `node_modules`, `.git`, caches as single units for performance
- **Multi-root support** - Scan WSL, Windows, network drives separately with labels
- **Duplicate detection** - Find identical files across all scanned locations
- **Stale file identification** - Track last access times, find archival candidates
- **Built-in cleanup** - Docker pruning, cache clearing, build artifact removal

## Documentation

- **[Usage Guide](docs/USAGE.md)** - Commands, workflows, and examples
- **[Cleanup Guide](docs/CLEANUP.md)** - Comprehensive cleanup recipes and safety protocols
- **[Architecture](docs/ARCHITECTURE.md)** - Specification relationships and system design
- **[Development Guide](CLAUDE.md)** - For contributors and Claude Code development

## Common Operations

**Emergency space recovery:**
```bash
python3 scripts/cleanup.py uv-cache           # Clear UV cache (often 50-200GB)
python3 scripts/cleanup.py docker-prune --all # Remove all unused Docker data
```

**Scanning large drives:**
```bash
# Windows paths are slow from WSL - use native PowerShell when possible
python3 scripts/scan.py /mnt/c/Users/Chris --label windows

# Scans checkpoint every 1000 files - safe to interrupt and resume
python3 scripts/scan.py /large/path --label big-scan
```

**Finding duplicates:**
```bash
python3 scripts/analyse.py --report duplicates
python3 scripts/analyse.py --report duplicates --output json > duplicates.json
```

## Architecture

**Storage:** SQLite database (`generated/hoardwick.db`)
- `files` - Indexed files with metadata, hashes, aggregation flags
- `directory_stats` - Pre-computed directory metrics
- `scans` - Multi-root scan tracking with timestamps
- `scan_progress` - Resumable checkpoints

**Aggregate Patterns** (treated as single database entries):
- `node_modules/` - npm packages
- `.git/objects/` - git objects
- `__pycache__/`, `.next/`, `dist/`, `target/` - build outputs
- `venv/`, `.venv/` - Python virtual environments
- `Cache/`, `cache2/` - browser caches

**Performance:**
- Checkpoints every 1000 files (configurable)
- Symlink loop detection via inode tracking
- Lazy hashing (only files < 100MB)
- Aggregation reduces database size by ~90%

## Requirements

- Python 3.10+
- click, rich

```bash
pip3 install -r requirements.txt
```

## Project Structure

```
hoardwick/
├── scripts/           # Executable utilities
│   ├── scan.py        # Storage scanner
│   ├── analyse.py     # Duplicate/stale detection
│   └── cleanup.py     # Cleanup operations
├── specs/             # LiveSpec specifications
├── docs/              # Documentation
├── generated/         # SQLite database (gitignored)
└── .livespec/         # LiveSpec framework
```

## License

MIT

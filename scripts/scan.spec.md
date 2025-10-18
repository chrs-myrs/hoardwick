---
criticality: CRITICAL
failure_mode: Cannot scan storage
governed-by: .livespec/standard/metaspecs/behavior.metaspec.md
implements: ../specs/behaviors/scanner.spec.md
---

# Storage Scanner Script

## Purpose

CLI tool to scan storage locations and build file metadata database.

## Usage

```bash
python3 scripts/scan.py <paths...> [options]
```

## Options

- `--database PATH`: Database file location (default: `./generated/hoardwick.db`)
- `--label TEXT`: Label for this scan (for tracking multiple scans)
- `--exclude PATTERN`: Add exclusion pattern (can be repeated)
- `--no-resume`: Start fresh, ignore previous checkpoints
- `--checkpoint-every N`: Checkpoint frequency in files (default: 1000)
- `--hash-files`: Compute file hashes during scan (slower, for duplicate detection)

## Examples

```bash
# Fast scan (no hashing)
python3 scripts/scan.py /home/chris

# Scan with hashing (for duplicate detection)
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

## Performance

**Default mode (no --hash-files):**
- ~500-1000 files/second
- Expected: 30-60 minutes for 500k files

**With --hash-files:**
- ~50-100 files/second (10x slower)
- Expected: 2-6 hours for 500k files
- Only use when duplicate detection needed

## Aggregate Detection

Large directories are automatically detected and aggregated (counted as single units):

- `.cache/` - All cache directories
- `.cargo/registry/` - Rust package cache
- `.npm/` - NPM cache
- `node_modules/` - NPM packages
- `.git/objects/` - Git objects
- `__pycache__/` - Python cache
- `.venv/`, `venv/` - Python virtual environments
- `target/`, `dist/`, `build/` - Build outputs

## Scan Areas

Scanner automatically discovers logical scan areas and tracks them separately:

- High priority: projects/, documents/, downloads/
- Normal priority: config/, application data
- Low priority: caches, build artifacts

Areas are shown before scanning begins and tracked in database for future use.

## Output

- Progress indicator during scan
- Summary report on completion
- Database file with indexed metadata

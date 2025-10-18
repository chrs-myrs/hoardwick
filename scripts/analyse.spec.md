---
criticality: CRITICAL
failure_mode: Cannot identify duplicates or waste
governed-by: .livespec/standard/metaspecs/behavior.metaspec.md
---

# Storage Analyser Script

## Purpose

Analyses scanned storage to identify duplicates, stale files, and storage waste.

## Usage

```bash
python3 scripts/analyse.py [options]
```

## Options

- `--database PATH`: Database file location (default: `./generated/hoardwick.db`)
- `--report TYPE`: Report type (duplicates, stale, summary) (default: summary)
- `--output FORMAT`: Output format (terminal, json, csv) (default: terminal)
- `--stale-days N`: Files not accessed in N days considered stale (default: 365)

## Examples

```bash
# Show summary report
python3 scripts/analyse.py

# Find duplicates
python3 scripts/analyse.py --report duplicates

# Find stale files (not accessed in 180 days)
python3 scripts/analyse.py --report stale --stale-days 180

# Export to JSON
python3 scripts/analyse.py --report duplicates --output json > duplicates.json
```

## Output

- Human-readable terminal output by default
- Structured JSON/CSV for processing
- Statistics and recommendations

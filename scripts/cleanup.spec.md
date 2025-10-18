---
criticality: IMPORTANT
failure_mode: Cannot execute common cleanup tasks
governed-by: ../specs/workspace/constitution.spec.md
---

# Cleanup Utility Specification

## Purpose

Provides built-in cleanup operations for common storage management tasks.

## Commands

### uv-cache
```bash
python3 scripts/cleanup.py uv-cache [OPTIONS]
```

**Options**:
- `--prune-only`: Remove only unreachable packages (preserves active dependencies)
- `--dry-run`: Preview without executing

**Behaviour**:
- Shows UV cache location and size
- In clean mode (default): Removes ALL cached packages
- In prune mode: Removes only unreachable/unused packages
- Displays statistics on removal
- Requires confirmation unless dry-run
- Handles large caches gracefully (timeout on size check)

**Use Cases**:
- Emergency space recovery: Use without `--prune-only` (clears everything)
- Routine maintenance: Use with `--prune-only` (keeps active versions)
- Space analysis: Use `--dry-run` to see what would be removed

### docker-prune
```bash
python3 scripts/cleanup.py docker-prune [OPTIONS]
```

**Options**:
- `--dry-run`: Preview without executing
- `--all`: Remove all unused images (not just dangling)
- `--volumes`: Also prune unused volumes

**Behaviour**:
- Shows current Docker disk usage
- Prunes system with selected options
- Shows updated disk usage
- Requires confirmation unless dry-run

### wsl-compact
```bash
python3 scripts/cleanup.py wsl-compact [OPTIONS]
```

**Options**:
- `--dry-run`: Preview without executing

**Behaviour**:
- Checks WSL environment
- Provides manual instructions for disk compaction
- Warns about WSL shutdown requirement
- Requires confirmation

### clear-cache
```bash
python3 scripts/cleanup.py clear-cache --type TYPE [OPTIONS]
```

**Options**:
- `--type`: Cache type (npm|pip|cargo|all)
- `--dry-run`: Preview without executing

**Behaviour**:
- Clears specified package manager caches
- npm: Uses `npm cache clean --force`
- pip: Uses `pip3 cache purge`
- cargo: Removes ~/.cargo/registry
- Requires confirmation per cache

### clear-build-artifacts
```bash
python3 scripts/cleanup.py clear-build-artifacts [PATTERNS] [OPTIONS]
```

**Options**:
- `--root PATH`: Root directory to search
- `--dry-run`: Preview without executing

**Default patterns**: target, dist, build, .next, out

**Behaviour**:
- Searches for build directories
- Verifies parent has project marker (package.json, Cargo.toml, etc.)
- Lists found directories
- Deletes with confirmation

### execute-plan
```bash
python3 scripts/cleanup.py execute-plan FILE [OPTIONS]
```

**Options**:
- `--section NAME`: Only process specific section
- `--dry-run`: Preview without executing

**Behaviour**:
- Parses markdown file for actions
- Extracts lines starting with "- Action:" or "Action:"
- Displays table of actions
- Currently manual execution (automated in future)

## Safety Features

- All destructive operations require confirmation
- Dry-run mode for all commands
- Clear output showing what will be affected
- Error handling with user-friendly messages

## Return Codes

- 0: Success
- 1: Command failed or user cancelled

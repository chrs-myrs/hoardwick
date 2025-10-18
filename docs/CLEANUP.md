# Cleanup Recipes

Quick reference for storage cleanup operations organised by urgency, safety, and common scenarios.

## Quick Command Reference

| Command | Space Saved | Safety | Re-downloads? |
|---------|-------------|--------|---------------|
| `uv cache clean` | 50-200GB | Safe | Yes |
| `uv cache prune` | Moderate | Safe | Only unused |
| `cleanup.py docker-prune --all --volumes` | 10-50GB | Review volumes | Images yes, volumes check |
| `cleanup.py clear-cache --type all` | 1-10GB | Safe | Yes |
| `cleanup.py clear-build-artifacts` | Varies | Safe | On rebuild |

## By Urgency

### Emergency Space Recovery

When you need immediate storage relief:

```bash
# 1. Clear UV cache completely (largest impact)
uv cache clean

# 2. Docker full cleanup
python3 scripts/cleanup.py docker-prune --all --volumes

# 3. Clear all package caches
python3 scripts/cleanup.py clear-cache --type all

# 4. Remove build artifacts across home
python3 scripts/cleanup.py clear-build-artifacts --root /home/chris
```

**Expected Recovery:** 50-250GB depending on your development activity

**Trade-off:** Next project will re-download dependencies (5-30 min initial delay)

### Routine Maintenance

Weekly/monthly cleanup that preserves frequently used items:

```bash
# 1. Prune unreachable UV cache only
uv cache prune

# 2. Basic Docker cleanup (dangling only)
python3 scripts/cleanup.py docker-prune

# 3. Clear build artifacts in projects directory
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects
```

**Expected Recovery:** 5-20GB

**Trade-off:** Minimal impact, only removes truly unused items

### Targeted Cleanup

When you know what's causing issues:

```bash
# Clear specific package manager
python3 scripts/cleanup.py clear-cache --type npm
python3 scripts/cleanup.py clear-cache --type pip

# Clear specific build patterns
python3 scripts/cleanup.py clear-build-artifacts target node_modules

# Preview before acting
uv cache clean --dry-run
python3 scripts/cleanup.py docker-prune --dry-run
```

## By Safety Level

### Safe (Re-downloadable)

These operations remove only content that can be restored automatically:

| Operation | Command | What Gets Removed |
|-----------|---------|-------------------|
| **UV cache** | `uv cache clean` | All Python package archives |
| **UV prune** | `uv cache prune` | Unreachable package versions |
| **Package caches** | `cleanup.py clear-cache` | npm/pip/cargo cached downloads |
| **Docker images** | `cleanup.py docker-prune --all` | Unused container images |
| **Build artifacts** | `cleanup.py clear-build-artifacts` | target/, dist/, build/, .next/ etc. |

**Recommendation:** Run these freely with `--dry-run` first to verify

### Review First (May Contain Data)

Operations that might affect important content:

| Operation | Command | Check First |
|-----------|---------|-------------|
| **Docker volumes** | `cleanup.py docker-prune --volumes` | `docker volume ls` - databases? |
| **Cargo registry** | `cleanup.py clear-cache --type cargo` | Active Rust projects? |
| **Temp directories** | Manual | Review `.tmp*/` contents |

**Recommendation:** Always review what will be removed, especially volumes

### Never Automate (Destructive)

Operations that require manual review:

- File deletion based on age/duplicates (use Hoardwick analysis first)
- WSL disk compaction (requires Windows admin + shutdown)
- System-wide temp directory cleanup (may break running apps)
- Removing `.git` directories or version control data

## Common Scenarios

### "I need 50GB right now"

Emergency space recovery with minimal impact:

```bash
# Check current space
df -h

# Clear UV cache (usually biggest win)
uv cache clean

# Verify recovery
df -h

# If more needed, continue with Docker
python3 scripts/cleanup.py docker-prune --all
```

**Time:** 2-5 minutes
**Recovery:** 50-200GB typically
**Impact:** Next Python project setup slower (one-time)

### "Weekly maintenance routine"

Safe ongoing cleanup:

```bash
# Prune unreachable caches
uv cache prune

# Basic Docker cleanup
python3 scripts/cleanup.py docker-prune

# Clear package manager caches
python3 scripts/cleanup.py clear-cache --type all
```

**Frequency:** Weekly or when disk >80% full
**Time:** 1-2 minutes
**Recovery:** 5-20GB
**Impact:** Minimal

### "Preparing for fresh project start"

Clean slate before major work:

```bash
# Clear build artifacts in project directories
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects

# Clear caches to force fresh downloads
python3 scripts/cleanup.py clear-cache --type all

# Keep UV cache but prune unreachable
uv cache prune
```

### "Post-Hoardwick scan cleanup"

After scanning and identifying issues:

```bash
# Run scan
python3 scripts/scan.py /home/chris

# Analyse for duplicates
python3 scripts/analyse.py --report duplicates

# Review duplicates, then target specific areas
# (Manual review required before deletion)

# Clear safe caches after cleaning files
uv cache prune
python3 scripts/cleanup.py clear-cache --type all
```

## UV Cache Details

UV maintains a cache of Python packages that can grow very large with multiple virtual environments.

### Commands

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `uv cache clean` | Removes ALL cached packages | Emergency space, or after major cleanup |
| `uv cache prune` | Removes only unreachable packages | Routine maintenance, keeps active versions |
| `uv cache dir` | Shows cache location | Finding the cache |

### Understanding the Impact

**After `uv cache clean`:**
- ✓ Immediate space recovery (often 50-200GB)
- ✓ Cache rebuilds automatically on next use
- ⚠ First `uv` command in each project will be slower (downloads packages)
- ⚠ Requires internet connection for next project setup

**After `uv cache prune`:**
- ✓ Removes unused versions only
- ✓ Active projects unaffected
- ✓ Minimal impact on workflow

### When UV Cache Grows

The cache grows when:
- Creating many virtual environments
- Testing multiple Python versions
- Installing large packages (PyTorch, TensorFlow, etc.)
- Working across many projects

Signs you should clean UV cache:
- `/home/chris/.cache/uv/` is >50GB
- Disk space critically low
- Haven't cleaned in >6 months

## Package Manager Caches

### npm

```bash
# Check cache size
du -sh ~/.npm

# Clear completely
python3 scripts/cleanup.py clear-cache --type npm
# Or directly: npm cache clean --force
```

Impact: Next `npm install` downloads packages fresh

### pip

```bash
# Check cache size
du -sh ~/.cache/pip

# Clear completely
python3 scripts/cleanup.py clear-cache --type pip
# Or directly: pip3 cache purge
```

Impact: Next `pip install` downloads packages fresh

### cargo (Rust)

```bash
# Check cache size
du -sh ~/.cargo/registry

# Clear via cleanup script (with confirmation)
python3 scripts/cleanup.py clear-cache --type cargo
```

Impact: Next Rust build downloads crates fresh

## Docker Cleanup

### Levels

```bash
# Basic: Remove stopped containers and dangling images
python3 scripts/cleanup.py docker-prune

# Aggressive: Remove ALL unused images
python3 scripts/cleanup.py docker-prune --all

# Complete: Include unused volumes (review first!)
python3 scripts/cleanup.py docker-prune --all --volumes
```

### Before Removing Volumes

```bash
# List volumes
docker volume ls

# Inspect specific volume
docker volume inspect VOLUME_NAME

# Check what's using it
docker ps -a --filter volume=VOLUME_NAME
```

Volumes may contain:
- Database data (PostgreSQL, MySQL)
- Application state
- Uploaded files

**Never remove volumes without verification**

## Build Artifacts

Common build directories that can be safely removed:

| Pattern | Language/Tool | Regenerated By |
|---------|---------------|----------------|
| `target/` | Rust (Cargo) | `cargo build` |
| `dist/` | Python, Node | `npm run build`, `python setup.py` |
| `build/` | Various | Project-specific build command |
| `.next/` | Next.js | `npm run dev` or `npm run build` |
| `out/` | Various | Build tools |
| `node_modules/` | Node.js | `npm install` (not included by default) |

### Finding Build Artifacts

```bash
# Preview what would be found
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects --dry-run

# Clean specific patterns
python3 scripts/cleanup.py clear-build-artifacts target dist --root ~/projects

# Clean everything in a directory
python3 scripts/cleanup.py clear-build-artifacts --root ~/projects
```

## Best Practices

1. **Always dry-run first** for unfamiliar operations
2. **Check disk space before and after** to verify impact
3. **Read confirmation prompts carefully** - they contain important context
4. **Emergency order:** UV cache > Docker > Package managers > Build artifacts
5. **Never automate destructive operations** without review
6. **Document custom cleanup needs** in this file for future reference

## Monitoring Space

```bash
# Overall disk usage
df -h

# Specific directory size (quick)
du -sh /path/to/directory

# Largest directories (careful, can be slow)
du -h /home/chris | sort -rh | head -20

# Using Hoardwick scan data
python3 scripts/analyse.py
```

## Future Enhancements

Planned improvements:

- Natural language commands ("clear caches safely")
- Scheduled cleanup automation
- Integration with Hoardwick duplicate detection
- Pre-defined cleanup recipes by role (data science, web dev, etc.)
- Safe file deletion based on Hoardwick analysis

---
criticality: USEFUL
failure_mode: Users don't understand VHDX overhead and waste time trying to compact beyond filesystem limits
governed-by: .livespec/standard/metaspecs/behavior.spec.md
guided-by: specs/2-strategy/architecture.spec.md
constrained-by: specs/workspace/workflows.spec.md
---

# VHDX Management Behavior

## Requirements

### VHDX Size Understanding

**Filesystem Overhead:**
- ext4 filesystem reserves 5-10% for metadata, journals, reserved blocks
- VHDX sparse files add 10-25% overhead for block alignment and metadata
- Total expected overhead: 20-35% over actual data usage
- Example: 85 GB data → 100-115 GB VHDX file is normal

**Multiple VHDX Detection:**
- Users may have multiple VHDXs: Ubuntu, Docker Desktop, other distros
- Each VHDX contributes to Windows C: drive usage
- Check all VHDXs when investigating Windows disk space issues

### Compaction Process

**Pre-Compaction Verification:**
- Check actual VHDX file size on Windows (not WSL df output)
- Verify VHDX location: `$env:LOCALAPPDATA\Packages\Canonical*\LocalState\ext4.vhdx`
- Calculate expected size: (WSL usage) × 1.25 = minimum VHDX size

**Compaction Steps:**
- Zero free space in WSL to mark empty blocks
- Shutdown WSL completely before compaction
- Use diskpart or optimize-vhd from Windows
- Do not start WSL or scans immediately after

**Post-Compaction Reality:**
- 4-10 GB recovery typical for 30-40 GB of deleted files
- Remaining gap (20-35%) is normal filesystem overhead
- Additional compaction attempts unlikely to free more space

### Cross-Platform Awareness

**Where Space Actually Is:**
- WSL internal usage (df): Shows data inside virtual disk
- VHDX file size: Space consumed on Windows C: drive
- Windows C: drive: Overall system capacity (real problem if >90%)

**Priority of Issues:**
- Windows C: >90% full: Critical (address first)
- VHDX >30% overhead: Normal (accept as filesystem limit)
- WSL >80% full: Moderate (clean internal caches)

## Non-Requirements

- System does not automatically compact VHDXs
- System does not warn about VHDX overhead
- Compaction is manual Windows operation (no automation from WSL)

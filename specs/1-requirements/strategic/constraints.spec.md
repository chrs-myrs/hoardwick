---
criticality: CRITICAL
failure_mode: System violates constraints causing data loss or corruption
governed-by: .livespec/standard/metaspecs/constraints.metaspec.md
---

# Hoardwick Constraints

## Requirements

- [!] System NEVER modifies files without explicit user confirmation
- [!] System operates read-only by default
- [!] System preserves file metadata (timestamps, permissions)
- [!] System handles cross-platform path differences (WSL vs Windows)
- [!] System respects .gitignore and hidden file conventions
- [!] System works offline (no cloud dependencies)

## Technical Constraints

- Python 3.8+ (available in WSL environment)
- Cross-platform path handling (pathlib)
- Must handle large directory trees (100k+ files)
- Must handle various filesystems (ext4, NTFS, network drives)

## Safety Constraints

- All destructive operations require explicit confirmation
- Maintain operation logs for audit trail
- Support rollback where possible
- Never follow symlinks during scanning (prevent loops)

---
criticality: IMPORTANT
failure_mode: Inconsistent development practices
governed-by: .livespec/standard/metaspecs/constitution.metaspec.md
---

# Hoardwick Development Constitution

## Core Principles

- Minimal specifications - only what's essential
- Evolve existing code - never duplicate files
- Safety first - read-only by default
- Preview before action - no surprises
- Cross-platform from start - WSL and Windows

## Development Practices

- Python scripts in `scripts/` directory
- Each script has matching `.spec.md` file
- Generated content in `generated/` (gitignored)
- Working files in `.tmp/` and `.scratch/` (gitignored)
- British English for documentation
- Use `python3` and `pip3` explicitly

## Code Standards

- Type hints for function signatures
- Docstrings for public functions
- Click for CLI interfaces
- Pathlib for path handling
- Rich for terminal output formatting

## Testing Approach

- Manual testing on real storage initially
- Test on safe directories first
- Validate cross-platform path handling
- Verify dry-run mode works correctly

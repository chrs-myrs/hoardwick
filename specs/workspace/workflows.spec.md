---
criticality: IMPORTANT
failure_mode: Without clear workflows, development becomes inconsistent and skips critical steps
---

# Hoardwick Development Workflows

## Requirements

**Feature Development:**
1. Specification first: Create `.spec.md` before implementation
   - Check specs/workspace/ for patterns and workflows before starting
   - Verify no similar spec exists to extend
2. Implementation: Follow spec, use type hints, rich output
3. Testing: Manual validation on safe directories
4. Documentation: Update CLEANUP.md or CLAUDE.md if user-facing

**Bug Fix Workflow:**
1. Reproduce issue on real data
2. Document expected vs actual behavior
3. Fix implementation
4. Verify fix resolves issue
5. Update spec if behavior changed

**Script Development Workflow:**
1. Create `scripts/name.spec.md` defining observable behavior
2. Implement `scripts/name.py` following patterns.spec.md
3. Test with `--dry-run` first
4. Test on safe directory
5. Document in CLEANUP.md if it's a cleanup operation

**Cleanup Operation Workflow:**
1. Research what will be removed
2. Implement with `--dry-run` mode
3. Add confirmation prompt if irreversible
4. Test dry-run shows accurate preview
5. Document in CLEANUP.md with safety level

**VHDX Compaction Workflow:**
1. Check actual VHDX file size on Windows (not just WSL `df` output)
2. Calculate expected overhead: ext4 uses 5-10%, VHDX sparse files add 10-25% more
3. Zero free space in WSL: `dd if=/dev/zero of=/tmp/zeros.img; rm /tmp/zeros.img`
4. Shutdown WSL: `wsl --shutdown` from Windows
5. Compact from Windows PowerShell: `diskpart → select vdisk → compact vdisk`
6. **Critical**: Do not start WSL or scans immediately after compaction
7. Accept 20-35% total overhead as filesystem limit (may not be reclaimable)

**Active Tool Cleanup Protocol:**
- For tools actively in use (VS Code, IDEs, databases): Only remove caches/logs/temp files
- Never remove: Binaries, extensions, configuration, user data
- Verify tool functionality after cleanup
- Document which directories are safe to clean vs must preserve

**Critical Data Safety Protocol:**
- Crypto wallets, credentials, irreversible data: Explicit backup before removal
- Backup verification: SHA256 checksum before and after copy
- Document backup location in cleanup record
- Only proceed with removal after verified backup exists

**Platform-Specific Cleanup:**
- Use tool-native cleanup commands: `go clean -modcache`, `uv cache clean`, `npm cache clean`
- Avoid manual `rm -rf` for tool-managed directories (permission issues, state corruption)
- Test tool-specific command exists before using
- Document correct cleanup method for each tool in CLEANUP.md

**Preference Learning Workflow:**
1. After cleanup decisions, run `python3 scripts/preferences.py show`
2. Review if preferences.json accurately reflects decisions
3. Update known_active_projects if new patterns emerge
4. Classify projects periodically with `preferences.py classify`
5. User preferences override age-based rules (project age ≠ uselessness)
6. Document exceptions in preferences.json known_active_projects

**Scan Data Lifecycle Workflow:**
1. After major cleanups (>5 GB freed): Consider scan data stale
2. Before analysis: Check scan timestamps, warn if >24 hours old
3. Database backup before continuing scans: `cp hoardwick.db hoardwick.db.backup`
4. After cleanup: Either rescan affected directories OR mark database as stale
5. Archive old databases by date: `mv hoardwick.db hoardwick.db.YYYY-MM-DD`
6. Incremental rescans: Rescan specific directories after targeted cleanup

**Rationale**: Session 2 analyzed yesterday's scan showing 43.9 GB UV cache. Reality: already cleaned, only 964 MB remained. Recommendations were 90% wrong due to stale data.

**Automated Cleanup with Sudo:**
1. Use zenity wrapper for password prompts: `scripts/zenity-askpass.sh`
2. Set environment: `SUDO_ASKPASS=scripts/zenity-askpass.sh sudo -A command`
3. Zenity wrapper content: `#!/bin/bash\nzenity --password --title="sudo password required"`
4. Make wrapper executable: `chmod +x scripts/zenity-askpass.sh`
5. Enables automated cleanup operations requiring elevated privileges

**User Communication Requirements:**
- Long-running operations (>1 min): Show periodic progress updates
- Background scans: Provide status check instructions
- When investigating issues: Explain what's happening, don't go silent
- Scans >5 mins: Show "Still working on..." messages
- When blocked: Communicate the blockage, don't disappear

**Rationale**: User asked "Hello?" when assistant got lost in diagnostics. User asked "How are the scans going?" after 45 mins silence. Need proactive communication.

**Spec-Code Sync:**
- When requirements change: Update spec first, then code
- When implementation reveals new requirements: Update spec immediately
- When new pattern emerges: Consider adding to patterns.spec.md
- When safety issue discovered: Document in workflows.spec.md or constitution.spec.md

**Commit Workflow:**
- Atomic commits: One logical change per commit
- Descriptive messages: What and why (not how)
- Evolve files: Never create duplicate versions (_v2, _old)
- Git history: Single source of truth (not filenames)

**Validation:**
  - New features have specs before implementation
  - Scripts have matching .spec.md files
  - Destructive operations have dry-run + confirmation
  - Cleanup operations documented in CLEANUP.md
  - Preference learnings captured after significant cleanup sessions

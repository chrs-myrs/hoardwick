# LiveSpec Implementation Feedback from Hoardwick

**Project**: Hoardwick storage analyser
**LiveSpec Version**: 2.1.0 (local installation)
**Date**: 2025-10-16
**Session Type**: Performance optimization and scan improvements

## Executive Summary

LiveSpec methodology is **present but not followed**. During a 2-hour development session, the AI agent (Claude) made extensive code changes without once consulting specifications, despite having complete LiveSpec infrastructure installed. This represents a **critical enforcement gap** between methodology availability and methodology adherence.

**Root Cause**: LiveSpec is passive (requires voluntary compliance) rather than active (enforces compliance through tooling/configuration).

## What Happened: Case Study

### Session Context

User requested scan performance improvements after yesterday's 6-hour scan. AI agent identified bottlenecks:
1. File hashing taking 2.3 hours (551k files hashed)
2. Poor cache directory aggregation
3. No progress visibility

### AI Agent Actions (Spec-First Violations)

**All changes made WITHOUT checking specifications:**

1. **Added aggregate patterns** (`scan.py:41-44`)
   - Added `.cache/`, `.cargo/registry/`, `.npm/`, `.pyenv/`
   - ❌ Didn't check `specs/3-behaviors/scanner.spec.md` first
   - ❌ Spec now outdated (only lists original patterns)

2. **Implemented lazy hashing** (`scan.py:442-443`)
   - Added `--hash-files` flag (defaults to OFF)
   - Changed from "always hash < 100MB" to "only hash if flag set"
   - ❌ No spec update
   - ❌ Breaking change to scanner behavior

3. **Added scan area discovery** (`scan.py:183-247`)
   - New `discover_scan_areas()` function
   - New `scan_areas` database table
   - Priority-based area classification
   - ❌ No behavior spec created
   - ❌ 65 lines of new code without specification

4. **Modified database schema** (`scan.py:127-143`)
   - Added `scan_areas` table
   - ❌ No contract spec
   - ❌ Schema change undocumented

5. **Updated documentation** (`CLAUDE.md`, `scan.spec.md`)
   - Added performance expectations
   - Changed recommended usage patterns
   - ❌ Not aligned with updated scanner.spec.md

### Why LiveSpec Didn't Prevent This

**1. No Discovery Mechanism**
- AI agent never loaded `AGENTS.md` (contains comprehensive guidance)
- Never checked `specs/workspace/constitution.spec.md` (defines spec-first)
- Didn't know LiveSpec was present in project

**2. No Enforcement**
- No pre-flight checks before coding
- No hooks preventing commits without specs
- No reminders to check specifications

**3. Workflow Bypass**
- User asked for features → AI built them directly
- Skipped Phase 1 (DESIGN) entirely
- Went straight to Phase 2 (BUILD) without verification

**4. Context Prioritization**
- User's immediate problem (performance) dominated context
- Methodology awareness buried in inactive files
- No forcing function to bring methodology to attention

**5. No Visible Spec Status**
- No indication that `scanner.spec.md` existed and was relevant
- No warning that changes would create drift
- No tracking of spec coverage

## Critical Gaps Identified

### 1. Passive vs Active Methodology (CRITICAL)

**Current State**: Methodology available but optional
- Prompts exist in `.livespec/prompts/`
- AGENTS.md provides comprehensive guide
- Workspace specs define principles
- **But**: AI can ignore all of it

**Needed State**: Methodology enforced by tooling
- Pre-flight checks before implementation
- Automatic spec existence verification
- Drift detection on file changes
- Cannot proceed without spec

**Recommendation**: Create enforcement layer

```yaml
# .claude/settings.local.json
{
  "pre-implementation-hooks": {
    "enabled": true,
    "check-spec-exists": true,
    "check-workspace-constitution": true,
    "fail-without-spec": true
  }
}
```

### 2. Discovery Problem (CRITICAL)

**Issue**: AI agents don't know LiveSpec is present

**Evidence from session:**
- Never mentioned AGENTS.md
- Never read workspace constitution
- Never suggested using methodology prompts
- Proceeded as if no methodology existed

**Why**:
- Files exist but aren't in AI's default context
- No breadcrumb from PURPOSE.md
- No integration with Claude Code workflow

**Recommendation**: Auto-injection mechanism

```markdown
<!-- In PURPOSE.md -->
# Hoardwick

**Development Methodology**: This project uses [LiveSpec](/.livespec/AGENTS.md).

**AI Agents**: Read `.livespec/AGENTS.md` before any implementation.
```

Or better: Claude Code integration

```json
// .claude/settings.local.json
{
  "always-include-context": [
    ".livespec/AGENTS.md",
    "specs/workspace/constitution.spec.md"
  ]
}
```

### 3. No Slash Command Integration (CRITICAL)

**Issue**: LiveSpec prompts exist but aren't accessible via workflow

**Current**: `.livespec/prompts/` directory with 20+ prompts
**Missing**: `.claude/commands/` integration

**Recommendation**: Generate slash commands during setup

```bash
# Auto-generate from prompts
mkdir -p .claude/commands

# For each prompt in .livespec/prompts/
# Create corresponding slash command
echo "Use .livespec/prompts/1-design/1b-define-behaviors.md" > \
  .claude/commands/define-behavior.md
```

**Better**: Make this part of LiveSpec distribution

```
.livespec/
├── prompts/                # Methodology prompts
├── claude-commands/        # Pre-generated slash commands
│   ├── design-behavior.md
│   ├── implement.md
│   ├── detect-drift.md
│   └── ...
└── install.sh             # Symlinks claude-commands → .claude/commands/
```

### 4. No Pre-Flight Checks (CRITICAL)

**Issue**: Can implement without spec verification

**Current**: Agent proceeds to implementation immediately
**Needed**: Mandatory spec check before any code change

**Recommendation**: Add verification layer

```markdown
# .livespec/guards/check-spec-exists.md

Before implementing, verify:

1. Check for spec:
   ls specs/3-behaviors/[feature].spec.md || \
   ls specs/3-contracts/[feature].spec.md

2. If NO spec:
   - STOP implementation
   - Output: "Spec required. Use /define-behavior first."
   - Link to Phase 1 prompts

3. If YES spec:
   - Read spec completely
   - Verify requirements clear
   - Proceed with implementation
```

Then configure Claude Code to always check this before coding.

### 5. No Drift Detection (IMPORTANT)

**Issue**: Code and specs diverge silently

**Current**:
- `scanner.spec.md` says lazy hashing < 100MB always
- Code now uses `--hash-files` flag (default OFF)
- No alert, no warning

**Needed**: Automated drift detection

**Recommendation**: Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for drift between code and specs
python3 .livespec/detect-drift.py

if [ $? -ne 0 ]; then
    echo "❌ Drift detected between code and specifications"
    echo "Run: /detect-drift to sync"
    exit 1
fi
```

Or GitHub Actions workflow:

```yaml
# .github/workflows/spec-drift.yml
name: Spec Drift Detection
on: [push, pull_request]
jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check spec-code alignment
        run: python3 .livespec/detect-drift.py
```

### 6. Spec Status Invisibility (IMPORTANT)

**Issue**: No visibility into spec coverage

**Needed**: Dashboard showing:
- Which files have specs
- Which specs are outdated
- What needs specification

**Recommendation**: Quick status command

```bash
# Add to .livespec/utils/
./check-spec-coverage.sh

# Output:
Spec Coverage Report
====================
✅ scan.py → specs/3-behaviors/scanner.spec.md (OUTDATED)
✅ analyse.py → specs/3-behaviors/analyser.spec.md (OK)
❌ cleanup.py → NO SPEC
⚠️  New functions without specs: 3

Run /define-behavior to create missing specs
```

### 7. Workspace Constitution Not Integrated (IMPORTANT)

**Issue**: Constitution exists but AI never reads it

**File**: `specs/workspace/constitution.spec.md`
**Content**:
- "Each script has matching `.spec.md` file"
- "Minimal specifications - only what's essential"
- "Type hints for function signatures"

**Problem**: AI didn't know to check this

**Recommendation**: Constitution as pre-flight requirement

```markdown
# .livespec/guards/check-constitution.md

Before any implementation:

1. Read specs/workspace/constitution.spec.md
2. Verify your plan follows all principles
3. If uncertain, ask user for clarification
4. Only proceed when constitution-compliant
```

## What Would Have Prevented Today's Issues

### Scenario: AI Starts Coding Scan Improvements

**What Actually Happened:**
1. User: "Scan took 6 hours, fix performance"
2. AI: *Immediately starts analyzing code and proposing changes*
3. AI: *Implements changes directly*
4. Result: 200+ lines changed, 0 spec updates

**What Should Have Happened with Enforcement:**

```
User: "Scan took 6 hours, fix performance"

AI: [Pre-flight check triggered]
    - Loading .livespec/AGENTS.md...
    - Reading specs/workspace/constitution.spec.md...
    - Checking specs/3-behaviors/scanner.spec.md...

AI: "I found scanner.spec.md. Let me verify it's current before proposing changes."

AI: [Reads scanner.spec.md]
    - Lazy hashing: < 100MB
    - Aggregate patterns: node_modules, .git, __pycache__, .next, etc.
    - Checkpoint-based resumption

AI: "The spec describes current scanner behavior. Your performance issues suggest:
    1. Hashing strategy too aggressive (551k files hashed)
    2. Missing .cache/ from aggregate patterns

    Before implementing fixes, I should update scanner.spec.md to reflect new requirements.

    Should I use /detect-drift to document current state, then /define-behavior to specify improvements?"

User: "Yes, let's do that properly"

AI: [Follows Phase 4 → Phase 1 → Phase 2 workflow]
    1. Documents current behavior
    2. Creates updated spec with new requirements
    3. Implements according to spec
    4. Updates spec with actual implementation
```

**Difference**: Methodology awareness built into workflow, not optional.

## Specific Recommendations for LiveSpec Project

### Immediate (Can Implement Now)

**1. Add Installation Checklist**

Update `.livespec/README.md`:

```markdown
# LiveSpec Installation

After copying .livespec/ to your project:

## Required Steps

- [ ] Create `.claude/commands/` and symlink prompts
- [ ] Add AGENTS.md reference to PURPOSE.md
- [ ] Configure Claude Code to auto-load workspace specs
- [ ] Add pre-commit hooks for drift detection
- [ ] Create spec coverage dashboard script

## Verification

Run: `./livespec-verify.sh`

Should see:
✅ Slash commands configured
✅ AGENTS.md accessible to AI
✅ Workspace specs in auto-context
✅ Pre-commit hooks active
```

**2. Generate Claude Code Integration**

Add to LiveSpec distribution:

```
.livespec/
└── integrations/
    └── claude-code/
        ├── commands/              # Slash commands for each prompt
        ├── settings.template.json # Auto-context configuration
        └── install-claude.sh      # Sets up integration
```

**3. Create Enforcement Scripts**

```bash
.livespec/
└── guards/
    ├── check-spec-exists.py      # Verify spec before implementation
    ├── detect-drift.py            # Compare code vs specs
    ├── spec-coverage.py           # Coverage report
    └── install-hooks.sh           # Set up git hooks
```

**4. Add Breadcrumb to PURPOSE.md Template**

```markdown
# templates/PURPOSE.md

# Project Name

**Purpose**: [Why this exists]

**Development**: This project uses [LiveSpec](/.livespec/AGENTS.md) methodology.

**AI Agents**: Always read `.livespec/AGENTS.md` before implementing features.
```

### Short-Term (Next Release)

**1. Active Enforcement Mode**

New configuration option:

```yaml
# .livespec/config.yml
enforcement:
  mode: strict          # strict | advisory | off
  require-specs: true
  block-without-spec: true
  auto-drift-check: true
```

**2. Claude Code Native Integration**

Propose integration to Claude Code team:

```json
// Proposed .claude/livespec.json
{
  "enabled": true,
  "spec-first-enforcement": true,
  "auto-context": [
    ".livespec/AGENTS.md",
    "specs/workspace/"
  ],
  "pre-implementation-checks": [
    "check-spec-exists",
    "verify-constitution"
  ]
}
```

**3. Spec Status in Editor**

Visual indicators:

```
scan.py  [📋 Spec: OUTDATED]
analyse.py  [📋 Spec: OK]
cleanup.py  [❌ No spec]
```

**4. Interactive Spec Creation**

When AI detects missing spec:

```
AI: "cleanup.py has no specification. Create one now?"
    [Yes - Use /define-behavior]
    [Later - Add to backlog]
    [Skip - I know what I'm doing]
```

### Long-Term (Future Versions)

**1. LSP Server for Spec Checking**

Real-time spec validation:

```
[In editor, writing code]
function hashFile(path: string): void {
  ...
}

[Inline warning appears]
⚠️  No spec requirement found for hashFile()
    scanner.spec.md doesn't mention file hashing behavior
    [Create spec requirement] [Ignore]
```

**2. AI-Powered Drift Reconciliation**

```bash
./livespec drift reconcile

Drift detected in scan.py:
  Code: Uses --hash-files flag (defaults OFF)
  Spec: Says "hashes files < 100MB" (always)

Suggested resolution:
  Update spec to match code implementation

[Show diff] [Apply] [Manual]
```

**3. Spec Test Generation**

```bash
./livespec generate tests specs/3-behaviors/scanner.spec.md

Generated tests/behaviors/scanner.test.ts:
  ✓ Scanner aggregates node_modules
  ✓ Scanner uses lazy hashing when flag set
  ✓ Scanner creates checkpoints every 1000 files
```

**4. Methodology Compliance Score**

```
Project: Hoardwick
LiveSpec Compliance: 67%

✅ Specs exist (8/10 files)
⚠️  Specs outdated (3/8 specs)
❌ No pre-commit hooks
✅ Workspace constitution defined
⚠️  Drift detected (2 files)

Recommendations:
  1. Run /detect-drift and sync specifications
  2. Create specs for cleanup.py
  3. Install git hooks for enforcement
```

## Comparison: What Works vs What's Missing

### Works Well ✅

1. **Prompt Structure**: Phase-based organization clear and logical
2. **MSL Format**: Minimal specs are effective when used
3. **AGENTS.md**: Comprehensive guidance document
4. **Dogfooding**: LiveSpec uses itself (good validation)
5. **Documentation**: Excellent explanations of methodology

### Missing ❌

1. **Discoverability**: AI agents don't know LiveSpec is there
2. **Enforcement**: Methodology passive, not active
3. **Integration**: No Claude Code / editor integration
4. **Automation**: No drift detection, no auto-checks
5. **Visibility**: No spec status, no coverage dashboard
6. **Workflow**: Prompts not in execution path (no slash commands)

## Key Insights for LiveSpec Evolution

### 1. Methodology Needs Teeth

**Current**: Beautiful methodology documentation
**Reality**: Ignored when not convenient
**Solution**: Enforcement mechanisms that make compliance the path of least resistance

### 2. Passive Documentation Doesn't Work

**Insight**: Having great docs in `.livespec/` doesn't help if AI never reads them
**Solution**: Inject into AI context automatically, make unavoidable

### 3. Familiarity Defeats Discipline

**Observation**: Even with methodology present, AI bypassed it because user's problem felt urgent
**Solution**: Hard stops that force methodology even when "obvious" solutions exist

### 4. Tooling Gap

**Issue**: LiveSpec is files and structure, but modern development needs tool integration
**Solution**: Native editor support, git hooks, CI/CD workflows, status dashboards

### 5. Default Path Matters

**Current**: Following LiveSpec requires extra steps
**Better**: Following LiveSpec is the default, bypassing it requires effort

## Recommended Next Steps for LiveSpec

### Priority 1: Enforcement Foundation

1. Create `check-spec-exists` guard script
2. Add git pre-commit hook template
3. Generate Claude Code slash commands
4. Add AGENTS.md breadcrumb to PURPOSE.md template

### Priority 2: Discovery Improvement

1. Auto-context configuration for Claude Code
2. Installation verification script
3. Quick-start checklist in README
4. Visual indicators of LiveSpec presence

### Priority 3: Drift Prevention

1. Drift detection script
2. CI/CD workflow template
3. Spec coverage reporter
4. Reconciliation tools

### Priority 4: Developer Experience

1. Slash command shortcuts
2. Interactive spec creation
3. Status dashboard
4. IDE extensions (VS Code, etc.)

## Meta-Note: Irony of This Situation

**The AI agent writing this feedback is the same one that violated the methodology all day.**

This isn't a failure of:
- User understanding (they set up LiveSpec correctly)
- Local installation (all files present and accessible)
- Documentation (comprehensive and clear)

This is a failure of:
- Discovery (AI didn't know to look)
- Enforcement (nothing prevented violation)
- Integration (methodology disconnected from workflow)

**Lesson**: Great methodology + poor integration = bypassed methodology

## Conclusion

LiveSpec has **excellent foundations** but needs an **enforcement layer** to translate from "methodology available" to "methodology followed." The gap isn't in the philosophy or structure - it's in making that structure **unavoidable** in the development workflow.

Key changes needed:
1. ✅ Make LiveSpec **discoverable** (AI must encounter it)
2. ✅ Make LiveSpec **enforced** (hard to bypass)
3. ✅ Make LiveSpec **integrated** (part of tooling, not separate)
4. ✅ Make LiveSpec **visible** (status always apparent)

With these enhancements, LiveSpec could move from "best practice documentation" to "development methodology that works in practice."

---

**Project**: Hoardwick
**Session**: 2025-10-16
**AI Agent**: Claude (Sonnet 4.5)
**LiveSpec**: v2.1.0
**Outcome**: Successful performance fixes, complete methodology bypass, valuable insights for LiveSpec improvement

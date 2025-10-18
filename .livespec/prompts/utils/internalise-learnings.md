---
generated: 2025-10-16T14:00:00Z
generated_by: Manual creation following .livespec/prompts/utils/generate-internalise-learnings.md
sources:
  - specs/workspace/constitution.spec.md
  - specs/workspace/patterns.spec.md
  - specs/workspace/workflows.spec.md
phase: utils
purpose: Capture learnings from conversations into Hoardwick specifications
---

# Internalise Learnings

<ultrathink>
I need to analyze THIS conversation to capture learnings for Hoardwick.

**Hoardwick Top Principles:**
1. Minimal specifications - only what's essential
2. Evolve existing code - never duplicate files
3. Safety first - read-only by default
4. Preview before action - no surprises
5. Cross-platform from start - WSL and Windows

**Hoardwick Spec Structure:**
- specs/workspace/: Process (constitution, patterns, workflows)
- specs/1-requirements/strategic/: Mission (outcomes, constraints)
- specs/2-strategy/: Technical approach (architecture)
- specs/3-behaviors/: Observable features (scanner, etc.)

**Update Workflow** (from workflows.spec.md):
- When new pattern emerges: Add to patterns.spec.md
- When safety issue discovered: Document in workflows.spec.md or constitution.spec.md
- When requirements change: Update spec first, then code
- When implementation reveals requirements: Update spec immediately

**I will scan THIS conversation for:**
- User corrections to my assumptions
- Clarifications about storage management, cleanup safety, cross-platform issues
- Patterns that emerged during cleanup work
- Anti-patterns identified (logging in JSON, missing specs)
- Knowledge gaps that caused issues (LiveSpec not followed, preferences architecture)
</ultrathink>

## Execution

### Phase 1: Conversation Analysis

Scanning THIS conversation for learnings...

**Looking for:**
- User corrections to assumptions
- Clarifications about cleanup safety, VS Code usage, crypto wallets
- Patterns that emerged (aggregate detection, preference learning)
- Anti-patterns identified (preferences.json as log, missing workspace specs)
- Knowledge gaps that caused issues (LiveSpec passive not active)

### Phase 2: Learning Classification

**Mapping learnings to Hoardwick specification structure:**

**Process Learnings** (→ specs/workspace/):
- How we work, conventions, safety principles
- Files:
  - specs/workspace/constitution.spec.md (core principles)
  - specs/workspace/patterns.spec.md (coding patterns)
  - specs/workspace/workflows.spec.md (development workflows)

**Mission Learnings** (→ specs/1-requirements/strategic/):
- High-level requirements, constraints
- Files:
  - specs/1-requirements/strategic/outcomes.spec.md
  - specs/1-requirements/strategic/constraints.spec.md

**Strategy Learnings** (→ specs/2-strategy/):
- Architectural decisions, technical approach
- Files:
  - specs/2-strategy/architecture.spec.md

**Behavior Learnings** (→ specs/3-behaviors/):
- Observable outcomes, features
- Files:
  - specs/3-behaviors/scanner.spec.md
  - specs/3-behaviors/preference-learning.spec.md (needs creation)

### Phase 3: Spec Update Recommendations

For each learning identified in conversation, propose:

1. **Target spec:** [specific file path in specs/]
2. **Update type:** [new spec | update existing | add validation]
3. **Specific change:** [actual content to add/modify following MSL minimalism]
4. **Rationale:** [why this prevents future mistakes]

**MSL Minimalism Check** (before adding to specs):
- Would the system fail without this requirement? (If no → exclude)
- Am I specifying HOW instead of WHAT? (If yes → remove)
- What specific problem does this prevent? (If theoretical → omit)
- Could this be inferred or is it conventional? (If yes → don't state)

### Phase 4: Implementation Plan

**Steps to capture learnings:**
1. Review proposed spec updates above
2. Create/update specs following patterns.spec.md:
   - MSL format (YAML frontmatter, Requirements section)
   - One requirement per observable need
   - Justify each requirement's existence
3. Validate changes against constitution.spec.md principles:
   - Minimal specifications only
   - Safety-first approach documented
   - Cross-platform considerations noted
4. Test that documented learning prevents repetition
5. Update CLAUDE.md if user-facing workflow changes

## Learning Summary

**To be filled after analyzing THIS conversation:**

**Patterns Recognized:** [From this specific conversation]
**Spec Updates Needed:** [Specific file paths]
**Principles Reinforced:** [From constitution.spec.md]
**Anti-Patterns Identified:** [What to avoid in future]

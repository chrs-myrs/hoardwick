---
type: metaspec
purpose: Define quality criteria for persona documents
applies_to: research/personas/*.md
note: This is guidance, not an MSL spec. Personas are discovery artifacts, not specifications.
---

# Persona Metaspec

**Purpose**: Define what constitutes a well-formed user persona document that effectively informs requirements.

## Essential Elements

A well-formed persona document MUST include:

- [ ] **Identity**
  - Name (real or pseudonym)
  - Role/title clearly stated
  - Demographic context (if relevant to product)

- [ ] **Goals**
  - Primary goal (main objective)
  - Secondary goals (supporting objectives)
  - Success criteria (how they measure success)

- [ ] **Behaviors**
  - Observable patterns (how they currently work)
  - Tool usage (what they use today)
  - Frequency (how often they perform key tasks)

- [ ] **Pain Points**
  - Current frustrations (what doesn't work)
  - Workarounds (how they cope today)
  - Impact (consequences of pain points)

- [ ] **Needs** (that will inform requirements)
  - Explicit needs (what they ask for)
  - Latent needs (what they don't know they need)
  - Links to requirements these will inform

## Quality Criteria

### Evidence-Based
Personas MUST be based on actual user research, not assumptions:
- References research source (interviews, surveys, observations)
- Sample size indicated (n=X users)
- Method documented (how data collected)

### Specific
Detailed enough to inform design decisions:
- Concrete examples, not generalities
- Quotes from actual users (if available)
- Specific behaviors, not vague descriptions

### Actionable
Clear implications for requirements:
- Each need links to potential requirement
- Pain points suggest solutions
- Goals inform success criteria

## Validation Checklist

Before using persona to inform requirements:

1. [ ] **Evidence documented**
   - Research source identified
   - Sample size stated
   - Method clear

2. [ ] **Specificity check**
   - Concrete examples provided
   - No vague generalities
   - Actual user quotes included

3. [ ] **Actionability verified**
   - Needs map to specific requirements
   - Pain points imply solutions
   - Goals inform success criteria

4. [ ] **Bias check**
   - Not based on assumptions
   - Multiple users represented
   - Edge cases considered

## Anti-Patterns

**Avoid these common mistakes:**

❌ **Assumption-based personas**
```markdown
## Goals
- Wants to save time (assumption, not researched)
```

✅ **Evidence-based**:
```markdown
## Goals
- Wants to save time
  - Evidence: 8/10 interviewees mentioned time pressure
  - Quote: "I only have 5 minutes during lunch" (P3)
```

❌ **Vague pain points**:
```markdown
## Pain Points
- System is slow
```

✅ **Specific pain points**:
```markdown
## Pain Points
### Checkout Takes Too Long
- **Issue**: 5-step checkout process takes 8-10 minutes
- **Workaround**: Save items to cart, complete later
- **Impact**: Abandons 40% of carts due to time
- **Quote**: "By step 3 I've given up" (P7)
```

❌ **Unlinked needs**:
```markdown
## Needs
- Faster checkout
```

✅ **Linked needs**:
```markdown
## Needs
### Need: Checkout in ≤3 Steps
- **Priority**: HIGH
- **Informs**: `specs/requirements/functional/simplified-checkout.spec.md`
- **Rationale**: Current 5-step process causes 40% cart abandonment
- **Evidence**: User interviews (n=10), analytics data
```

## Template Location

`.livespec/templates/research/persona.md.template`

## Example

See: `examples/ecommerce-checkout/research/personas/busy-professional.md`

## Relationship to Requirements

Personas inform functional requirements via `informed-by:` frontmatter:

```yaml
# specs/requirements/functional/simplified-checkout.spec.md
---
informed-by:
  - research/personas/busy-professional.md
  - research/personas/first-time-buyer.md
---
```

The persona's needs become the functional requirements. The persona provides the **user context** that justifies **why** the requirement exists.

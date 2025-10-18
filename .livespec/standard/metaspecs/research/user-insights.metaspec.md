---
type: metaspec
purpose: Define quality criteria for user research documentation
applies_to: research/insights/*.md
note: This is guidance, not an MSL spec. Insights documents capture research findings.
---

# User Insights Metaspec

**Purpose**: Define what constitutes well-documented user research that provides credible evidence for requirements decisions.

## Essential Elements

A well-formed user insights document MUST include:

- [ ] **Research Method**
  - Type (interviews, surveys, usability tests, observation, diary studies)
  - Protocol (questions asked, tasks given, observation framework)
  - Duration (per session, total time)

- [ ] **Sample Description**
  - Size (number of participants)
  - Demographics (relevant characteristics)
  - Recruitment method (how participants selected)
  - Screening criteria (inclusion/exclusion)

- [ ] **Key Findings**
  - Observable patterns
  - Direct evidence (quotes, observations, data)
  - Frequency (how many participants showed this)

- [ ] **Synthesis**
  - Themes across findings
  - Patterns and connections
  - Unexpected insights

- [ ] **Implications**
  - What this means for requirements
  - Specific recommendations
  - Priority indication

- [ ] **Requirements Informed**
  - Links to functional requirements
  - How findings inform specifications
  - Validation approach

## Quality Criteria

### Method Clearly Documented
Research MUST be replicable:
- Method described in detail
- Protocol/questions included or referenced
- Conditions noted (location, tools used, etc.)

### Sample Adequately Described
Understand who was researched:
- Size sufficient for method (5-8 for qual, 30+ for quant)
- Demographics relevant to product
- Recruitment unbiased

### Evidence Separated from Interpretation
Clear distinction between:
- **Raw data**: Direct quotes, observed behaviors, measured data
- **Interpretation**: What researcher concludes from data
- **Implications**: What this means for product

### Findings Actionable
Research leads to clear next steps:
- Specific recommendations
- Linked to requirements
- Priority based on user impact

## Validation Checklist

Before using insights to inform requirements:

1. [ ] **Method validity**
   - Appropriate for research question
   - Sample size adequate
   - Protocol sound

2. [ ] **Evidence quality**
   - Direct quotes/observations provided
   - Frequency indicated (n=X)
   - Edge cases noted

3. [ ] **Synthesis quality**
   - Patterns identified across findings
   - Connections made explicit
   - Unexpected insights highlighted

4. [ ] **Implications clear**
   - Recommendations specific
   - Requirements linkage explicit
   - Priority justified

## Structure

### Minimum Viable Insights Document

```markdown
# [Research Topic] - [Date]

**Method**: [Type]
**Sample**: n=[X], [demographics]
**Date**: YYYY-MM-DD

## Key Findings

### Finding 1: [Pattern]
**Evidence**: "[Quote]" (P1, P3, P5 - 3/10 users)
**Interpretation**: [What this means]
**Implication**: [What to do]

## Requirements Informed
- [Requirement link] - Based on [which findings]
```

## Anti-Patterns

**Avoid these common mistakes:**

❌ **Vague method**:
```markdown
**Method**: Interviewed some users
```

✅ **Clear method**:
```markdown
**Method**: Semi-structured interviews
**Protocol**: 10 open-ended questions about current checkout experience
**Duration**: 45-60 minutes per session
**Location**: Video call (Zoom)
**Date range**: 2025-01-10 to 2025-01-20
**Sample**: n=10, online shoppers who made 3+ purchases in last 6 months
**Recruitment**: Email to existing customers, $50 incentive
```

❌ **Inadequate sample description**:
```markdown
**Sample**: 10 users
```

✅ **Adequate sample description**:
```markdown
**Sample**: n=10
**Demographics**:
- Age: 25-45 (mean=34)
- Gender: 6 female, 4 male
- Tech proficiency: 7 high, 3 medium (self-reported)
- Shopping frequency: All shop online 2+ times/month
**Recruitment**: Email to customers who made 3+ purchases last 6 months
**Screening**: Excluded anyone who works in e-commerce/UX
**Incentive**: $50 Amazon gift card
```

❌ **Interpretation without evidence**:
```markdown
## Finding: Users Want Faster Checkout
Users are frustrated with checkout length.
```

✅ **Evidence-based finding**:
```markdown
## Finding 1: Checkout Length Causes Abandonment

### Evidence
**Observed behavior**:
- 7/10 participants sighed or showed frustration during checkout
- Average time: 8.5 minutes (measured)
- 4/10 mentioned considering abandoning mid-checkout

**Direct quotes**:
- "This is taking forever, I might just come back later" (P3)
- "Why do they need all this information?" (P7)
- "I'm on my lunch break, don't have time for this" (P2, P5, P9)

**Quantified**: 7/10 showed frustration, 4/10 considered abandoning

### Interpretation
Checkout length exceeds user time expectations and tolerance, particularly for time-constrained situations (lunch break, quick purchase).

### Implication
**Requirement**: Simplify checkout to ≤3 minutes for time-constrained users
**Priority**: HIGH (affects 70% of sample, 40% abandonment risk)
**Informs**: `specs/requirements/functional/simplified-checkout.spec.md`
```

❌ **Vague recommendations**:
```markdown
## Recommendations
- Make checkout better
- Improve user experience
```

✅ **Specific, actionable recommendations**:
```markdown
## Recommendations

### 1. Reduce Checkout to 3 Steps Maximum
**Based on**: Finding 1 (checkout length), Finding 3 (form fatigue)
**Priority**: HIGH
**Rationale**: 8.5 min current avg, users expect <3 min
**Informs**: `specs/requirements/functional/simplified-checkout.spec.md`
**Validation approach**: Time-to-completion metric, abandonment rate

### 2. Implement Guest Checkout
**Based on**: Finding 2 (account creation resistance)
**Priority**: HIGH
**Rationale**: 6/10 users attempted to skip account creation
**Informs**: `specs/requirements/functional/guest-checkout.spec.md`
**Validation approach**: Guest checkout usage rate, conversion improvement

### 3. Add Inline Form Validation
**Based on**: Finding 4 (error frustration)
**Priority**: MEDIUM
**Rationale**: Users want immediate feedback, not end-of-form errors
**Informs**: `specs/requirements/functional/smart-forms.spec.md`
**Validation approach**: Error recovery rate, form completion time
```

## Evidence Hierarchy

**Strongest to weakest:**

1. **Measured behavior**: Direct observation, analytics, time measurements
2. **Reported behavior**: What users say they do (verify with observation)
3. **Preferences**: What users say they want (validate against behavior)
4. **Opinions**: What users think (interesting, but lowest priority)

Always prioritize observed/measured over self-reported.

## Template Location

`.livespec/templates/research/user-insights.md.template`

## Example

See: `examples/ecommerce-checkout/research/insights/user-interviews-2025-01.md`

## Relationship to Requirements

Research insights provide the **evidence base** for requirements:

```
Research Finding → User Need → Functional Requirement

"7/10 users frustrated by checkout length" → "Need faster checkout" → "Complete checkout in ≤3 steps"
```

```yaml
# specs/requirements/functional/simplified-checkout.spec.md
---
informed-by:
  - research/insights/user-interviews-2025-01.md
validation_notes: |
  Based on interviews (n=10): 70% showed checkout frustration,
  avg time 8.5 min, 40% considered abandoning.
  Target: <3 min, <10% abandonment.
---
```

Research provides the **why** and **evidence** behind every requirement.

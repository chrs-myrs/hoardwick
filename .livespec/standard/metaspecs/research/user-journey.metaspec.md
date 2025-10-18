---
type: metaspec
purpose: Define quality criteria for user journey maps
applies_to: research/journeys/*.md
note: This is guidance, not an MSL spec. Journeys are discovery artifacts that map user experience.
---

# User Journey Metaspec

**Purpose**: Define what constitutes a well-formed user journey map that effectively identifies pain points and informs requirements.

## Essential Elements

A well-formed user journey document MUST include:

- [ ] **Journey Context**
  - Associated persona (who is on this journey)
  - Goal (what user wants to accomplish)
  - Entry point (how journey begins)
  - Exit/success state (what completion looks like)

- [ ] **Sequential Steps**
  - Ordered stages of the journey
  - Actions taken at each step
  - Touchpoints (where interaction happens)

- [ ] **Pain Points Per Step**
  - Specific frictions encountered
  - User emotional state
  - Observable frustrations

- [ ] **Needs Identified**
  - What would improve this journey
  - Links to requirements these inform
  - Priority indication

- [ ] **Evidence**
  - Research method (observation, interview, diary study)
  - Sample size
  - User quotes/observations

## Quality Criteria

### Based on Actual User Observation
Journey MUST reflect real user behavior, not idealized flow:
- Observed in actual use OR reported in interviews
- Alternative paths documented (not just happy path)
- Failure scenarios included

### Pain Points Specific and Documented
Each pain point MUST be:
- Concrete and observable
- Backed by evidence (quotes, observations)
- Linked to user impact

### Requirements Traceability Clear
Journey MUST show:
- Which pain points inform which requirements
- How needs map to solutions
- Priority based on user impact

### Insights Actionable
Journey findings MUST:
- Suggest specific improvements
- Inform functional requirements
- Enable validation criteria

## Validation Checklist

Before using journey to inform requirements:

1. [ ] **Evidence complete**
   - Method documented
   - Sample size stated
   - User quotes included

2. [ ] **Pain points specific**
   - Each step has pain points identified
   - Impact described
   - User emotional state noted

3. [ ] **Traceability established**
   - Pain points map to requirements
   - Requirements reference this journey
   - Priority informed by impact

4. [ ] **Alternative paths covered**
   - Error scenarios documented
   - Workarounds observed
   - Edge cases considered

## Structure

### Minimum Viable Journey Map

```markdown
# [Journey Name]

**Persona**: [Link to persona]
**Goal**: [What user wants]
**Entry**: [How journey starts]
**Success**: [What completion looks like]

## Step 1: [Name]
**Action**: [What user does]
**Touchpoint**: [Where]
**Pain points**:
- [Specific friction]
**Needs**: [What would help] → informs [requirement link]

## Step 2: [Next]
[...]

## Key Insights
- [Insight 1] → informs [requirement]
```

## Anti-Patterns

**Avoid these common mistakes:**

❌ **Idealized journey** (not based on observation):
```markdown
## Step 1: User Opens App
**Action**: Quickly navigates to product
**Pain points**: None - it's intuitive!
```

✅ **Realistic journey** (observed behavior):
```markdown
## Step 1: User Opens App
**Action**: Looks for search, tries menu, scrolls homepage
**Touchpoint**: Mobile app homepage
**User state**: Confused (tried 3 different approaches)
**Pain points**:
- Search icon not prominent (6/10 users missed it)
- Menu has too many options (users gave up scanning)
- Homepage doesn't show user's interests
**Evidence**: "Where do I search? I'm lost" (P4, P7, P9)
**Needs**: Prominent search → informs simplified-navigation.spec.md
```

❌ **Vague pain points**:
```markdown
## Pain Points
- Process is confusing
```

✅ **Specific pain points**:
```markdown
## Pain Points
### Shipping Address Form Too Long
- **Issue**: 8 required fields for digital product
- **User state**: Frustrated (sighs, considers abandoning)
- **Workaround**: Enters fake address to proceed
- **Impact**: 25% abandon at this step
- **Evidence**: Observed in 7/10 usability tests
- **Needs**: Conditional form fields → informs smart-forms.spec.md
```

❌ **Missing traceability**:
```markdown
## Insights
- Users want faster checkout
```

✅ **Clear traceability**:
```markdown
## Key Insights

### Insight 1: Checkout Too Many Steps
**Evidence**: Average completion time 8.5 minutes, target <3 minutes
**User impact**: 40% cart abandonment (analytics)
**Requirements informed**:
- `specs/requirements/functional/simplified-checkout.spec.md`
  - Based on: Steps 3-7 pain points
  - Requirement: Reduce to ≤3 steps
  - Validation: Complete in <3 minutes
```

## Template Location

`.livespec/templates/research/user-journey.md.template`

## Example

See: `examples/ecommerce-checkout/research/journeys/buyer-purchase-journey.md`

## Relationship to Requirements

Journeys inform functional requirements by identifying pain points that become requirements:

```
Journey Pain Point → User Need → Functional Requirement

"Checkout takes 8 minutes" → "Need faster checkout" → "Checkout in ≤3 steps"
```

```yaml
# specs/requirements/functional/simplified-checkout.spec.md
---
informed-by:
  - research/journeys/buyer-purchase-journey.md
validation_notes: |
  Journey shows 8.5 min avg checkout time, 40% abandonment.
  Target: <3 minutes, <10% abandonment based on journey insights.
---
```

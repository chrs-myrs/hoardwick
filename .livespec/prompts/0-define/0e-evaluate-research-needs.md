---
implements: specs/3-behaviors/prompts/0e-evaluate-research-needs.spec.md
---

# 0e: Evaluate Research Needs

**Phase**: DEFINE
**Purpose**: Intelligently assess whether research is needed to inform requirements
**Prerequisites**: PURPOSE.md, outcomes.spec.md, complexity-assessment.md exist
**Optional**: Skip entirely for projects without user research needs

## When to Use This

**Use when:**
- Building user-facing features
- User workflows or pain points unclear
- Multiple user types with different needs
- UX patterns need validation
- Requirements based on assumptions
- Stakeholder alignment on needs required

**Skip when:**
- Backend API with defined contract
- Infrastructure/tooling project
- Internal automation (no complex users)
- Requirements fully documented from prior research
- Simple CRUD following standard patterns

## Task

Analyze the project and suggest targeted research activities that would improve requirements quality. Make research feel valuable, not like busywork.

## Instructions

### Step 1: Analyze Project Characteristics

Read the following files:
- `PURPOSE.md` - Understand project vision
- `specs/1-requirements/strategic/outcomes.spec.md` - Review requirements
- `specs/1-requirements/strategic/complexity-assessment.md` - Understand complexity

Answer these questions:

**1. Project Type Classification:**
- [ ] User-facing application (web/mobile app with end-users)
- [ ] Developer platform (APIs, SDKs, tools for developers)
- [ ] Internal tool (used by organization members)
- [ ] Infrastructure (backend systems, no direct users)
- [ ] Governance (processes, policies, procedures)
- [ ] Hybrid (multiple types)

**2. User Understanding:**
- Are user types clearly defined? (Yes/No/Partial)
- Are user goals documented? (Yes/No/Assumptions)
- Are user workflows understood? (Yes/No/Hypothetical)
- Are pain points known? (Yes/No/Assumed)

**3. Complexity Factors:**
- From complexity-assessment.md:
  - Discovery needs score: [X/10]
  - Requirements volatility: [X/10]
- Are UX patterns established or novel?
- Are there multiple user segments?

### Step 2: Check Existing Research

Check if `research/` folder exists and contains:
- `personas/*.md` - User personas
- `journeys/*.md` - User journey maps
- `flows/*.md` - UX flow diagrams
- `insights/*.md` - Research findings

**For each existing artifact:**
- Does it align with current project scope?
- Is it recent/relevant?
- Does it cover identified user types?
- Are there gaps?

### Step 3: Identify Research Gaps

Based on project type and existing research, identify what's missing:

#### User-Facing Applications

**Likely need:**
- **Personas** - If multiple user types with different goals
- **User Journeys** - If workflows cross multiple touchpoints/steps
- **UX Flows** - If interaction patterns need validation
- **User Insights** - If pain points or needs are assumptions

#### Developer Platforms

**Likely need:**
- **Developer Personas** - If serving multiple developer types (beginners, experts)
- **Integration Journeys** - If complex onboarding/setup workflows
- **API Flows** - If interaction patterns non-obvious
- **User Insights** - If developer needs unclear (interview potential users)

#### Internal Tools

**Likely need:**
- **User Personas** - If different roles use tool differently
- **Workflow Journeys** - If complex business processes
- **UX Flows** - If novel interaction patterns
- **User Insights** - If stakeholder needs unclear

#### Infrastructure/Governance

**Likely skip research** - But consider:
- **Technical Spike** - If architectural approaches uncertain
- **Stakeholder Insights** - If requirements unclear/contentious

### Step 4: Prioritize Research Activities

For each identified gap, assess:

**Priority Levels:**

**HIGH** - Do this first:
- Critical to project success
- Prevents costly mistakes
- Blocks design decisions
- High uncertainty/risk

**MEDIUM** - Valuable but optional:
- Improves quality
- Reduces some uncertainty
- Can design without it (with assumptions)

**LOW** - Nice to have:
- Refinement/optimization
- Low risk if skipped
- Can validate during/after implementation

**Effort Estimates:**
- **Quick** (2-4 hours): Single persona, simple flow
- **Moderate** (1-2 days): Multiple personas, journey mapping, simple insights study
- **Substantial** (3-5 days): Comprehensive insights study with interviews/testing

### Step 5: Present Recommendations

Create a prioritized list:

```markdown
# Research Evaluation for [Project]

**Date**: [YYYY-MM-DD]
**Project Type**: [Classification]
**Existing Research**: [Summary of what exists in research/]

## Recommendations

### HIGH Priority (Do These)

#### 1. [Research Activity]
**Type**: [Persona/Journey/Flow/Insights]
**Rationale**: [Why this matters - what decisions it will inform]
**Effort**: [Quick/Moderate/Substantial] ([X hours/days])
**Template**: `.livespec/templates/research/[template].md.template`
**Quality Guide**: `.livespec/standard/metaspecs/research/[metaspec].metaspec.md`
**Informs**:
- specs/requirements/functional/[feature].spec.md
- specs/requirements/functional/[feature].spec.md

**Questions This Answers:**
- [Key question 1]
- [Key question 2]

---

#### 2. [Next HIGH priority activity]
[Same structure...]

### MEDIUM Priority (Consider These)

#### 3. [Research Activity]
[Same structure...]

### LOW Priority (Optional)

#### 4. [Research Activity]
[Same structure...]

## If You Skip Research

**Risks:**
- [What could go wrong without this research]
- [Assumptions that may be incorrect]

**Mitigation:**
- Document assumptions in requirements
- Plan validation during implementation
- Budget time for iteration when assumptions prove wrong

## Next Steps

**If proceeding with research:**
1. Choose HIGH priority activities to start
2. Use templates to create artifacts in research/
3. Follow metaspec quality criteria
4. Link research to requirements via `informed-by:` frontmatter
5. Re-run this prompt (0e) if new gaps identified
6. Proceed to 0f-identify-constraints when ready

**If skipping research:**
1. Document key assumptions in requirements
2. Proceed to 0f-identify-constraints
3. Plan validation approach for later
```

### Step 6: Guide Execution (If User Proceeds)

If user chooses to conduct research:

**For each activity:**

1. **Create artifact using template:**
   ```bash
   cp .livespec/templates/research/[type].md.template research/[category]/[name].md
   ```

2. **Guide through sections:**
   - Reference metaspec for quality criteria
   - Prompt for evidence, not assumptions
   - Ensure traceability (which requirements informed)

3. **Validate completeness:**
   - Check against metaspec essential elements
   - Verify links to requirements
   - Confirm evidence-based (quotes, observations, data)

4. **Update requirements:**
   - Add `informed-by:` frontmatter to relevant requirements
   - Refine requirements based on research findings
   - Document how research shaped requirements

### Step 7: Iterate as Needed

**Support multiple passes through this prompt:**
- Initial evaluation (start of Phase 0)
- After first research round (what did we learn? what's still unclear?)
- Before Phase 1 (are we ready to design?)
- During Phase 1 if gaps emerge (discovered unknowns)

**Each iteration:**
- Check what's been completed
- Identify new gaps
- Adjust priorities based on learnings
- Maintain focus on value (not completionism)

## Example Scenarios

### Scenario 1: E-Commerce Checkout

**Project Type**: User-facing application
**Complexity**: Medium (integration with payment providers)

**Recommendations:**
- **HIGH**: User Insights (checkout friction study) - 2 days
  - Why: Checkout is critical conversion point
  - Informs: simplified-checkout.spec.md, guest-checkout.spec.md
- **HIGH**: UX Flow (checkout process) - 4 hours
  - Why: Multiple paths (guest, registered, errors)
  - Informs: checkout-flow.spec.md
- **MEDIUM**: Personas (shopper types) - 3 hours
  - Why: Helps prioritize features for different user types
  - Informs: multiple feature requirements

### Scenario 2: Developer CLI Tool

**Project Type**: Developer platform
**Complexity**: Low (standard CLI patterns)

**Recommendations:**
- **MEDIUM**: Developer Personas (experience levels) - 2 hours
  - Why: Helps balance simplicity vs power
  - Informs: command-structure.spec.md, help-system.spec.md
- **LOW**: User Insights (pain points with existing tools) - 1 day
  - Why: Nice to have, but can infer from competitive analysis
  - Informs: various feature requirements

**Note**: Likely can skip research entirely and proceed to Phase 1.

### Scenario 3: Internal Governance System

**Project Type**: Governance/internal tool
**Complexity**: High (process complexity, stakeholder alignment)

**Recommendations:**
- **HIGH**: Stakeholder Insights (requirements clarity) - 3 days
  - Why: Requirements volatility high, alignment critical
  - Informs: policy-enforcement.spec.md, audit-trail.spec.md
- **HIGH**: Workflow Journeys (governance processes) - 1 day
  - Why: Complex multi-step processes across departments
  - Informs: workflow.spec.md, approval-flow.spec.md
- **MEDIUM**: User Personas (governance roles) - 3 hours
  - Why: Different permissions and responsibilities
  - Informs: access-control.spec.md

## Exit Criteria

Before proceeding to 0f (identify constraints):

- [ ] Project type classified
- [ ] Existing research reviewed
- [ ] Research gaps identified (or determined none needed)
- [ ] Recommendations presented with priorities
- [ ] User made informed decision (proceed with research / skip / partial)
- [ ] If research conducted: artifacts created, quality validated, requirements updated
- [ ] If research skipped: assumptions documented, validation plan noted

## Quality Checks

**Avoid these anti-patterns:**
- ❌ Forcing research on non-user-facing projects
- ❌ Suggesting research "just to be thorough"
- ❌ Creating rigid requirements when flexibility appropriate
- ❌ Making research feel like compliance exercise
- ❌ Blocking progress when skipping is reasonable

**Ensure these patterns:**
- ✅ Clear value proposition for each suggestion
- ✅ Honest about what can be skipped
- ✅ Realistic effort estimates
- ✅ Evidence-based research (not theater)
- ✅ Seamless flow into Phase 1 (design)

## Next Step

Once research evaluation is complete (research conducted OR decision to skip):

Proceed to `0f-identify-constraints.md`

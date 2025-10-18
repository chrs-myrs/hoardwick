# Hoardwick Specification Architecture

This document visualizes the relationships between all specifications in the Hoardwick project.

## Specification Graph

```mermaid
graph LR
    %% Requirements Layer
    outcomes["specs/1-requirements/strategic/<br/>outcomes.spec.md"]
    constraints["specs/1-requirements/strategic/<br/>constraints.spec.md"]

    %% Strategy Layer
    architecture["specs/2-strategy/<br/>architecture.spec.md"]

    %% Behaviors Layer
    scanner["specs/3-behaviors/<br/>scanner.spec.md"]
    preferences["specs/3-behaviors/<br/>preference-learning.spec.md"]
    vhdx["specs/3-behaviors/<br/>vhdx-management.spec.md"]

    %% Workspace Layer
    constitution["specs/workspace/<br/>constitution.spec.md"]
    patterns["specs/workspace/<br/>patterns.spec.md"]
    workflows["specs/workspace/<br/>workflows.spec.md"]

    %% Derivation relationships (derives-from)
    outcomes ==derives==> architecture
    constraints ==derives==> architecture

    %% Satisfaction relationships (satisfies)
    scanner ==satisfies==> outcomes

    %% Guidance relationships (guided-by)
    architecture --guides--> scanner
    architecture --guides--> preferences
    architecture --guides--> vhdx

    %% Constraint relationships (constrained-by)
    preferences -.constrained.-> patterns
    vhdx -.constrained.-> workflows

    %% Styling
    classDef requirement fill:#fff4e6,stroke:#ff9800,stroke-width:2px
    classDef strategy fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef behavior fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    classDef workspace fill:#fff3e0,stroke:#ff9800,stroke-width:2px

    class outcomes,constraints requirement
    class architecture strategy
    class scanner,preferences,vhdx behavior
    class constitution,patterns,workflows workspace
```

## Legend

- **Bold lines (==derives==>)**: Derivation - spec derives requirements from other specs
- **Solid lines (--guides-->)**: Guidance - spec guides implementation of other specs
- **Dotted constraint lines (-.constrained.->)**: Constraints - spec is constrained by patterns/workflows
- **Bold satisfaction lines (==satisfies==>)**: Satisfaction - spec satisfies requirements from outcomes

## Specification Layers

### 1. Requirements
- **outcomes.spec.md**: What the system must achieve
- **constraints.spec.md**: Non-negotiable limitations and safety requirements

### 2. Strategy
- **architecture.spec.md**: Technical approach and core components

### 3. Behaviors
- **scanner.spec.md**: Storage scanning behavior (resumable, aggregating, staleness detection)
- **preference-learning.spec.md**: User preference classification and learning
- **vhdx-management.spec.md**: VHDX overhead understanding and compaction workflows

### 4. Workspace
- **constitution.spec.md**: Core development principles and practices
- **patterns.spec.md**: Coding patterns, naming conventions, data storage patterns
- **workflows.spec.md**: Development workflows (feature dev, cleanup, VHDX compaction, git setup)

## Key Relationships

1. **architecture** derives requirements from **outcomes** and **constraints**
2. **scanner** satisfies the scanning requirements defined in **outcomes**
3. All three behaviors (**scanner**, **preferences**, **vhdx**) are guided by **architecture**
4. **preferences** follows coding patterns from **patterns**
5. **vhdx** follows workflows defined in **workflows**

## Specification Health

✅ All behavior specs linked to architecture
✅ Requirements flow clearly from outcomes → architecture → behaviors
✅ Workspace specs provide cross-cutting development guidance
✅ Clear derivation chain from requirements through strategy to implementation

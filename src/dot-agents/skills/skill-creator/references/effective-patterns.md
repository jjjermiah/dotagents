# Effective Skill Patterns

Proven patterns and anti-patterns for skill design.

## Pattern: Domain-Specific References

**When**: Skill covers multiple sub-domains, each substantial (>100 lines), users typically need one at a time.

**Structure**:
```
testing-skill/
├── SKILL.md (core + overview)
└── references/
    ├── advanced.md
    ├── bdd.md
    ├── fixtures.md
    └── snapshots.md
```

Agent reads only relevant reference per task context.

## Pattern: Checklist References

**When**: Systematic evaluation needed, quality depends on thoroughness, items vary by context.

**Structure**:
```
code-reviewer/
├── SKILL.md (workflow + when to use checklists)
└── references/
    └── checklists.md (API, DB, frontend checklists)
```

SKILL.md describes workflow. Agent consults checklists during evaluation.

## Pattern: Example-Driven Output

**When**: Output format/quality critical, showing more effective than describing.

**Structure**:
```
code-reviewer/
├── SKILL.md (output structure)
└── references/
    └── examples.md (sample reviews with format)
```

SKILL.md describes structure. Examples show proper execution.

## Pattern: Persuasion-Enforced Skills

**When**: Skill enforces discipline (TDD, verification, safety-critical practices) or guides important decisions.

**Structure**:
```markdown
## Core Requirements (Authority)

YOU MUST [action]. Never [anti-pattern]. No exceptions.

## Implementation (Commitment)

When [trigger], IMMEDIATELY [action].

Track with: TodoWrite checklist

## Why This Matters (Social Proof)

[X without Y = failure]. Every time.
```

**Key elements**:
- **Authority**: Imperative "YOU MUST", absolute language
- **Commitment**: Explicit triggers + required actions
- **Social Proof**: Document failure modes, universal patterns
- **Unity**: Collaborative "we" language for non-hierarchical skills
- **Ethical boundaries**: No fear/shame/guilt, no false urgency

See [persuasion-principles.md](persuasion-principles.md) for principle definitions, combinations by skill type, and research citations.

## Pattern: Script-Heavy Skills

**When**: Same code rewritten repeatedly, deterministic operation, reliability critical.

**Structure**:
```
pdf-editor/
├── SKILL.md (when to use scripts)
└── scripts/
    ├── rotate_pdf.py
    ├── merge_pdfs.py
    └── extract_text.py
```

Token-efficient, tested, executable without context loading.

## Pattern: Progressive Workflow

**When**: Core workflow common, advanced features occasional.

**Structure**:
```markdown
# SKILL.md
## Quick start
[core example]

## Advanced
- **Forms**: See [FORMS.md](FORMS.md)
- **API**: See [REFERENCE.md](REFERENCE.md)
```

Common case in SKILL.md, advanced in references.

## Anti-Pattern: Duplicate "When to Use"

**Wrong**:
```yaml
description: Guide for skills
---
## When to use me
Use when creating skills...
```

**Right**:
```yaml
description: |
  Guide for creating and validating skills. Use when creating skills, validating structure, or packaging—e.g., "create skill", "validate skill".
---
## Core Principles
...
```

Body loads AFTER triggering. Trigger info must be in description.

## Anti-Pattern: Auxiliary Docs

**Wrong**:
```
skill/
├── SKILL.md
├── README.md
├── INSTALLATION.md
└── QUICK_REFERENCE.md
```

**Right**:
```
skill/
├── SKILL.md (all essential content)
└── references/ (optional details)
```

Agent only reads SKILL.md and explicit references.

## Anti-Pattern: Vague Description

**Wrong**:
```yaml
description: Helps with code quality
```

**Right**:
```yaml
description: |
  Structured code review against plans and standards. Use when validating completed features before merge—e.g., "finished step X", "ready for review", "check quality and tests".
```

Include specific capabilities, "Use when" contexts, and examples.

## Anti-Pattern: Bloated SKILL.md

**Signs**: >500 lines, long example lists, complete API reference, copy-pasted external docs.

**Fix**: Move examples to references/examples.md, API to references/api.md, link external docs.

## Anti-Pattern: Broken Progressive Disclosure

**Wrong**:
```markdown
# SKILL.md
Follow steps: [workflow]
# (references exist but unmentioned)
```

**Right**:
```markdown
# SKILL.md
Follow steps: [workflow]

For advanced patterns: [references/advanced.md](references/advanced.md)
For fixtures: [references/fixtures.md](references/fixtures.md)
```

Explicitly link with usage guidance.

## Pattern Selection

**Scripts**: Deterministic, repetitive, identical rewrites, reliability critical.

**Domain References**: Multiple domains, substantial content per domain, one domain per task.

**Checklists**: Systematic evaluation, consistency critical, context-varying items.

**Examples**: Output format critical, showing beats describing, style/tone matters.

## Combining Patterns

**Code Reviewer** (Checklist + Examples):
```
code-reviewer/
├── SKILL.md (workflow)
└── references/
    ├── checklists.md (what to check)
    └── examples.md (how to present)
```

**Testing** (Domain + Examples):
```
testing/
├── SKILL.md (core)
└── references/
    ├── unit-testing.md
    ├── integration-testing.md
    └── examples.md
```

**Data Processing** (Scripts + References):
```
data-processing/
├── SKILL.md (workflow + scripts)
├── scripts/
│   ├── clean_data.py
│   └── validate_schema.py
└── references/
    └── schemas.md
```

Choose patterns based on need, not applying all to every skill.

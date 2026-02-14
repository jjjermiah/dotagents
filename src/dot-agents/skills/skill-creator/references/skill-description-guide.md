# Skill Description Guide

The `description` field determines when the skill loads. It's always in context, so it must be concise yet comprehensive.

## Template

```yaml
description: |
  <What it does>. Use when <context>, <context>, or <context>—e.g., "<example>", "<example>".
```

**Components:**

1. **Capability statement** (1 sentence) — what the skill enables
2. **"Use when" clause** (2-4 contexts) — semantic conditions, not keywords
3. **Examples** (1-3, optional) — concrete queries/tasks after em-dash

**Constraints:**

- 50-120 words total
- No separate "Triggers:" or "Keywords:" sections
- No disambiguation ("use X instead") — multiple skills loading is fine
- Third person voice (description is injected into system prompt)

## Context Types

Mix these for best coverage:

| Type              | Example                                                  |
| ----------------- | -------------------------------------------------------- |
| Task-based        | "when writing tests", "when reviewing code"              |
| Artifact-based    | "when working with R packages", "when editing pixi.toml" |
| Environment-based | "when pixi.lock detected", "when in a Python project"    |
| Intent-based      | "when selecting libraries", "when debugging errors"      |

## Examples

### Good

```yaml
description: |
  Pytest-first Python testing practices. Use when writing or reviewing tests, 
  designing fixtures and mocks, or setting up coverage—e.g., "add tests", 
  "fixture design", "fakes vs mocks".
```

- Clear capability
- Multiple task contexts
- Concrete examples

```yaml
description: |
  Base pixi package manager for environment setup. Use when initializing projects, 
  adding packages, or managing environments—e.g., "pixi add numpy", "setup pixi". 
  Also use when pixi.lock detected.
```

- Capability + contexts + examples
- Environment-based trigger

### Bad

```yaml
description: Helps with Python testing.
```

- Too vague — when would you NOT use this?

```yaml
description: |
  Triggers: "pytest", "test", "fixture", "mock", "coverage"
```

- Keyword list without semantic context
- Misses paraphrases ("write tests", "add unit tests")

```yaml
description: |
  Python testing skill. Use for pytest. For unittest, use another skill.
  Keywords: pytest, fixture, mock. Do not use for integration tests.
```

- Unnecessary disambiguation
- Mixed formats
- Restrictive ("do not use")

## Writing Process

1. **List 5 ways users request this** — tasks, questions, contexts
2. **Extract semantic patterns** — what ties them together?
3. **Write capability statement** — one sentence, what it enables
4. **Add "Use when" contexts** — 2-4 conditions covering the patterns
5. **Add examples** — 1-3 concrete queries (optional but helpful)

## Validation

Ask yourself:

1. Reading only the description, is it clear when to use this skill?
2. Would an LLM select this for the 5 request types you listed?
3. Is it under 120 words?

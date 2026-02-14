---
name: python-code-quality
description: Python code quality with Ruff linting/formatting and ty type checking. Use when configuring Ruff rules, setting up ty type checking, writing pyproject.toml quality config, creating pixi quality tasks, enforcing type annotations, or fixing lint errors—e.g., "set up ruff and ty", "configure Python linting", "add type checking to project", "fix ruff violations".
---

# Python Code Quality

## Purpose

Enforce consistent Python code quality using **Ruff** (linting + formatting) and
**ty** (type checking) from Astral. This skill defines the standard configuration,
rule selection, and pixi task integration for all Python projects.

## CRITICAL: Use Context7 for Tool APIs

**YOU MUST query Context7 before writing Ruff or ty configuration.** These tools
evolve rapidly. Stale knowledge produces invalid config.

```
Context7 slugs:
  Ruff docs:  /websites/astral_sh_ruff
  ty docs:    /websites/astral_sh_ty
```

Query Context7 for any non-trivial config question. No exceptions.

## Tool Overview

| Tool          | Role                          | Config Files                                  |
| ------------- | ----------------------------- | --------------------------------------------- |
| `ruff check`  | Linting (800+ rules)          | `pyproject.toml` `[tool.ruff]` or `ruff.toml` |
| `ruff format` | Formatting (Black-compatible) | Same as above                                 |
| `ty check`    | Type checking (Rust-based)    | `pyproject.toml` `[tool.ty]` or `ty.toml`     |

Both tools are installed via pixi/conda: `ruff = "*"` and `ty = "*"`.

## Configuration Strategy

### Where to Put Config

| Project Layout                | Ruff Config                                | ty Config                                |
| ----------------------------- | ------------------------------------------ | ---------------------------------------- |
| Single package                | `pyproject.toml` `[tool.ruff]`             | `pyproject.toml` `[tool.ty]`             |
| Workspace (monorepo)          | Root `ruff.toml` shared                    | Per-package `pyproject.toml` `[tool.ty]` |
| Workspace (per-package rules) | Per-package `pyproject.toml` `[tool.ruff]` | Per-package `pyproject.toml` `[tool.ty]` |

Ruff auto-discovers the closest config file per-file. ty must be pointed at
specific directories or uses the config in its working directory.

### Standard Ruff Config (pyproject.toml)

This is the baseline for new projects. Adapt to your needs.

```toml
[tool.ruff]
target-version = "py313"    # Match your requires-python
line-length = 88
src = ["src"]

[tool.ruff.lint]
select = [
    # === Errors & Core ===
    "E",    # pycodestyle errors
    "F",    # Pyflakes (undefined names, unused imports)
    "W",    # pycodestyle warnings
    # === Imports ===
    "I",    # isort (import sorting)
    # === Modernization ===
    "UP",   # pyupgrade (modern Python idioms)
    # === Bug Detection ===
    "B",    # flake8-bugbear (common bugs)
    # === Style & Simplification ===
    "N",    # pep8-naming conventions
    "SIM",  # flake8-simplify (reduce complexity)
    "C4",   # flake8-comprehensions (better comprehensions)
]
ignore = ["T201"]           # Allow print() — remove for libraries

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["ALL"]        # Relax all rules in tests

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### Extended Ruff Config (Stricter)

For projects requiring annotations, no print statements, and stricter hygiene:

```toml
[tool.ruff.lint]
select = [
    # --- Core (always enabled) ---
    "E", "F", "W", "I", "UP", "B", "N", "SIM", "C4",
    # --- Annotations ---
    "ANN",  # flake8-annotations (require type hints)
    # --- Import hygiene ---
    "ICN",  # flake8-import-conventions
    "TID",  # flake8-tidy-imports
    # --- Code quality ---
    "A",    # flake8-builtins (no shadowing builtins)
    "T10",  # flake8-debugger (no breakpoints)
    "T20",  # flake8-print (no print statements)
    "EM",   # flake8-errmsg (clear error messages)
    # --- Standards ---
    "PTH",  # flake8-use-pathlib (prefer pathlib)
    "PL",   # Pylint rules
]
```

### Standard ty Config (pyproject.toml)

```toml
[tool.ty.environment]
python-version = "3.13"     # Match your requires-python
python-platform = "linux"   # Or "darwin", "all" for cross-platform

[tool.ty.src]
include = ["src"]           # Where your source code lives
```

#### ty Rule Overrides

ty rules have three severity levels: `error`, `warn`, `ignore`.

```toml
[tool.ty.rules]
# Promote to errors (non-zero exit on violation)
possibly-missing-import = "error"
possibly-missing-attribute = "error"

# Demote noisy rules to warnings
possibly-unresolved-reference = "warn"

# Disable rules that produce false positives
division-by-zero = "ignore"
```

#### ty Overrides for Test Files

```toml
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"
```

#### Suppressing Unresolvable Imports

```toml
[tool.ty.analysis]
allowed-unresolved-imports = ["some_optional_dep.**"]
```

### Standalone ruff.toml (Workspace Root)

For monorepos with a single shared ruff config:

```toml
cache-dir = ".cache/ruff/.ruff-cache"
line-length = 88
include = ["packages/**/*.py", "libs/**/*.py"]
extend-exclude = ["dev/**"]
preview = true              # Enable preview rules (opt-in)

[format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true
docstring-code-line-length = 88

[lint]
select = ["E", "F", "W", "I", "UP", "B", "N", "SIM", "C4", "ANN"]

[lint.per-file-ignores]
"*.ipynb" = ["A", "ANN", "T20"]    # Relax for notebooks
"tests/**" = ["ALL"]
```

## Pixi Integration

### Quality Feature Pattern

Define a `quality` feature in `pixi.toml` with Ruff and ty:

```toml
[feature.quality.dependencies]
ruff = "*"
ty = "*"

[feature.quality.tasks]
lint = {cmd = "ruff check src/", description = "Run ruff linter"}
lint-fix = {cmd = "ruff check --fix src/", description = "Lint with auto-fix"}
format = {cmd = "ruff format src/", description = "Format code"}
format-check = {cmd = "ruff format --check src/", description = "Check formatting"}
typecheck = {cmd = "ty check src/", description = "Run ty type checker"}
qc = {depends-on = ["lint", "format-check", "typecheck"], description = "All quality checks"}
```

Include the feature in your environment:

```toml
[environments]
default = {features = ["quality", ...]}
```

### Workspace Quality Tasks

For monorepos, run tools on the correct directories:

```toml
[feature.quality.tasks]
# Ruff auto-discovers closest pyproject.toml per-file
lint = {cmd = "ruff check libs/", description = "Lint all packages"}
lint-fix = {cmd = "ruff check --fix libs/", description = "Lint with auto-fix"}
format = {cmd = "ruff format libs/", description = "Format all packages"}
format-check = {cmd = "ruff format --check libs/", description = "Check formatting"}
# ty must be told which packages to check
typecheck = {cmd = "ty check libs/pkg_a libs/pkg_b", description = "Type check all"}
qc = {depends-on = ["lint", "format-check", "typecheck"], description = "All QC"}
```

## Fixing Violations

### Ruff Auto-Fix

```bash
ruff check --fix <path>     # Apply safe fixes
ruff check --fix --unsafe-fixes <path>  # Include unsafe fixes (review diff!)
```

### Inline Suppression

```python
x = eval("1+1")  # noqa: S307 — required for dynamic config loading

# ty suppression
result = dynamic_call()  # type: ignore[possibly-unresolved-reference]
```

**YOU MUST** add a comment explaining WHY when suppressing a rule inline.
Unexplained `noqa` comments are technical debt.

## YOU MUST

- Configure `target-version` to match `requires-python` in your project
- Set `src = ["src"]` in Ruff config so import sorting works correctly
- Always run `ruff format` BEFORE `ruff check` (formatting can introduce lint issues)
- Use `per-file-ignores` for tests, notebooks—never disable rules globally
  when only certain files need relaxation
- Query Context7 before writing non-trivial Ruff/ty configuration
- Include a `qc` task in pixi that runs lint + format-check + typecheck

## NEVER

- Disable `F` (Pyflakes) or `E4/E7/E9` rules — these catch real bugs
- Use `select = ["ALL"]` without heavy `ignore` — too noisy, creates churn
- Suppress rules inline without explanation
- Skip type checking — ty is fast enough to run on every commit
- Mix `ruff.toml` and `pyproject.toml [tool.ruff]` in the same project
  (Ruff uses the first config it finds; mixing causes silent ignoring)

## Cross-Reference Skills

- **python-testing**: Test files should use relaxed lint rules via `per-file-ignores`
- **python-production-libs**: Library recommendations include `ruff` and `ty` in dev deps
- **pixi-tasks**: Task dependency chains for `qc` task orchestration
- **script-writer**: Scripts should follow the same lint rules as project code

## References (Load on Demand)

- **[references/ruff-rules.md](references/ruff-rules.md)** — Load when selecting
  which Ruff rule sets to enable, understanding rule prefixes, or choosing
  between standard vs. strict configs
- **[references/ty-config.md](references/ty-config.md)** — Load when configuring
  ty environment settings, rule overrides, or workspace type checking

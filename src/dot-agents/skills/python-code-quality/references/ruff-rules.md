# Ruff Rule Sets Reference

Quick reference for selecting Ruff lint rule sets. Ruff supports 800+ rules
organized by prefix. Use `select` to enable, `ignore` to exclude specific codes.

## Rule Selection Mechanics

```toml
[tool.ruff.lint]
select = ["E", "F"]              # Base set
extend-select = ["UP", "B"]     # Add to inherited config
ignore = ["E501"]                # Exclude specific rules
```

- `select` replaces the default rule set entirely
- `extend-select` adds to the current set (useful with inherited configs)
- `ignore` removes specific rules from the resolved set
- CLI flags override config; current config overrides inherited config

## Recommended Rule Sets by Tier

### Tier 1: Always Enable (Bug Detection)

| Prefix | Source         | What It Catches                                   |
|--------|----------------|---------------------------------------------------|
| `F`    | Pyflakes       | Undefined names, unused imports, redefined unused |
| `E4`   | pycodestyle    | Import errors                                     |
| `E7`   | pycodestyle    | Statement errors                                  |
| `E9`   | pycodestyle    | Runtime/syntax errors                             |
| `B`    | flake8-bugbear | Common bugs (mutable defaults, assert, except)    |
| `W`    | pycodestyle    | Warnings (trailing whitespace, blank lines)       |

### Tier 2: Standard Quality

| Prefix | Source                | What It Catches                                |
|--------|-----------------------|------------------------------------------------|
| `I`    | isort                 | Import sorting and grouping                    |
| `N`    | pep8-naming           | Naming conventions (class, function, variable) |
| `UP`   | pyupgrade             | Deprecated syntax, modernize to target-version |
| `SIM`  | flake8-simplify       | Unnecessarily complex code                     |
| `C4`   | flake8-comprehensions | Suboptimal list/dict/set comprehensions        |

### Tier 3: Strict Hygiene

| Prefix | Source                    | What It Catches                                                            |
|--------|---------------------------|----------------------------------------------------------------------------|
| `ANN`  | flake8-annotations        | Missing type annotations on functions                                      |
| `A`    | flake8-builtins           | Shadowing Python builtins                                                  |
| `T10`  | flake8-debugger           | Leftover breakpoint() / pdb calls                                          |
| `T20`  | flake8-print              | Print statements (use logging instead)                                     |
| `EM`   | flake8-errmsg             | Poor error message patterns                                                |
| `PTH`  | flake8-use-pathlib        | os.path usage (prefer pathlib)                                             |
| `PL`   | Pylint                    | Broad pylint checks (PLR=refactor, PLC=convention, PLE=error, PLW=warning) |
| `ICN`  | flake8-import-conventions | Import alias conventions (np, pd, etc.)                                    |
| `TID`  | flake8-tidy-imports       | Banned imports, relative import rules                                      |

### Tier 4: Optional / Domain-Specific

| Prefix  | Source              | When to Use                                                   |
|---------|---------------------|---------------------------------------------------------------|
| `D`     | pydocstyle          | Enforce docstring conventions (set `convention = "google"`)   |
| `S`     | flake8-bandit       | Security checks (useful for web/API code)                     |
| `PT`    | flake8-pytest-style | Pytest idiom enforcement                                      |
| `RUF`   | Ruff-specific       | Ruff's own rules (mutable class/module defaults)              |
| `ERA`   | eradicate           | Detect commented-out code                                     |
| `PERF`  | perflint            | Performance anti-patterns                                     |
| `ASYNC` | flake8-async        | Async/await issues                                            |
| `FAST`  | FastAPI             | FastAPI-specific route issues                                 |

## Common Ignores

| Code      | Rule                    | Why Ignore                              |
|-----------|-------------------------|-----------------------------------------|
| `E501`    | Line too long           | Formatter handles this                  |
| `T201`    | Print found             | Acceptable in scripts/CLIs              |
| `ANN101`  | Missing type for self   | Removed (deprecated)                    |
| `ANN102`  | Missing type for cls    | Removed (deprecated)                    |
| `PLR0913` | Too many arguments      | Sometimes unavoidable in API clients    |
| `PLR0904` | Too many public methods | Sometimes unavoidable in facade classes |

## Per-File Ignores

Always use `per-file-ignores` instead of globally disabling rules:

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["ALL"]                    # Tests: full relaxation
"*.ipynb" = ["A", "ANN", "T20"]        # Notebooks: allow prints, no annotations
"__init__.py" = ["E402", "F401"]       # Init files: allow re-exports, late imports
"**/migrations/**" = ["ALL"]           # DB migrations: auto-generated
"scripts/**" = ["T20"]                 # Scripts: allow print()
```

## Preview Mode

```toml
preview = true    # Enable preview (unstable) rules
```

Preview rules are marked with `🧪` in Ruff docs. They may change between
versions. Use in projects where you control the Ruff version pin.

## Formatter Settings

```toml
[tool.ruff.format]
quote-style = "double"              # Match Black default
indent-style = "space"
skip-magic-trailing-comma = false   # Respect trailing commas
line-ending = "auto"
docstring-code-format = true        # Format code blocks in docstrings
docstring-code-line-length = 88     # Match line-length
```

## Pylint Sub-Categories

When using `PL`, you get all subcategories. Fine-tune with:

```toml
[tool.ruff.lint]
select = ["PL"]

[tool.ruff.lint.pylint]
max-args = 6                     # Default: 5
max-branches = 13                # Default: 12
max-returns = 8                  # Default: 6
max-statements = 55              # Default: 50
allow-dunder-method-names = [    # Custom dunders that won't trigger
    "__rich_console__",
    "__rich_repr__",
]
```

## Context7 Queries

When you need details on specific rules:

```text
libraryId: /websites/astral_sh_ruff
Queries:
  "ruff flake8-bugbear B rules list"
  "ruff per-file-ignores configuration"
  "ruff isort settings section-order"
  "ruff pylint settings max-args"
  "ruff preview rules list"
```

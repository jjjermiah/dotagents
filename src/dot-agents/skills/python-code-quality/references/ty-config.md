# ty Configuration Reference

ty is Astral's Python type checker written in Rust. Fast, strict, and
designed to work alongside Ruff.

## Config File Locations

| File | Format |
|------|--------|
| `pyproject.toml` | `[tool.ty]` prefix |
| `ty.toml` | No prefix (root-level keys) |

ty searches for config in the current directory and parent directories.
If a `pyproject.toml` has no `[tool.ty]` table, it is skipped and the search
continues upward.

## Environment Configuration

```toml
[tool.ty.environment]
python-version = "3.13"         # Must match requires-python
python-platform = "linux"       # "darwin", "win32", "all", or "linux"
root = ["./src"]                # First-party module search paths
extra-paths = ["./stubs"]       # Additional type stub paths
python = ".venv"                # Path to venv (usually auto-detected)
```

### Platform Notes

- Set `python-platform = "linux"` for server/container code
- Set `python-platform = "all"` for cross-platform libraries
- ty defaults to the current platform if not specified

### Root (Source Discovery)

ty auto-detects `./src` if it exists and is not a package (no `__init__.py`).
Set `root` explicitly for non-standard layouts:

```toml
[tool.ty.environment]
root = ["./src", "./lib"]       # Priority order (first wins)
```

## Source Inclusion/Exclusion

```toml
[tool.ty.src]
include = ["src", "tests"]       # Only check these paths
exclude = [
    "generated/**",
    "*.proto",
    "tests/fixtures/**",
    "!tests/fixtures/important.py"   # Re-include specific file
]
```

Patterns follow `.gitignore`-like syntax. `exclude` takes precedence over `include`.

## Rule Configuration

### Severity Levels

| Level | Behavior |
|-------|----------|
| `error` | Reported as error, exit code 1 |
| `warn` | Reported as warning, exit code 0 (default) |
| `ignore` | Rule disabled entirely |

### Setting Rule Severity

```toml
[tool.ty.rules]
# Set all rules to a baseline
all = "warn"

# Override specific rules
possibly-missing-import = "error"
possibly-missing-attribute = "error"
possibly-unresolved-reference = "warn"
division-by-zero = "ignore"
redundant-cast = "ignore"
unused-ignore-comment = "warn"
```

### Common ty Rules

| Rule | Default | Description |
|------|---------|-------------|
| `possibly-unresolved-reference` | warn | Name might not be defined |
| `possibly-missing-import` | error | Module import may be missing |
| `possibly-missing-attribute` | error | Attribute may not exist on type |
| `division-by-zero` | warn | Division by literal zero |
| `redundant-cast` | ignore | Unnecessary type cast |
| `unused-ignore-comment` | ignore | Suppression comment not needed |
| `index-out-of-bounds` | warn | Index may be out of range |

## Overrides (Per-File Rules)

Apply different rules to specific file patterns:

```toml
[[tool.ty.overrides]]
include = ["tests/**", "**/test_*.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"

[[tool.ty.overrides]]
include = ["generated/**"]
exclude = ["generated/important.py"]

[tool.ty.overrides.rules]
possibly-unresolved-reference = "ignore"
```

Multiple overrides can match the same file. Later overrides take precedence.

## Analysis Settings

### Suppressing Unresolvable Imports

For optional or dynamic dependencies:

```toml
[tool.ty.analysis]
allowed-unresolved-imports = [
    "some_optional_dep.**",
    "test.**",
    "!test.foo",              # But NOT this one
]
```

Glob syntax:
- `*` matches any characters except `.`
- `**` matches any number of module components
- `!` prefix negates (later entries take precedence)

### Ignore Comment Handling

```toml
[tool.ty.analysis]
# Only accept ty-specific ignore comments (not mypy's `type: ignore`)
respect-type-ignore-comments = false
```

## Terminal / Output

```toml
[tool.ty.terminal]
output-format = "full"          # "full", "concise", "github", "gitlab", "junit"
error-on-warning = true         # Exit code 1 for warnings too
```

Use `output-format = "github"` in CI for GitHub annotations.
Use `output-format = "gitlab"` for GitLab CI code quality reports.

## CLI Usage

```bash
ty check src/                           # Check specific directory
ty check --warn all                     # All rules as warnings
ty check --error all                    # All rules as errors
ty check --ignore division-by-zero      # Disable specific rule
ty check --error-on-warning             # Strict mode for CI
```

## Workspace Patterns

ty does not have native workspace support. For monorepos:

```toml
# pixi.toml — run ty per-package
[feature.quality.tasks]
typecheck = {
    cmd = "ty check libs/pkg_a libs/pkg_b libs/pkg_c",
    description = "Type check all packages"
}
```

Each package should have its own `pyproject.toml` with `[tool.ty]` for
package-specific settings (python-version, src paths, rule overrides).

## Context7 Queries

```text
libraryId: /websites/astral_sh_ty
Queries:
  "ty configuration pyproject.toml settings"
  "ty rules list all diagnostics"
  "ty overrides per-file configuration"
  "ty analysis allowed-unresolved-imports"
  "ty environment python-version platform"
```

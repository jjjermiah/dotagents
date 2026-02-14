---
name: pixi-expert
description: Comprehensive pixi package manager skill for all pixi operations from beginner to advanced. Use for initializing projects, managing dependencies, configuring environments, multi-environment setups, workspace composition, system requirements (CUDA/glibc), task workflows, CI/CD integration, or any pixi.toml/pyproject.toml configuration—e.g., "pixi init", "pixi add numpy", "setup multi-environment project", "configure CUDA", "monorepo workspace", "pixi.lock issues", "Docker with pixi", "GitHub Actions pixi".
---

# Pixi Expert

## Purpose

Complete reference for pixi - the modern cross-platform package manager unifying conda and PyPI ecosystems. Covers everything from basic project setup to advanced multi-environment composition and workspace management.

## Core Concepts

When we work with pixi, we treat the project folder as a **workspace** with three key artifacts:

| Artifact                       | Purpose                                          | Git        |
| ------------------------------ | ------------------------------------------------ | ---------- |
| `pixi.toml` / `pyproject.toml` | Manifest with dependencies, tasks, configuration | **Commit** |
| `pixi.lock`                    | Reproducible lock file with exact versions       | **Commit** |
| `.pixi/`                       | Environment directory with installed packages    | **Ignore** |

```gitignore
# .gitignore
.pixi/
```

## Quick Start

### Project Setup

```bash
pixi init                      # New project (pixi.toml)
pixi init --format pyproject   # Python package (pyproject.toml)
```

### Dependencies

```bash
pixi add numpy pandas          # Add conda-forge packages
pixi add --pypi requests       # Add PyPI packages
pixi add --platform linux-64 gcc  # Platform-specific
pixi remove <package>          # Remove package
```

### Environment Management

```bash
pixi install                   # Sync environment with manifest
pixi install --frozen          # Use lock exactly (CI/production)
pixi install --locked          # Error if lock outdated
pixi install --all             # Install all environments

pixi shell                     # Enter environment shell
pixi shell -e dev              # Specific environment

pixi run <command>             # Run command in environment
pixi run -e dev pytest         # Run in specific environment
pixi run test                  # Run defined task
```

### Information

```bash
pixi info                      # Project/environment details
pixi list                      # Installed packages
pixi tree                      # Dependency tree
```

## Configuration

### pixi.toml (General Projects)

```toml
[workspace]
name = "my-project"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "win-64"]

[dependencies]
python = ">=3.10"
numpy = "*"

[pypi-dependencies]
requests = ">=2.28"

[tasks]
start = "python main.py"
test = "pytest"
```

### pyproject.toml (Python Packages)

```toml
[project]
name = "my-package"
version = "0.1.0"
dependencies = ["numpy", "pandas"]  # PyPI runtime deps

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "win-64"]

[tool.pixi.dependencies]
python = ">=3.10"

[tool.pixi.pypi-dependencies]
requests = "*"

[tool.pixi.tasks]
test = "pytest"
```

## Lock File Management

**YOU MUST always commit `pixi.lock`** for reproducibility. Every project without a committed lock file eventually encounters version conflicts and broken builds.

```bash
pixi install              # Updates lock if manifest changed
pixi install --frozen     # Install from lock without updating
pixi install --locked     # Error if lock doesn't match manifest
pixi update               # Update dependencies and regenerate lock
```

## Multi-Environment Composition

We define multiple environments using **features** and **solve groups** for reliable environment composition.

### Basic Pattern

```toml
[dependencies]
python = ">=3.10"
numpy = "*"

# Define features (named dependency sets)
[feature.test.dependencies]
pytest = "*"
pytest-cov = "*"

[feature.test.tasks]
test = "pytest -v --cov"

[feature.dev.dependencies]
ruff = "*"
mypy = "*"

[feature.dev.tasks]
lint = "ruff check ."

# Compose environments
[environments]
default = ["test"]                              # default + test
dev = { features = ["test", "dev"] }            # default + test + dev
prod = { features = [], solve-group = "main" }  # minimal only
test-prod = { features = ["test"], solve-group = "main" }
lint = { features = ["dev"], no-default-feature = true }
```

### Solve Groups

Keep dependency versions consistent across environments:

```toml
[environments]
dev = { features = ["test", "dev"], solve-group = "production" }
prod = { features = [], solve-group = "production" }
test-prod = { features = ["test"], solve-group = "production" }
```

### Platform-Specific Features

```toml
[feature.cuda]
platforms = ["linux-64"]
channels = ["nvidia", "conda-forge"]
dependencies = { cuda = "12.*" }

[feature.cuda.system-requirements]
cuda = "12"

[environments]
gpu = ["cuda"]
cpu = []
```

**Reference**: Load `references/environments.md` for detailed patterns.

## System Requirements

Virtual packages declare system capabilities for the solver.

| Virtual Package | Represents    | Typical Value |
| --------------- | ------------- | ------------- |
| `__linux`       | Linux kernel  | `>= 4.18`     |
| `__glibc`       | GNU C Library | `>= 2.28`     |
| `__cuda`        | CUDA driver   | `>= 12`       |
| `__osx`         | macOS version | `>= 13.0`     |

### CUDA Configuration

```toml
[system-requirements]
cuda = "12"  # Expected host CUDA driver API

[feature.gpu.dependencies]
pytorch = "*"
cuda-nvcc = "*"
```

### glibc / Linux Version

```toml
# For older systems (CentOS 7, RHEL 7)
[system-requirements]
linux = "3.10"
libc = { family = "glibc", version = "2.17" }
```

### Override via Environment Variables

```bash
export CONDA_OVERRIDE_CUDA=11.8
export CONDA_OVERRIDE_GLIBC=2.17
pixi install
```

**Reference**: Load `references/system-requirements.md` for detailed CUDA/glibc patterns.

## Workspace & Multi-Package Repos

Structure multiple packages in one repository:

```text
repo/
├── pixi.toml              # Optional root workspace manifest
└── packages/
    ├── core/
    │   └── pixi.toml      # Package manifest
    ├── app/
    │   └── pixi.toml
    └── utils/
        └── pixi.toml
```

### Package Manifest

```toml
[package]
name = "core"
version = "0.1.0"

[dependencies]
requests = "*"
utils = { path = "../utils" }  # Cross-package dependency

[tasks]
build = "python -m build"
test = "pytest"
```

### Commands

```bash
pixi run --manifest-path packages/core/pixi.toml test
pixi install --manifest-path packages/app/pixi.toml
```

**Reference**: Load `references/workspace.md` for monorepo patterns and build systems.

## Task Workflows

Define and run project tasks:

```toml
[tasks]
test = "pytest"
test-cov = "pytest --cov"
lint = { cmd = "ruff check .", depends-on = ["format"] }
format = "ruff format ."
dev = "uvicorn main:app --reload"
```

```bash
pixi run test          # Run task
pixi run lint          # Runs format first (dependency)
pixi run --list        # List available tasks
```

**Note**: For complex task orchestration (caching, inputs/outputs, parameterized tasks), load **pixi-tasks** skill in combination.

## Global Tools

Install CLI tools system-wide:

```bash
pixi global install ruff black mypy
pixi global install python=3.11
pixi global list
pixi global update
```

## Environment Variables

Pixi sets automatically:

| Variable                | Value                                 |
| ----------------------- | ------------------------------------- |
| `CONDA_PREFIX`          | Environment path (`.pixi/envs/<env>`) |
| `PIXI_PROJECT_ROOT`     | Project directory                     |
| `PIXI_ENVIRONMENT_NAME` | Current environment name              |

## Integration Patterns

### Docker

```dockerfile
FROM ghcr.io/prefix-dev/pixi:0.41.4 AS build

WORKDIR /app
COPY . .
RUN pixi install --locked -e prod
RUN pixi shell-hook -e prod -s bash > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
RUN echo 'exec "$@"' >> /app/entrypoint.sh

FROM ubuntu:24.04
WORKDIR /app
COPY --from=build /app/.pixi/envs/prod /app/.pixi/envs/prod
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
```

### GitHub Actions

```yaml
- uses: prefix-dev/setup-pixi@v0.9.2
  with:
    pixi-version: v0.41.4
    cache: true
- run: pixi run test
```

## Troubleshooting

```bash
pixi info                    # Check environment state
pixi list                    # See installed packages
pixi tree                    # View dependency tree
pixi install                 # Sync environment
rm -rf .pixi && pixi install # Clean reinstall
```

## References

Load these references when needed:

- **[references/environments.md](references/environments.md)**: Load when defining multi-environment setups, features, solve groups, or environment composition patterns.
- **[references/system-requirements.md](references/system-requirements.md)**: Load when configuring CUDA, glibc, virtual packages, or dealing with platform-specific dependencies and Docker GPU setups.
- **[references/workspace.md](references/workspace.md)**: Load when structuring monorepos, setting up multi-package workspaces, managing cross-package dependencies, or using build systems (pixi-build-python, pixi-build-cmake, rattler-build).

## Do / Don't

**Do**

- **YOU MUST commit `pixi.lock`** for reproducibility. Lock files not in version control = broken reproducibility. Every time.
- **Always use `pixi run`** over manual activation in scripts and CI. Scripts with manual activation fail in other environments without warning.
- **Always use solve groups** when defining multiple environments. Environments without solve groups inevitably diverge and create "works on my machine" bugs.
- Use Context7 or official pixi docs for exact syntax.
- Keep root workspace manifests minimal; details in member packages.

**Don't**

- **Never edit `pixi.lock` by hand**. Manual edits corrupt the lock and cause solver failures that waste hours to debug.
- Assume undocumented options exist (check docs first).
- Forget to update lock file after changing dependencies.
- Mix conda-forge and PyPI dependencies without considering compatibility.

## External Resources

- **Pixi Documentation**: https://pixi.sh/latest/
- **Multi-environments**: https://pixi.sh/latest/tutorials/multi_environment/
- **Manifest reference**: https://pixi.sh/latest/reference/pixi_manifest/

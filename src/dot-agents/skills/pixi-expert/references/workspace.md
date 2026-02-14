# Workspace Reference

Monorepo patterns, multi-package workspaces, cross-package dependencies.

## Contents

- [Workspace Structure](#workspace-structure)
- [Workspace Manifest (Root)](#workspace-manifest-root)
- [Package Manifest (Member)](#package-manifest-member)
- [Cross-Package Dependencies](#cross-package-dependencies)
- [Workspace Tasks](#workspace-tasks)
- [CLI Commands](#cli-commands)
- [Common Patterns](#common-patterns)
- [Build Systems](#build-systems)
- [Best Practices](#best-practices)

## Workspace Structure

```text
repo/
├── packages/
│   ├── core/
│   │   ├── pixi.toml
│   │   └── src/
│   └── app/
│       ├── pixi.toml
│       └── src/
```

## Workspace Manifest (Root)

Use a root manifest only when you need shared channels/platforms. Otherwise, keep manifests per package.

```toml
[workspace]
name = "my-repo"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64"]
```

## Package Manifest (Member)

```toml
[package]
name = "core"
version = "0.1.0"

[dependencies]
requests = "*"
utils = { path = "../utils" }

[tasks]
build = "python -m build"
test = "pytest"
```

## Cross-Package Dependencies

### Path Dependencies

```toml
# In packages/app/pixi.toml
[dependencies]
core = { path = "../core" }
utils = { path = "../utils" }
requests = "*"
```

### Build Dependencies

```toml
[package.build-dependencies]
core = { path = "../core" }

[build-dependencies]
cmake = "*"
```

## Workspace Tasks

Define tasks per package and call them with `--manifest-path`.

## CLI Commands

```bash
pixi run --manifest-path packages/core/pixi.toml test
pixi install --manifest-path packages/app/pixi.toml
```

## Common Patterns

### Library + CLI + Server

Run tasks per package with `--manifest-path`:

```bash
pixi run --manifest-path lib/pixi.toml build
pixi run --manifest-path cli/pixi.toml build
pixi run --manifest-path server/pixi.toml dev
```

### Multi-Language Project

```bash
pixi run --manifest-path rust-lib/pixi.toml build
pixi run --manifest-path python-bindings/pixi.toml build
pixi run --manifest-path js-client/pixi.toml build
```

## Build Systems

### Python Package

```toml
[package]
name = "my-package"
version = "0.1.0"

[package.build]
backend = { name = "pixi-build-python", version = "*" }
```

### C++ with CMake

```toml
[package]
name = "cpp-lib"
version = "0.1.0"

[package.build]
backend = { name = "pixi-build-cmake", version = "*" }

[build-dependencies]
cmake = "*"
ninja = "*"
```

### Rattler-Build (Advanced)

```toml
[package]
name = "advanced"
version = "0.1.0"

[package.build]
backend = { name = "pixi-build-rattler-build", version = "*" }
```

## Best Practices

1. **Keep root manifest minimal** - Details in member packages
2. **Use consistent versioning** - Match workspace version in members
3. **Use path dependencies** for internal packages
4. **Document dependencies** in comments

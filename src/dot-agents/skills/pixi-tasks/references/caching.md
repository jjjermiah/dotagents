# Caching Reference

Task result caching, input/output tracking, build optimization.

## Contents

- [How Caching Works](#how-caching-works)
- [Basic Patterns](#basic-patterns)
- [Glob Patterns](#glob-patterns)
- [External Data Caching](#external-data-caching)
- [Multi-Stage Builds](#multi-stage-builds)
- [CI/CD Optimization](#cicd-optimization)
- [Debugging](#debugging)
- [Common Issues](#common-issues)
- [Best Practices](#best-practices)

## How Caching Works

Pixi reuses task results when inputs, outputs, command, and environment packages are unchanged.

Cache invalidates when:

- Any input file changes
- Any output file missing
- Command string changes
- Environment packages change

## Basic Patterns

### Single Input

```toml
[tasks]
run = { cmd = "python main.py", inputs = ["main.py"] }
```

### Multiple Inputs

```toml
[tasks]
build = {
  cmd = "gcc main.c -o main",
  inputs = ["main.c", "header.h", "Makefile"]
}
```

### With Outputs

```toml
[tasks]
compile = {
  cmd = "make",
  inputs = ["src/*.c", "include/*.h"],
  outputs = ["build/app"]
}
```

## Glob Patterns

```toml
[tasks]
# Rust project
build = {
  cmd = "cargo build --release",
  inputs = ["src/**/*.rs", "Cargo.toml", "Cargo.lock"],
  outputs = ["target/release/myapp"]
}

# Python package
build = {
  cmd = "python -m build",
  inputs = ["src/**/*.py", "pyproject.toml"],
  outputs = ["dist/*.whl"]
}

# Documentation
docs = {
  cmd = "mkdocs build",
  inputs = ["docs/**/*.md", "mkdocs.yml"],
  outputs = ["site/index.html"]
}
```

## External Data Caching

```toml
[tasks]
# Download (cached by output existence)
download-model = {
  cmd = "curl -L -o model.pkl https://example.com/model.pkl",
  outputs = ["model.pkl"]
}

# Process (cached by inputs)
process = {
  cmd = "python process.py",
  inputs = ["model.pkl", "process.py"],
  outputs = ["results.json"],
  depends-on = ["download-model"]
}
```

## Multi-Stage Builds

```toml
[tasks]
download = {
  cmd = "curl -o data.csv ...",
  outputs = ["data.csv"]
}

process = {
  cmd = "python process.py",
  inputs = ["data.csv", "process.py"],
  outputs = ["processed.parquet"],
  depends-on = ["download"]
}

analyze = {
  cmd = "python analyze.py",
  inputs = ["processed.parquet", "analyze.py"],
  outputs = ["report.html"],
  depends-on = ["process"]
}
```

## CI/CD Optimization

### GitHub Actions

```yaml
- uses: prefix-dev/setup-pixi@v0.9.2
  with:
    cache: true

- run: pixi run build
```

### Docker Layer Caching

```dockerfile
# Stage 1: Dependencies (cached)
FROM ghcr.io/prefix-dev/pixi:0.41.4 AS deps
COPY pixi.toml pixi.lock ./
RUN pixi install --frozen

# Stage 2: Build (cached by inputs)
FROM deps AS build
COPY src/ ./src/
RUN pixi run build
```

## Debugging

Re-run tasks by changing inputs or command definitions.

## Common Issues

**Task runs every time**:

```toml
# Bad: node_modules changes frequently
build = { cmd = "npm run build", inputs = ["node_modules/"] }

# Good: track source files only
build = { cmd = "npm run build", inputs = ["src/", "package.json"] }
```

**Cache not invalidating**:

```toml
# Bad: missing header dependency
build = { cmd = "gcc main.c", inputs = ["main.c"] }

# Good: include all dependencies
build = { cmd = "gcc main.c", inputs = ["main.c", "header.h"] }
```

## Best Practices

1. **Be explicit about inputs** - List all files that affect output
2. **Always specify outputs** - Enables cache verification
3. **Use depends-on for ordering** - Not just input tracking
4. **Clean old outputs** when needed

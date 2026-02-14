# Cross-Environment Reference

Multi-version testing, environment matrices, cross-environment workflows.

## Contents

- [Basic Syntax](#basic-syntax)
- [Python Version Matrix](#python-version-matrix)
- [Backend Version Matrix](#backend-version-matrix)
- [Build/Test Separation](#buildtest-separation)
- [GPU/CPU Testing](#gpucpu-testing)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Basic Syntax

```toml
[tasks]
my-task = {
  depends-on = [
    { task = "test", environment = "py311" },
    { task = "test", environment = "py312" },
  ]
}
```

## Python Version Matrix

```toml
[dependencies]
pytest = "*"

[feature.py311.dependencies]
python = "3.11.*"

[feature.py312.dependencies]
python = "3.12.*"

[feature.py313.dependencies]
python = "3.13.*"

[environments]
py311 = ["py311"]
py312 = ["py312"]
py313 = ["py313"]

[tasks]
test = "pytest -v"

test-all = {
  depends-on = [
    { task = "test", environment = "py311" },
    { task = "test", environment = "py312" },
    { task = "test", environment = "py313" },
  ]
}
```

```bash
pixi run test-all         # All versions
pixi run -e py311 test    # Single version
```

## Backend Version Matrix

```toml
[feature.v1.dependencies]
fastapi = "0.100.*"

[feature.v2.dependencies]
fastapi = "0.110.*"

[environments]
v1 = { features = ["v1"], solve-group = "backend" }
v2 = { features = ["v2"], solve-group = "backend" }

[tasks]
test = "pytest"
test-matrix = {
  depends-on = [
    { task = "test", environment = "v1" },
    { task = "test", environment = "v2" },
  ]
}
```

## Build/Test Separation

```toml
[feature.build.dependencies]
rust = ">=1.70"

[feature.build.tasks]
compile = "cargo build --release"

[feature.test.dependencies]
pytest = "*"

[feature.test.tasks]
test-python = "pytest"

[environments]
build = ["build"]
test = ["test"]

[tasks]
ci = {
  depends-on = [
    { task = "compile", environment = "build" },
    { task = "test-python", environment = "test" },
  ]
}
```

## GPU/CPU Testing

```toml
[feature.gpu]
platforms = ["linux-64"]
system-requirements = { cuda = "12" }

[feature.cpu]
dependencies = { cpuonly = "*" }

[environments]
gpu = ["gpu"]
cpu = ["cpu"]

[tasks]
train = "python train.py"
train-all = {
  depends-on = [
    { task = "train", environment = "cpu" },
    { task = "train", environment = "gpu" },
  ]
}
```

## CI/CD Integration

### GitHub Actions Matrix

```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ["py311", "py312", "py313"]
    steps:
      - uses: prefix-dev/setup-pixi@v0.9.2
      - run: pixi run -e ${{ matrix.python }} test
```

### Parallel Testing

```toml
[tasks]
test-parallel = """
pixi run -e py311 test &
pixi run -e py312 test &
pixi run -e py313 test &
wait
"""
```

## Best Practices

1. **Use solve groups** for consistent versions:

```toml
[environments]
py311 = { features = ["py311"], solve-group = "test" }
py312 = { features = ["py312"], solve-group = "test" }
```

1. **Name environments clearly**: `py311`, `gpu`, `prod`

2. **Keep cross-env tasks simple** - Just delegation

3. **Document environment differences** in comments

## Troubleshooting

**Environment not found**:

```bash
pixi info  # List available environments
```

**Task not in environment**:

```toml
# Task must be in default or feature included in environment
[tasks]
test = "pytest"  # Available to all

[feature.special.tasks]
special-test = "pytest special/"  # Only in environments with "special" feature
```

**Execution order**:
Pixi runs dependencies based on the task graph; parallel execution is not documented.

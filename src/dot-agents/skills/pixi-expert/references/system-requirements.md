# System Requirements Reference

Virtual packages, CUDA, glibc, and system compatibility.

## Contents

- [Virtual Packages](#virtual-packages)
- [Default Requirements](#default-requirements)
- [CUDA Configuration](#cuda-configuration)
- [glibc Configuration](#glibc-configuration)
- [Environment Variable Overrides](#environment-variable-overrides)
- [Feature-Specific Requirements](#feature-specific-requirements)
- [Platform-Specific Dependencies](#platform-specific-dependencies)
- [Common Errors](#common-errors)
- [Docker Integration](#docker-integration)

## Virtual Packages

System capability markers used by the solver:

| Virtual Package | Represents    | Example           |
| --------------- | ------------- | ----------------- |
| `__linux`       | Linux kernel  | `__linux >= 4.18` |
| `__glibc`       | GNU C Library | `__glibc >= 2.28` |
| `__cuda`        | CUDA driver   | `__cuda >= 12`    |
| `__osx`         | macOS version | `__osx >= 13.0`   |

## Default Requirements

### Linux

```toml
[system-requirements]
linux = "4.18"
libc = { family = "glibc", version = "2.28" }
```

### macOS

```toml
[system-requirements]
macos = "13.0"
```

## CUDA Configuration

### Basic Setup

```toml
[system-requirements]
cuda = "12"  # Expected host CUDA driver API version

[feature.gpu.dependencies]
pytorch = "*"
cuda-nvcc = "*"
```

### Multi-CUDA Support

```toml
[feature.cuda11]
system-requirements = { cuda = "11" }
dependencies = { cudatoolkit = "11.*" }

[feature.cuda12]
system-requirements = { cuda = "12" }
dependencies = { cuda = "12.*" }

[environments]
gpu-11 = ["cuda11"]
gpu-12 = ["cuda12"]
```

## glibc Configuration

### Custom Version

```toml
[system-requirements]
libc = { family = "glibc", version = "2.17" }
```

### Supporting Older Systems

```toml
# For CentOS 7, RHEL 7, older HPC
[system-requirements]
linux = "3.10"
libc = { family = "glibc", version = "2.17" }
```

## Environment Variable Overrides

```bash
export CONDA_OVERRIDE_CUDA=11.8
export CONDA_OVERRIDE_GLIBC=2.28
export CONDA_OVERRIDE_OSX=12.0
pixi install
```

## Feature-Specific Requirements

```toml
[system-requirements]
linux = "4.18"  # Default

[feature.gpu]
system-requirements = { cuda = "12" }

[feature.legacy]
system-requirements = { linux = "4.12", libc = { family = "glibc", version = "2.17" } }

[environments]
gpu = ["gpu"]
legacy = ["legacy"]
```

## Platform-Specific Dependencies

```toml
[dependencies]
python = ">=3.10"

[target.linux-64.dependencies]
gcc_linux-64 = "*"

[target.osx-64.dependencies]
clang_osx-64 = "*"

[target.win-64.dependencies]
vs2019_win-64 = "*"
```

## Common Errors

### Mismatching Virtual Package

```text
× The workspace requires '__linux' to be at least version '4.18'
  but the system has version '4.12.14'
```

**Fix**: Lower requirement or upgrade system.

### CUDA Not Detected

```text
× The platform should have __cuda on version 12
```

**Fix**: Check `nvidia-smi`, use `CONDA_OVERRIDE_CUDA=12`.

## Docker Integration

```dockerfile
FROM nvidia/cuda:12.0-runtime-ubuntu22.04
RUN curl -fsSL https://pixi.sh/install.sh | bash
COPY pixi.toml pixi.lock ./
RUN pixi install -e gpu
```

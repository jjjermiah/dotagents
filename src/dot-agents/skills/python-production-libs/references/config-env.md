# Config & Environment

**ALWAYS query Context7 before writing config code.**

## Context7 (REQUIRED)

```text
Library: /theskumar/python-dotenv

Suggested queries:
- "load_dotenv options and override"
- "dotenv_values for dict access"

Library: /yaml/pyyaml

Suggested queries:
- "safe_load vs load"
- "dump with default_flow_style"
```

For pydantic-settings, see `validation.md`.

## python-dotenv (simple)

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
```

## TOML (stdlib 3.11+)

```python
import tomllib
from pathlib import Path

with Path("config.toml").open("rb") as f:
    config = tomllib.load(f)
```

## YAML

```bash
pip install pyyaml
```

```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)  # Always safe_load!
```

## Pattern: Combined Config

Priority (highest to lowest):
1. Environment variables
2. `.env` file
3. `config.toml`
4. Defaults

Use `pydantic-settings` for type-safe access with automatic env loading.

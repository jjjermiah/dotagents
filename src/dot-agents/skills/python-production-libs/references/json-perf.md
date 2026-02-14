# JSON Performance: orjson

**ALWAYS query Context7 before writing orjson code.**

## Context7 (REQUIRED)

```text
Library: /ijl/orjson

Suggested queries:
- "serialization options and flags"
- "datetime and UUID handling"
- "numpy array serialization"
- "custom default function"
```

## Why orjson > json

- 2-3x faster
- Native `datetime`, `UUID`, `dataclass` support
- Compact output

## Install

```bash
pip install orjson
```

## Quick Pattern

```python
import orjson
from datetime import datetime

data = {"ts": datetime.now(), "items": [1, 2, 3]}

# Returns bytes (not str)
json_bytes = orjson.dumps(data)
parsed = orjson.loads(json_bytes)

# Options
orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
```

## Key Options

- `OPT_INDENT_2` - Pretty print
- `OPT_SORT_KEYS` - Deterministic output
- `OPT_UTC_Z` - Append Z to UTC timestamps
- `OPT_SERIALIZE_NUMPY` - NumPy arrays

## FastAPI Integration

```python
from fastapi.responses import ORJSONResponse
app = FastAPI(default_response_class=ORJSONResponse)
```

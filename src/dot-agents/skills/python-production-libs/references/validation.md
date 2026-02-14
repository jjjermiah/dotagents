# Validation: pydantic

**ALWAYS query Context7 before writing pydantic code.**

## Context7 (REQUIRED)

```text
Library: /pydantic/pydantic

Suggested queries:
- "BaseModel validation and serialization"
- "field validators and model validators"
- "nested models and generics"
- "strict mode configuration"

Library: /pydantic/pydantic-settings

Suggested queries:
- "BaseSettings from environment variables"
- "env file and env prefix configuration"
- "nested settings with delimiter"
```

## Why pydantic > dataclasses

- Runtime validation
- Type coercion (`"123"` → `123`)
- JSON serialization built-in
- Settings from env vars

## Install

```bash
pip install pydantic pydantic-settings
```

## Quick Pattern

```python
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

class User(BaseModel):
    id: int
    email: str
    age: int = Field(ge=0, le=120)

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"
```

## Key APIs

- `BaseModel` - Data validation
- `BaseSettings` - Env config
- `Field()` - Constraints
- `@field_validator` / `@model_validator` - Custom validation
- `.model_dump()` / `.model_dump_json()` - Serialization

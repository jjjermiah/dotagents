# Async: anyio

**ALWAYS query Context7 before writing anyio code.**

## Context7 (REQUIRED)

```text
Library: /agronholm/anyio

Suggested queries:
- "task groups and structured concurrency"
- "cancellation and timeouts"
- "synchronization primitives"
- "running sync code in threads"
- "async file operations"
```

## Why anyio > asyncio (for libraries)

- Works with asyncio AND trio
- Structured concurrency (task groups)
- Better cancellation
- Use asyncio for apps; anyio for libraries

## Install

```bash
pip install anyio
```

## Quick Pattern

```python
import anyio

async def main():
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch, 1)
        tg.start_soon(fetch, 2)
    # All tasks complete here

anyio.run(main)
```

## Key APIs

- `anyio.create_task_group()` - Structured concurrency
- `anyio.fail_after()` / `anyio.move_on_after()` - Timeouts
- `anyio.Lock()` / `anyio.Semaphore()` - Sync primitives
- `anyio.to_thread.run_sync()` - Run blocking code
- `anyio.Path` - Async file operations

## asyncio (for apps)

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:  # 3.11+
        tg.create_task(fetch(1))
        tg.create_task(fetch(2))

asyncio.run(main)
```

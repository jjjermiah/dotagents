# CLI: typer

**ALWAYS query Context7 before writing typer code.**

## Context7 (REQUIRED)

```text
Library: /fastapi/typer

Suggested queries:
- "commands and subcommands"
- "options and arguments with Annotated"
- "progress bars and rich integration"
- "testing CLI with CliRunner"
```

## Why typer > argparse

- Type-hint based (no manual parser)
- Auto-generates help from docstrings
- Built on click, integrates with rich
- Less boilerplate

## Install

```bash
pip install "typer[all]"
```

## Quick Pattern

```python
import typer
from typing import Annotated
from pathlib import Path

app = typer.Typer()

@app.command()
def process(
    input_file: Annotated[Path, typer.Argument(help="Input file")],
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
):
    """Process a file."""
    ...

if __name__ == "__main__":
    app()
```

## Key APIs

- `typer.Typer()` - App instance
- `@app.command()` - Register command
- `typer.Argument()` / `typer.Option()` - Parameter config
- `typer.echo()` / `typer.Exit()` - Output and exit
- `CliRunner` - Testing

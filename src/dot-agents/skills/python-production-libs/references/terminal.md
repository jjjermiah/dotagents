# Terminal Output: rich

**ALWAYS query Context7 before writing rich code.**

## Context7 (REQUIRED)

```text
Library: /textualize/rich

Suggested queries:
- "console print with styles and markup"
- "tables with columns and rows"
- "progress bars and track"
- "logging handler integration"
- "exception tracebacks with locals"
```

## Why rich > print()

- Colored, styled output
- Tables, progress bars, panels
- Syntax highlighting
- Beautiful tracebacks

## Install

```bash
pip install rich
```

## Quick Pattern

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()
console.print("[bold red]Error:[/] Something failed")

# Table
table = Table(title="Results")
table.add_column("Name", style="cyan")
table.add_row("Alice")
console.print(table)

# Progress
for item in track(items, description="Processing..."):
    process(item)
```

## Key Classes

- `Console` - Main output
- `Table` - Tabular data
- `Panel` - Boxed content
- `Syntax` - Code highlighting
- `track()` / `Progress` - Progress bars
- `RichHandler` - Logging integration

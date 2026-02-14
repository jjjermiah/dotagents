---
name: python-pybytesize
description: Byte size parsing and formatting with pybytesize. Use when converting bytes to human-readable sizes, parsing size strings, or doing block-aligned calculations—e.g., "format 1GB as MiB", "parse '500MB'", "human readable file size".
---

# Pybytesize

## Purpose

Use pybytesize (imported as `bytesize`) to parse and manipulate byte sizes with consistent unit conversions and formatting. We provide concise, accurate examples that show how ByteSize objects behave with metric vs binary units.

## Key Requirements

**ALWAYS distinguish metric vs binary units explicitly.** Mixing MB (1000) with MiB (1024) causes silent errors. No exceptions.

**YOU MUST catch specific exceptions** (`UnrecognizedSizeStringError`, `UnknownUnitError`, `NegativeByteSizeError`) when parsing user input. Generic `ByteSizeError` catches everything—but specific exceptions give better UX. Every time.

**When doing block-aligned calculations, verify `block_bytes > 0` first.** `apparent_size()` raises `ValueError` on invalid input. Always.

## Quick start

Create a ByteSize from bytes or a size string and print a readable value.

```python
from bytesize import ByteSize

size = ByteSize(1_048_576)
print(size)  # 1.00 MiB

size = ByteSize("500MB")
print(size.bytes)  # 500000000
print(size)        # 476.84 MiB
```

## Common tasks

Convert between metric and binary units using dynamic attributes.

```python
from bytesize import ByteSize

size = ByteSize(1_073_741_824)
print(size.MB)   # 1073.741824
print(size.MiB)  # 1024.0
print(size.GiB)  # 1.0
```

Pick a best-fit unit for display.

```python
from bytesize import ByteSize

size = ByteSize(1_234_567)
unit, value = size.readable_metric
print(f"{value:.2f} {unit}")  # 1.23 MB

unit, value = size.readable_binary
print(f"{value:.2f} {unit}")  # 1.18 MiB
```

Format with precision and target units using format spec.

```python
from bytesize import ByteSize

size = ByteSize(123_456_789)
print(f"{size:.2f:MB}")   # 123.46 MB
print(f"{size:.2f:GiB}")  # 0.11 GiB
```

Compute block-aligned apparent size.

```python
from bytesize import ByteSize

size = ByteSize(123_456_789)
aligned = size.apparent_size(4096)
print(aligned.bytes)  # 123457536
```

Arithmetic works on ByteSize objects and preserves units.

```python
from bytesize import ByteSize

total = ByteSize("1GB") + ByteSize("512MB")
print(total)  # 1.50 GiB
```

## Error handling

pybytesize provides specific exceptions you can catch for validation and UX.

```python
from bytesize import (
    ByteSize,
    ByteSizeError,
    NegativeByteSizeError,
    UnrecognizedSizeStringError,
    UnknownUnitError,
)

try:
    size = ByteSize("not_a_size")
except UnrecognizedSizeStringError:
    print("Could not parse size string")

try:
    size = ByteSize("100XX")
except UnknownUnitError as e:
    print(f"Unknown unit: {e}")

try:
    size = ByteSize(-1000)
except NegativeByteSizeError as e:
    print(f"Error: {e}")

try:
    size = ByteSize("-50MB")
except ByteSizeError as e:
    print(f"ByteSize error: {e}")
```

## Non-obvious details

**String parsing without validation = runtime failures. Every time.** Always wrap parsing in try/except blocks for user input.

- String parsing accepts whitespace and underscores (e.g., " 1024B ", "1_073_741_824MB").
- `print(ByteSize(...))` defaults to a best-fit binary unit (base 1024).
- `readable_metric` uses base 1000, `readable_binary` uses base 1024; both return `(unit, value)`.
- Full-name unit attributes are supported (e.g., `megabytes`, `gibibytes`).
- `apparent_size(block_bytes)` requires `block_bytes > 0`; it raises ValueError otherwise.

## References

None.

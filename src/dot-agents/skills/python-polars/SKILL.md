---
name: python-polars
description: Enforces Polars over Pandas for functional pipe-style data manipulation (like dplyr in R). Use when writing Python data processing code, data transformation pipelines, ETL workflows, or analytical queries—e.g., "process this CSV", "aggregate sales data", "filter and transform DataFrame", "group by and calculate metrics".
---

# Python Polars - Pipe-Style Data Manipulation

## Purpose

Enforce Polars as the default for all Python data manipulation. Polars provides a functional, pipe-style API similar to dplyr in R—code reads as a clear series of composable transformations rather than imperative steps. This produces more readable, maintainable, and performant data pipelines.

## CRITICAL: Polars-First Mandate

**YOU MUST use Polars for ALL data manipulation in Python.** No exceptions for new code.

**IMMEDIATELY upon loading this skill:**
1. Announce: "Using python-polars - enforcing pipe-style data manipulation with Polars"
2. Reject any pandas code without explicit justification
3. Convert all data operations to Polars expressions and method chains

### Authority: Why Polars is Mandatory

- **Pipe-style syntax**: Method chains read as clear transformation steps (like dplyr's `%>%`)
- **Immutable data**: No hidden state mutations, predictable transformations
- **Expression-based**: Operations are explicit and composable
- **Automatic optimization**: Query planner optimizes your pipeline
- **Modern standard**: Polars is the dplyr equivalent for Python

### Commitment: Exception Protocol

If you MUST use pandas (ML ecosystem compatibility only):
1. Announce: "FALLING BACK TO PANDAS: [specific reason]"
2. Keep pandas usage at boundary (convert: `df_polars.to_pandas()`)
3. Return to Polars immediately after boundary operation

### Social Proof: Industry Standard

Polars represents the modern functional approach to data manipulation—like dplyr in R, it emphasizes readable pipelines over imperative code. Legacy pandas patterns (in-place mutation, index manipulation, row iteration) are technical debt.

## Core Principles: The Pipe-Style Philosophy

| Principle | Polars (Good) | Pandas (Bad) |
|-----------|---------------|--------------|
| **Method chains** | Continuous pipeline | Breaking into separate statements |
| **Readability** | Each step clearly named | Mental state tracking required |
| **Expressions** | `pl.col("x") * 2` | `df["x"] * 2` (implicit) |
| **Immutability** | `df.with_columns(...)` returns new | `df["x"] = y` mutates in place |
| **Functional** | Data flows through transformations | Imperative step-by-step |

### The Readable Pipeline Pattern

**GOOD - Clear pipe-style chain:**
```python
import polars as pl

result = (
    pl.scan_csv("sales.csv")                    # 1. Start with data source
    .filter(pl.col("date") >= "2024-01-01")    # 2. Filter to relevant rows
    .with_columns(                              # 3. Add computed columns
        revenue=pl.col("units") * pl.col("price"),
        is_weekend=pl.col("date").dt.weekday().is_in([6, 7]),
    )
    .group_by(["region", "is_weekend"])         # 4. Group for aggregation
    .agg(                                       # 5. Calculate metrics
        total_revenue=pl.col("revenue").sum(),
        order_count=pl.col("order_id").count(),
        avg_order=pl.col("revenue").mean(),
    )
    .filter(pl.col("order_count") > 10)         # 6. Filter aggregated results
    .sort(["region", "total_revenue"], descending=[False, True])
    .collect()                                  # 7. Execute pipeline
)
```

**BAD - Broken into imperative steps:**
```python
import pandas as pd  # WRONG - using pandas

df = pd.read_csv("sales.csv")  # Eager load
df = df[df["date"] >= "2024-01-01"]  # Filter
df["revenue"] = df["units"] * df["price"]  # Mutate
df["is_weekend"] = df["date"].dt.weekday.isin([6, 7])  # More mutation
result = df.groupby(["region", "is_weekend"]).agg({  # Group and aggregate
    "revenue": ["sum", "mean", "count"]
})
```

## YOU MUST

- **Use Polars for all data manipulation** - pandas is legacy tech debt
- **Write pipe-style chains** - continuous method chains, not broken steps
- **Start with lazy scanning** - `pl.scan_csv()`, `pl.scan_parquet()` for large data
- **Use explicit column references** - `pl.col("name")` over string indexing
- **Compute multiple columns in single context** - parallel execution within `.with_columns()`
- **Name each transformation clearly** - code should read like data flows
- **Query Context7 for Polars APIs** - `context7_query-docs(libraryId="/pola-rs/polars", query="...")`

## NEVER

- **Use pandas for new data manipulation code** - convert to Polars immediately
- **Break pipelines into sequential steps** - use single chain with comments
- **Iterate rows with `iter_rows()`** - use vectorized expressions
- **Apply Python functions with `apply()`** - use native Polars expressions
- **Mutate DataFrames in place** - Polars is immutable, embrace it
- **Use index-based operations** - Polars has no index (and that's good)
- **Mix pandas and Polars** - choose one per pipeline, convert at boundaries only

## Quick Reference: Pandas vs Polars

| Operation | Pandas (Imperative) | Polars (Pipe-Style) |
|-----------|---------------------|---------------------|
| **Read CSV (large)** | `pd.read_csv()` then filter | `pl.scan_csv().filter().collect()` |
| **Select columns** | `df[["a", "b"]]` | `df.select("a", "b")` |
| **Filter rows** | `df[df.a > 10]` | `df.filter(pl.col("a") > 10)` |
| **Add column** | `df["c"] = df.a + df.b` | `df.with_columns(c=pl.col("a") + pl.col("b"))` |
| **Group by + agg** | `df.groupby("x").y.sum()` | `df.group_by("x").agg(pl.col("y").sum())` |
| **Window/rank** | `df.groupby("x").y.rank()` | `df.with_columns(pl.col("y").rank().over("x"))` |
| **Conditional** | `np.where(df.a > 10, "high", "low")` | `pl.when(pl.col("a") > 10).then("high").otherwise("low")` |
| **Join** | `df1.merge(df2, on="id")` | `df1.join(df2, on="id")` |
| **Sort** | `df.sort_values("a")` | `df.sort("a")` |
| **Drop duplicates** | `df.drop_duplicates()` | `df.unique()` |
| **Missing values** | `df.fillna(0)` | `df.fill_null(0)` |

## The Expression is Everything

Master these patterns for pipe-style code:

```python
# Column reference and arithmetic
pl.col("revenue") / pl.col("units")

# Conditional logic (CASE WHEN equivalent)
pl.when(pl.col("age") >= 18).then("adult").otherwise("minor")

# String operations
pl.col("name").str.to_uppercase()
pl.col("email").str.contains("@")

# Date/time operations
pl.col("timestamp").dt.year()
pl.col("date").dt.truncate("1d")

# Aggregations (use in .agg() context)
pl.col("value").sum()
pl.col("value").mean()
pl.col("id").n_unique()

# Window functions (use .over() for group transforms)
pl.col("value").sum().over("category")  # Category total per row
pl.col("value").rank().over("category")   # Rank within category
```

## References (Load on Demand)

- **[references/migration-patterns.md](references/migration-patterns.md)** - Load when converting existing pandas code or need side-by-side operation comparisons
- **[references/anti-patterns.md](references/anti-patterns.md)** - Load when reviewing code quality or debugging performance issues
- **[references/pipe-style-guide.md](references/pipe-style-guide.md)** - Load when designing complex multi-step pipelines or need formatting guidance
- **[references/expression-patterns.md](references/expression-patterns.md)** - Load when building reusable expression functions or need advanced composition patterns

## Context7 Integration

**YOU MUST query Context7 for Polars APIs before writing implementation code.**

```bash
# Resolve library ID first
context7_resolve-library-id(libraryName="polars", query="Polars DataFrame library")

# Then query for specific operations
context7_query-docs(libraryId="/pola-rs/polars", query="lazy scan filter example")
```

Context7 provides current, accurate API documentation. Pre-trained knowledge of Polars APIs will be stale and cause bugs.

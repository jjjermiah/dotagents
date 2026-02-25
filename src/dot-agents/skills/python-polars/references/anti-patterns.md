# Anti-Patterns: What to Avoid in Polars

## 1. Row-Based Iteration

**BAD - Never iterate rows:**
```python
# SLOW - Python loop over rows
for row in df.iter_rows():
    if row["value"] > 100:
        process(row)
```

**GOOD - Use vectorized expressions:**
```python
# FAST - Native vectorized operations
result = df.filter(pl.col("value") > 100)
```

**Why**: Row iteration breaks vectorization, disables SIMD, and forces Python interpreter overhead for every row. Polars expressions are compiled and run in parallel.

## 2. Breaking the Pipeline

**BAD - Multiple intermediate DataFrames:**
```python
# Forces sequential execution, harder to read
df1 = df.filter(pl.col("date") >= "2024-01-01")
df2 = df1.with_columns(revenue=pl.col("units") * pl.col("price"))
df3 = df2.filter(pl.col("revenue") > 1000)
result = df3.group_by("region").agg(pl.col("revenue").sum())
```

**GOOD - Single continuous chain:**
```python
# Optimized query plan, clear transformation steps
result = (
    df.filter(pl.col("date") >= "2024-01-01")
    .with_columns(revenue=pl.col("units") * pl.col("price"))
    .filter(pl.col("revenue") > 1000)
    .group_by("region")
    .agg(pl.col("revenue").sum())
)
```

**Why**: Breaking into intermediate variables prevents query optimization and reduces readability. The optimizer can't see across variable boundaries.

## 3. Sequential Pipe Functions

**BAD - Multiple .pipe() calls that could be one context:**
```python
# Sequential execution, no parallelism
def add_foo(df):
    return df.with_columns(foo=pl.col("a") * 2)

def add_bar(df):
    return df.with_columns(bar=pl.col("b") + 10)

def add_baz(df):
    return df.with_columns(baz=pl.col("c").str.to_uppercase())

result = df.pipe(add_foo).pipe(add_bar).pipe(add_baz)
# Forces 3 separate operations, zero parallelism
```

**GOOD - Single .with_columns() context:**
```python
# All columns computed in parallel
result = df.with_columns(
    foo=pl.col("a") * 2,
    bar=pl.col("b") + 10,
    baz=pl.col("c").str.to_uppercase(),
)
```

**Why**: Each `.pipe()` call is a separate operation. Single context enables automatic parallelization.

## 4. In-Place Mutations (Pandas Habit)

**BAD - Trying to mutate in place:**
```python
# Pandas-style mutation (doesn't work in Polars)
df["new_col"] = ...  # Error - Polars DataFrames are immutable
df.drop("old_col", inplace=True)  # inplace parameter doesn't exist
```

**GOOD - Embrace immutability:**
```python
# Always returns new DataFrame
result = df.with_columns(new_col=...)
result = result.drop("old_col")
# df is unchanged - predictable and safe
```

**Why**: Immutability prevents bugs from hidden state changes. Each operation creates a clear data lineage.

## 5. Index-Based Operations

**BAD - Using index patterns from pandas:**
```python
# These don't exist in Polars!
df.set_index("id")  # No index concept
df.loc[0]  # No loc
df.iloc[0:10]  # No iloc
df.reset_index()  # Not needed
```

**GOOD - Explicit column operations:**
```python
# Row access is always explicit
row_0 = df.row(0)  # Get first row as tuple

# Row filtering is always with filter()
result = df.filter(pl.col("id") == 1)

# Column access is always with select/with_columns
result = df.select("col_a", "col_b")
result = df.head(10)  # Instead of iloc[:10]
```

**Why**: Indices are fragile (what if data is sorted?). Explicit column references are self-documenting and don't break when data changes.

## 6. Eager Loading Large Data

**BAD - Reading entire file then filtering:**
```python
# Loads everything into memory, then filters
df = pl.read_csv("huge_file.csv")  # 10GB loaded
result = df.filter(pl.col("date") > "2024-01-01")  # Most data discarded
```

**GOOD - Lazy scanning with predicate pushdown:**
```python
# Only reads rows and columns that pass the filter
result = (
    pl.scan_csv("huge_file.csv")
    .filter(pl.col("date") > pl.lit("2024-01-01"))
    .select(["id", "value"])  # Projection pushdown too
    .collect()
)
```

**Why**: Lazy execution enables predicate pushdown - the query optimizer pushes filters to the data source, reading only what's needed.

## 7. Python UDFs with apply/map_elements

**BAD - Using Python functions for simple operations:**
```python
# SLOW - Python function called for every row
def categorize_price(price):
    if price < 10:
        return "low"
    elif price < 50:
        return "medium"
    else:
        return "high"

result = df.with_columns(
    category=pl.col("price").map_elements(categorize_price)
)
```

**GOOD - Native Polars expressions:**
```python
# FAST - Vectorized native implementation
result = df.with_columns(
    category=pl.when(pl.col("price") < 10)
        .then("low")
        .when(pl.col("price") < 50)
        .then("medium")
        .otherwise("high")
)
```

**Why**: `map_elements()` forces row-by-row Python execution. Only use for operations that truly can't be expressed as native expressions.

## 8. Ignoring Data Types

**BAD - Implicit type inference:**
```python
# Letting Polars infer (may fail or be suboptimal)
df = pl.DataFrame({
    "id": ["1", "2", "3"],  # Should stay string
    "value": [1, 2, 3],
    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
})
# id might get parsed as integer, date stays string
```

**GOOD - Explicit schema definition:**
```python
# Define schema explicitly for clarity and correctness
df = pl.DataFrame(
    data=[
        {"id": "1", "value": 1, "date": "2024-01-01"},
        {"id": "2", "value": 2, "date": "2024-01-02"},
    ],
    schema={
        "id": pl.Utf8,           # Keep IDs as strings
        "value": pl.Int64,
        "date": pl.Date,        # Parse as date
    }
)

# Or when reading
df = pl.read_csv(
    "data.csv",
    dtypes={"id": pl.Utf8, "amount": pl.Float64},
    try_parse_dates=True,
)
```

**Why**: Explicit types prevent bugs (IDs as integers lose leading zeros), improve memory efficiency, and enable better optimization.

## 9. Confusing Null and NaN

**BAD - Treating null and NaN the same:**
```python
# Wrong - NaN != null in Polars
result = df.with_columns(
    pl.col("value").fill_null(0),  # Only fills null, not NaN
)
# NaN values remain!
```

**GOOD - Handle both explicitly:**
```python
# Handle both missing data types
result = df.with_columns(
    pl.col("value").fill_null(0),     # Fill null (missing for all types)
    pl.col("float_col").fill_nan(0),  # Fill NaN (float not-a-number)
)

# Or chain them
result = df.with_columns(
    pl.col("float_col").fill_nan(0).fill_null(0)
)
```

**Why**: Polars distinguishes between `null` (missing data, any type) and `NaN` (IEEE 754 not-a-number, float only). They require different handling.

## 10. Window Functions Without Over

**BAD - Aggregation in wrong context:**
```python
# Returns scalar - wrong for row-level operations
result = df.with_columns(
    total=pl.col("revenue").sum(),  # Single value for entire column!
)
```

**GOOD - Use .over() for window functions:**
```python
# Returns value per row, computed within group
result = df.with_columns(
    total_by_category=pl.col("revenue").sum().over("category"),
    rank_in_category=pl.col("revenue").rank().over("category"),
)
```

**Why**: Same expression, different context = different semantics. `.over()` broadcasts aggregation back to row level (SQL window function behavior).

## Summary: When to Use What

| Situation | Approach | Why |
|-----------|----------|-----|
| **Simple transformation** | Native expressions | Speed, clarity |
| **Multiple column calcs** | Single `.with_columns()` | Parallelism |
| **Complex Python logic** | `map_elements()` (last resort) | Sometimes necessary |
| **Row iteration** | Never - refactor to expressions | Performance |
| **Large data** | Lazy scanning | Memory efficiency |
| **Aggregation per group** | `.group_by().agg()` | Scalar per group |
| **Group transform** | `.agg().over()` | Row-level with group context |
| **Join filtering** | Semi/anti joins | Optimization |
| **Missing data** | `fill_null()` / `fill_nan()` | Correct semantics |
| **Type safety** | Explicit schema | Correctness |

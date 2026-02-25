# Migration Patterns: Pandas to Polars

## File I/O Patterns

### Reading Data

| Pandas | Polars (Eager) | Polars (Lazy - Preferred) |
|--------|----------------|---------------------------|
| `pd.read_csv("file.csv")` | `pl.read_csv("file.csv")` | `pl.scan_csv("file.csv")` |
| `pd.read_parquet("file.parq")` | `pl.read_parquet("file.parq")` | `pl.scan_parquet("file.parq")` |

**Lazy is preferred for production** - query optimizer applies predicate pushdown and projection pushdown.

```python
# Pandas - loads everything, then filters
import pandas as pd
df = pd.read_csv("large_file.csv")
df_filtered = df[df["date"] > "2024-01-01"]

# Polars lazy - reads only what's needed
import polars as pl
result = (
    pl.scan_csv("large_file.csv")
    .filter(pl.col("date") > "2024-01-01")
    .collect()
)
```

### Writing Data

| Pandas | Polars |
|--------|--------|
| `df.to_csv("out.csv")` | `df.write_csv("out.csv")` |
| `df.to_parquet("out.parq")` | `df.write_parquet("out.parq")` |

## Column Selection

| Pandas | Polars |
|--------|--------|
| `df[["a", "b"]]` | `df.select("a", "b")` |
| `df["a"]` | `df.select("a")` or `df.get_column("a")` |
| `df.filter(regex="^prefix")` | `df.select(pl.col("^prefix.*$"))` |
| `df.iloc[:, :5]` | `df.select(pl.all().limit(5))` |

```python
# Multiple selection patterns
df.select("col_a", "col_b")                    # Explicit columns
df.select(pl.col("col_a"), pl.col("col_b"))   # Expression style
df.select(pl.all())                            # All columns
df.select(pl.col("^prefix_.*$"))              # Regex pattern
df.select(pl.col("a"), pl.col("b").alias("b_renamed"))  # With rename
```

## Filtering Rows

| Pandas | Polars |
|--------|--------|
| `df[df["a"] > 10]` | `df.filter(pl.col("a") > 10)` |
| `df[(df["a"] > 10) & (df["b"] < 5)]` | `df.filter((pl.col("a") > 10) & (pl.col("b") < 5))` |
| `df[df["c"].isin(["A", "B"])]` | `df.filter(pl.col("c").is_in(["A", "B"]))` |

```python
# Multiple conditions
result = df.filter(
    (pl.col("revenue") > 1000) &
    (pl.col("region") == "US") &
    (pl.col("date") > "2024-01-01")
)

# Or conditions
result = df.filter(
    (pl.col("category") == "A") |
    (pl.col("category") == "B")
)

# is_in for multiple values (cleaner than multiple or)
result = df.filter(pl.col("category").is_in(["A", "B", "C"]))
```

## Adding/Modifying Columns

| Pandas | Polars |
|--------|--------|
| `df["c"] = df["a"] + df["b"]` | `df = df.with_columns(c=pl.col("a") + pl.col("b"))` |
| `df["c"] = df["a"] * 2` | `df = df.with_columns(pl.col("a") * 2)` |
| `df["c"] = np.where(df["a"] > 0, "pos", "neg")` | `df = df.with_columns(pl.when(pl.col("a") > 0).then("pos").otherwise("neg"))` |

```python
# Single .with_columns() context = parallel execution
result = df.with_columns(
    # Multiple columns computed in parallel
    revenue_total=pl.col("revenue").sum(),
    revenue_mean=pl.col("revenue").mean(),
    is_high_value=pl.col("revenue") > 1000,
    price_category=pl.when(pl.col("price") < 10)
        .then("low")
        .when(pl.col("price") < 50)
        .then("medium")
        .otherwise("high"),
)
```

## Group By and Aggregation

| Pandas | Polars |
|--------|--------|
| `df.groupby("x").agg({"y": "sum"})` | `df.group_by("x").agg(pl.col("y").sum())` |
| `df.groupby("x").agg({"y": ["sum", "mean"]})` | `df.group_by("x").agg(pl.col("y").sum(), pl.col("y").mean())` |
| `df.groupby("x").size()` | `df.group_by("x").len()` |

```python
# Multiple aggregations with aliases
result = df.group_by(["region", "product"]).agg(
    pl.col("sales").sum().alias("total_sales"),
    pl.col("sales").mean().alias("avg_sales"),
    pl.col("sales").max().alias("max_sales"),
    pl.col("customer_id").n_unique().alias("unique_customers"),
    pl.col("order_id").count().alias("order_count"),
)

# Multiple columns at once
result = df.group_by("category").agg(pl.all().sum())  # Sum all numeric columns
```

## Window Functions (Group Transforms)

| Pandas | Polars |
|--------|--------|
| `df["size"] = df.groupby("c")["type"].transform(len)` | `df = df.with_columns(pl.col("type").count().over("c"))` |
| `df["rank"] = df.groupby("c")["v"].rank()` | `df = df.with_columns(pl.col("v").rank().over("c"))` |
| `df["cumsum"] = df.groupby("c")["v"].cumsum()` | `df = df.with_columns(pl.col("v").cum_sum().over("c"))` |

```python
# Window functions using .over()
result = df.with_columns(
    total_by_category=pl.col("revenue").sum().over("category"),
    revenue_rank=pl.col("revenue").rank().over("category"),
    running_total=pl.col("revenue").cum_sum().over("category"),
    market_share=pl.col("revenue") / pl.col("revenue").sum().over("category"),
)
```

## Joins

| Pandas | Polars |
|--------|--------|
| `df1.merge(df2, on="id")` | `df1.join(df2, on="id")` |
| `df1.merge(df2, left_on="a", right_on="b")` | `df1.join(df2, left_on="a", right_on="b")` |
| `df1.merge(df2, on="id", how="left")` | `df1.join(df2, on="id", how="left")` |
| `df1[df1["id"].isin(df2["id"])]` | `df1.join(df2, on="id", how="semi")` |
| `df1[~df1["id"].isin(df2["id"])]` | `df1.join(df2, on="id", how="anti")` |

```python
# Different join types
inner = df_left.join(df_right, on="id", how="inner")
left = df_left.join(df_right, on="id", how="left")
right = df_left.join(df_right, on="id", how="right")
full = df_left.join(df_right, on="id", how="full")
cross = df_left.join(df_right, how="cross")  # Cartesian product

# Semi join (filter to rows that exist in right)
semi = df_customers.join(df_orders, on="customer_id", how="semi")

# Anti join (filter to rows that DON'T exist in right)
anti = df_customers.join(df_orders, on="customer_id", how="anti")

# Different column names
joined = df_customers.join(
    df_orders,
    left_on="customer_id",
    right_on="id",
    how="left"
)
```

## Sorting

| Pandas | Polars |
|--------|--------|
| `df.sort_values("a")` | `df.sort("a")` |
| `df.sort_values("a", ascending=False)` | `df.sort("a", descending=True)` |
| `df.sort_values(["a", "b"], ascending=[True, False])` | `df.sort(["a", "b"], descending=[False, True])` |

## Dropping Duplicates

| Pandas | Polars |
|--------|--------|
| `df.drop_duplicates()` | `df.unique()` |
| `df.drop_duplicates(subset=["a"])` | `df.unique(subset=["a"])` |
| `df.drop_duplicates(keep="last")` | `df.unique(keep="last")` |

## Handling Missing Values

| Pandas | Polars |
|--------|--------|
| `df.fillna(0)` | `df.fill_null(0)` |
| `df["a"].fillna(method="ffill")` | `df.with_columns(pl.col("a").fill_null(strategy="forward"))` |
| `df.dropna()` | `df.drop_nulls()` |
| `df.dropna(subset=["a"])` | `df.drop_nulls(subset=["a"])` |

**Note**: Polars distinguishes between `null` (missing data) and `NaN` (not-a-number for floats). Use `fill_nan()` for NaN values.

```python
result = df.with_columns(
    pl.col("value").fill_null(0),                    # Fill nulls with 0
    pl.col("value").fill_null(strategy="forward"),  # Forward fill
    pl.col("value").fill_null(strategy="backward"), # Backward fill
    pl.col("float_col").fill_nan(0),                # Fill NaN (float only)
)
```

## Type Casting

| Pandas | Polars |
|--------|--------|
| `df["a"].astype(int)` | `df.with_columns(pl.col("a").cast(pl.Int64))` |
| `pd.to_datetime(df["date"])` | `df.with_columns(pl.col("date").str.to_date())` |

```python
result = df.with_columns(
    pl.col("id").cast(pl.Utf8),           # Keep IDs as strings
    pl.col("amount").cast(pl.Float64),    # Decimal numbers
    pl.col("count").cast(pl.Int64),        # Integers
    pl.col("date").str.to_date("%Y-%m-%d"), # Parse string to date
    pl.col("is_active").cast(pl.Boolean), # Boolean
)
```

## Complete Pipeline Example

**Pandas approach:**
```python
import pandas as pd
import numpy as np

df = pd.read_csv("sales.csv")
df = df[df["date"] >= "2024-01-01"]
df["revenue"] = df["units"] * df["price"]
df["is_weekend"] = df["date"].dt.weekday.isin([6, 7])
df["category"] = np.where(df["revenue"] > 1000, "high", "low")

grouped = df.groupby(["region", "is_weekend"]).agg({
    "revenue": ["sum", "mean", "count"],
    "customer_id": "nunique"
}).reset_index()

grouped.columns = ["region", "is_weekend", "total_revenue", "avg_revenue", "order_count", "unique_customers"]
result = grouped[grouped["order_count"] > 10].sort_values(["region", "total_revenue"], ascending=[True, False])
```

**Polars approach:**
```python
import polars as pl

result = (
    pl.scan_csv("sales.csv")  # Lazy start
    .filter(pl.col("date") >= "2024-01-01")
    .with_columns(
        revenue=pl.col("units") * pl.col("price"),
        is_weekend=pl.col("date").dt.weekday().is_in([6, 7]),
        category=pl.when(pl.col("revenue") > 1000).then("high").otherwise("low"),
    )
    .group_by(["region", "is_weekend"])
    .agg(
        total_revenue=pl.col("revenue").sum(),
        avg_revenue=pl.col("revenue").mean(),
        order_count=pl.col("order_id").count(),
        unique_customers=pl.col("customer_id").n_unique(),
    )
    .filter(pl.col("order_count") > 10)
    .sort(["region", "total_revenue"], descending=[False, True])
    .collect()
)
```

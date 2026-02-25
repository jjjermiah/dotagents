# Expression Patterns: Advanced Composition

## The Expression System

Polars is built on expressions (`pl.Expr`). Understanding expressions is key to writing efficient, composable code.

```python
# Everything is an expression
pl.col("price") * 1.1                           # Arithmetic expression
pl.col("name").str.to_uppercase()              # String expression
pl.col("value").sum().over("category")         # Window expression
pl.when(pl.col("x") > 0).then("pos").otherwise("neg")  # Conditional
```

## Building Reusable Expression Functions

### Pattern 1: Parameterized Expressions

```python
from typing import Any

def get_percentage_change(current: str, baseline: str) -> pl.Expr:
    """Calculate percentage change from baseline."""
    return (
        ((pl.col(current) - pl.col(baseline)) / pl.col(baseline) * 100)
        .alias(f"{current}_pct_change")
    )

def get_category_flag(column: str, threshold: float) -> pl.Expr:
    """Flag values above threshold in a column."""
    return (
        pl.when(pl.col(column) > threshold)
        .then(pl.lit("high"))
        .otherwise(pl.lit("low"))
        .alias(f"{column}_category")
    )

def get_binned_column(column: str, bins: list[float], labels: list[str]) -> pl.Expr:
    """Bin continuous values into categories."""
    expr = pl.when(pl.col(column) < bins[0]).then(labels[0])
    for i in range(len(bins) - 1):
        expr = expr.when(pl.col(column) < bins[i + 1]).then(labels[i])
    return expr.otherwise(labels[-1]).alias(f"{column}_binned")

# Usage in pipeline
result = (
    df.with_columns(
        get_percentage_change("revenue_2024", "revenue_2023"),
        get_category_flag("margin", threshold=20.0),
        get_binned_column("age", bins=[18, 35, 50, 65], labels=["youth", "adult", "middle", "senior"]),
    )
)
```

### Pattern 2: Conditional Logic Chains

```python
def get_customer_tier() -> pl.Expr:
    """Multi-tier customer classification."""
    return (
        pl.when(pl.col("lifetime_value") >= 10000)
        .then(pl.lit("platinum"))
        .when(pl.col("lifetime_value") >= 5000)
        .then(pl.lit("gold"))
        .when(pl.col("lifetime_value") >= 1000)
        .then(pl.lit("silver"))
        .otherwise(pl.lit("bronze"))
        .alias("customer_tier")
    )

def get_discount_rate() -> pl.Expr:
    """Tier-based discount calculation."""
    return (
        pl.when(pl.col("customer_tier") == "platinum")
        .then(pl.lit(0.20))
        .when(pl.col("customer_tier") == "gold")
        .then(pl.lit(0.15))
        .when(pl.col("customer_tier") == "silver")
        .then(pl.lit(0.10))
        .otherwise(pl.lit(0.05))
        .alias("discount_rate")
    )

def get_final_price() -> pl.Expr:
    """Calculate price after discount."""
    return (
        (pl.col("list_price") * (1 - pl.col("discount_rate")))
        .alias("final_price")
    )

# Chain them together
result = (
    df.with_columns(
        get_customer_tier(),
    )
    .with_columns(
        get_discount_rate(),
    )
    .with_columns(
        get_final_price(),
    )
)
```

### Pattern 3: Window Function Composition

```python
def get_rank_within_group(group_cols: list[str], rank_col: str) -> pl.Expr:
    """Calculate rank of value within group."""
    return (
        pl.col(rank_col)
        .rank(method="dense")
        .over(group_cols)
        .alias(f"{rank_col}_rank")
    )

def get_percentile_within_group(group_cols: list[str], col: str) -> pl.Expr:
    """Calculate percentile rank within group.""" 
    return (
        (pl.col(col).rank() / pl.col(col).count())
        .over(group_cols)
        .alias(f"{col}_percentile")
    )

def get_running_total(group_cols: list[str], col: str) -> pl.Expr:
    """Cumulative sum within group (ordered by current sort)."""
    return (
        pl.col(col)
        .cum_sum()
        .over(group_cols)
        .alias(f"{col}_running_total")
    )

def get_zscore_within_group(group_cols: list[str], col: str) -> pl.Expr:
    """Standardize values within group."""
    return (
        ((pl.col(col) - pl.col(col).mean()) / pl.col(col).std())
        .over(group_cols)
        .alias(f"{col}_zscore")
    )

# Usage
result = (
    df.sort("date")  # Ensure proper ordering for window functions
    .with_columns(
        get_rank_within_group(["region"], "sales"),
        get_percentile_within_group(["region", "quarter"], "sales"),
        get_running_total(["customer_id"], "revenue"),
        get_zscore_within_group(["category"], "price"),
    )
)
```

## Complex Expression Composition

### Pattern 4: Dynamic Column Selection

```python
def select_by_pattern(pattern: str) -> list[pl.Expr]:
    """Select columns matching regex pattern."""
    return [pl.col(pattern)]

def select_numeric() -> list[pl.Expr]:
    """Select all numeric columns."""
    return [
        pl.col(pl.FLOAT_DTYPES),
        pl.col(pl.INTEGER_DTYPES),
    ]

def get_summary_stats(column: str) -> list[pl.Expr]:
    """Generate multiple aggregations for a column."""
    return [
        pl.col(column).sum().alias(f"{column}_sum"),
        pl.col(column).mean().alias(f"{column}_mean"),
        pl.col(column).std().alias(f"{column}_std"),
        pl.col(column).min().alias(f"{column}_min"),
        pl.col(column).max().alias(f"{column}_max"),
        pl.col(column).count().alias(f"{column}_count"),
    ]

# Usage
result = (
    df.select(
        *select_by_pattern("^sales_.*$"),  # All sales_* columns
        *select_numeric(),                  # All numeric columns
    )
    .group_by("category")
    .agg(*get_summary_stats("revenue"))     # Multiple stats
)
```

### Pattern 5: String Manipulation Pipeline

```python
def clean_string_column(column: str) -> pl.Expr:
    """Standard string cleaning pipeline."""
    return (
        pl.col(column)
        .str.strip()                           # Remove whitespace
        .str.to_lowercase()                     # Normalize case
        .str.replace_all(r"[^a-z0-9\s]", "")   # Remove special chars
        .alias(f"{column}_cleaned")
    )

def extract_email_domain(column: str) -> pl.Expr:
    """Extract domain from email address."""
    return (
        pl.col(column)
        .str.split("@")
        .list.get(1)  # Get part after @
        .alias("email_domain")
    )

def format_currency(column: str, symbol: str = "$") -> pl.Expr:
    """Format numeric column as currency string."""
    return (
        pl.col(column)
        .map_elements(
            lambda x: f"{symbol}{x:,.2f}",
            return_dtype=pl.Utf8,
        )
        .alias(f"{column}_formatted")
    )

# Usage
result = (
    df.with_columns(
        clean_string_column("customer_name"),
        clean_string_column("company"),
        extract_email_domain("email"),
    )
)
```

### Pattern 6: DateTime Transformations

```python
def get_date_features(date_col: str) -> list[pl.Expr]:
    """Extract common date features."""
    return [
        pl.col(date_col).dt.year().alias("year"),
        pl.col(date_col).dt.month().alias("month"),
        pl.col(date_col).dt.day().alias("day"),
        pl.col(date_col).dt.weekday().alias("weekday"),
        pl.col(date_col).dt.isoweek().alias("iso_week"),
        pl.col(date_col).dt.quarter().alias("quarter"),
        pl.col(date_col).dt.is_leap_year().alias("is_leap_year"),
    ]

def get_fiscal_year(date_col: str, fiscal_start_month: int = 7) -> pl.Expr:
    """Calculate fiscal year based on start month."""
    return (
        pl.when(pl.col(date_col).dt.month() >= fiscal_start_month)
        .then(pl.col(date_col).dt.year() + 1)
        .otherwise(pl.col(date_col).dt.year())
        .alias("fiscal_year")
    )

def get_time_bucket(date_col: str, bucket: str = "1h") -> pl.Expr:
    """Truncate timestamp to time bucket."""
    return (
        pl.col(date_col)
        .dt.truncate(bucket)
        .alias(f"{date_col}_{bucket}_bucket")
    )

# Usage
result = (
    df.with_columns(
        *get_date_features("created_at"),
        get_fiscal_year("created_at", fiscal_start_month=10),
        get_time_bucket("created_at", "1d"),
    )
)
```

## Aggregation Expression Patterns

### Pattern 7: Multi-Metric Aggregation

```python
def get_full_aggregations() -> list[pl.Expr]:
    """Comprehensive set of aggregation metrics."""
    return [
        # Counts
        pl.count().alias("row_count"),
        pl.col("customer_id").n_unique().alias("unique_customers"),
        
        # Sums
        pl.col("revenue").sum().alias("total_revenue"),
        pl.col("units").sum().alias("total_units"),
        
        # Averages
        pl.col("revenue").mean().alias("avg_revenue"),
        pl.col("revenue").median().alias("median_revenue"),
        
        # Extremes
        pl.col("revenue").min().alias("min_revenue"),
        pl.col("revenue").max().alias("max_revenue"),
        
        # Dispersion
        pl.col("revenue").std().alias("std_revenue"),
        pl.col("revenue").var().alias("var_revenue"),
        
        # Quantiles
        pl.col("revenue").quantile(0.25).alias("p25_revenue"),
        pl.col("revenue").quantile(0.75).alias("p75_revenue"),
        
        # First/Last
        pl.col("revenue").first().alias("first_revenue"),
        pl.col("revenue").last().alias("last_revenue"),
    ]

# Usage
result = (
    df.group_by("region")
    .agg(*get_full_aggregations())
)
```

### Pattern 8: Conditional Aggregation

```python
def get_conditional_sum(column: str, condition: pl.Expr, alias: str) -> pl.Expr:
    """Sum column where condition is met."""
    return (
        pl.when(condition)
        .then(pl.col(column))
        .otherwise(0)
        .sum()
        .alias(alias)
    )

def get_conditional_count(condition: pl.Expr, alias: str) -> pl.Expr:
    """Count rows where condition is met."""
    return (
        pl.when(condition)
        .then(1)
        .otherwise(0)
        .sum()
        .alias(alias)
    )

# Usage - Analyze sales by category
result = (
    df.group_by("region")
    .agg(
        get_conditional_sum(
            "revenue",
            pl.col("category") == "electronics",
            "electronics_revenue"
        ),
        get_conditional_sum(
            "revenue",
            pl.col("category") == "clothing",
            "clothing_revenue"
        ),
        get_conditional_count(
            pl.col("revenue") > 1000,
            "high_value_orders"
        ),
    )
)
```

## Advanced Window Function Patterns

### Pattern 9: Rolling Calculations

```python
def get_rolling_stats(column: str, window: int, group_by: str | None = None) -> list[pl.Expr]:
    """Generate rolling window statistics."""
    base = pl.col(column)
    if group_by:
        base = base.over(group_by)
    
    return [
        base.rolling_mean(window).alias(f"{column}_ma{window}"),
        base.rolling_std(window).alias(f"{column}_std{window}"),
        base.rolling_min(window).alias(f"{column}_min{window}"),
        base.rolling_max(window).alias(f"{column}_max{window}"),
    ]

def get_exponential_moving_avg(column: str, span: int) -> pl.Expr:
    """Calculate exponential moving average."""
    alpha = 2 / (span + 1)
    return (
        pl.col(column)
        .ewm_mean(alpha=alpha, adjust=False)
        .alias(f"{column}_ema{span}")
    )

# Usage
result = (
    df.sort("date")
    .with_columns(
        *get_rolling_stats("sales", window=7, group_by="store_id"),
        *get_rolling_stats("sales", window=30, group_by="store_id"),
        get_exponential_moving_avg("sales", span=12),
    )
)
```

### Pattern 10: Lead/Lag Features

```python
def get_lag_features(column: str, lags: list[int], group_by: str | None = None) -> list[pl.Expr]:
    """Generate multiple lag features."""
    base = pl.col(column)
    if group_by:
        base = base.over(group_by)
    
    return [
        base.shift(lag).alias(f"{column}_lag{lag}")
        for lag in lags
    ]

def get_lead_features(column: str, leads: list[int], group_by: str | None = None) -> list[pl.Expr]:
    """Generate multiple lead (forward-looking) features."""
    base = pl.col(column)
    if group_by:
        base = base.over(group_by)
    
    return [
        base.shift(-lead).alias(f"{column}_lead{lead}")
        for lead in leads
    ]

def get_diff_features(column: str, periods: list[int], group_by: str | None = None) -> list[pl.Expr]:
    """Generate period-over-period differences."""
    base = pl.col(column)
    if group_by:
        base = base.over(group_by)
    
    return [
        (base - base.shift(period)).alias(f"{column}_diff{period}")
        for period in periods
    ]

# Usage - Time series feature engineering
result = (
    df.sort("date")
    .with_columns(
        *get_lag_features("sales", [1, 7, 30], group_by="store_id"),
        *get_diff_features("sales", [1, 7], group_by="store_id"),
    )
)
```

## Testing Expression Functions

```python
import polars as pl

def test_expression_function():
    """Test pattern for expression functions."""
    # Arrange
    df = pl.DataFrame({
        "revenue_2024": [110, 200, 50],
        "revenue_2023": [100, 100, 100],
    })
    
    # Act
    result = df.with_columns(
        get_percentage_change("revenue_2024", "revenue_2023")
    )
    
    # Assert
    assert result["revenue_2024_pct_change"].to_list() == [10.0, 100.0, -50.0]


def test_window_function():
    """Test pattern for window expressions."""
    df = pl.DataFrame({
        "category": ["A", "A", "B", "B"],
        "value": [10, 20, 30, 40],
    })
    
    result = (
        df.with_columns(
            get_rank_within_group(["category"], "value")
        )
        .sort(["category", "value"])
    )
    
    assert result["value_rank"].to_list() == [1, 2, 1, 2]
```

## Composition Best Practices

1. **Keep expressions pure** - No side effects, only return `pl.Expr`
2. **Use type hints** - `-> pl.Expr` makes intent clear
3. **Alias results** - Always name output columns
4. **Document parameters** - Explain what each parameter controls
5. **Test individually** - Unit test expression functions before using in pipelines
6. **Compose at the end** - Chain `.with_columns()` calls for related operations

# Pipe-Style Guide: Writing Readable Transformation Pipelines

## Philosophy

Polars enables **pipe-style data manipulation** similar to dplyr in R. Code should read as a clear series of composable transformations—each step explicitly stating what it does to the data.

```python
# The ideal: Code reads like a story
df = (
    pl.read_csv("sales.csv")           # Start with data
    .filter(pl.col("date") >= ...)   # Keep relevant rows
    .with_columns(...)               # Add computed columns
    .group_by(...)                    # Group for analysis
    .agg(...)                        # Calculate metrics
    .sort(...)                       # Order for presentation
)
```

## The Pipeline Structure

### 1. Start with Data Source

Always begin with where data comes from:

```python
# Good - Clear data origin
result = (
    pl.scan_parquet("sales/2024/*.parquet")  # Multiple files
    .filter(pl.col("date") >= "2024-01-01")
    .collect()
)

# Or with explicit DataFrame creation
result = (
    pl.DataFrame(data)
    .with_columns(...)
)
```

### 2. Filter Early and Often

Push filters toward the beginning to reduce data volume:

```python
# Good - Filter early
result = (
    pl.scan_csv("large_file.csv")
    .filter(pl.col("status") == "active")     # Filter early
    .filter(pl.col("date") >= "2024-01-01")   # Chain filters
    .select(["id", "value"])                   # Project early
    .with_columns(...)
    .collect()
)

# The optimizer will combine and push down these operations
```

### 3. Group Operations Logically

Use parentheses and line breaks to show logical sections:

```python
result = (
    pl.scan_csv("sales.csv")
    
    # Section 1: Data cleaning
    .filter(pl.col("price") > 0)
    .filter(pl.col("quantity").is_not_null())
    
    # Section 2: Feature engineering
    .with_columns(
        revenue=pl.col("price") * pl.col("quantity"),
        discount_rate=pl.col("discount") / pl.col("price"),
        is_high_value=pl.col("price") > 1000,
    )
    
    # Section 3: Aggregations
    .group_by(["region", "is_high_value"])
    .agg(
        total_revenue=pl.col("revenue").sum(),
        avg_discount=pl.col("discount_rate").mean(),
        transaction_count=pl.col("id").count(),
    )
    
    # Section 4: Post-processing
    .filter(pl.col("transaction_count") > 10)
    .sort(["region", "total_revenue"], descending=[False, True])
    .collect()
)
```

### 4. Use Comments for Intent, Not Mechanics

```python
# Good - Comments explain WHY
result = df.filter(
    pl.col("date") >= "2024-01-01"  # Focus on current year data
)

# Bad - Comments restate WHAT
result = df.filter(
    pl.col("date") >= "2024-01-01"  # Filter where date >= 2024-01-01
)

# Good - Section comments
df = (
    pl.read_csv("data.csv")
    
    # Remove invalid records before analysis
    .filter(pl.col("value").is_not_null())
    .filter(pl.col("value") > 0)
    
    # Calculate derived metrics
    .with_columns(
        normalized=pl.col("value") / pl.col("value").max(),
        category=pl.when(pl.col("value") > 100)
            .then("high")
            .otherwise("low"),
    )
)
```

## Naming Conventions for Clarity

### Expression Functions

Create reusable, named expression builders:

```python
# Good - Named expression functions
def get_revenue_growth(current: str, previous: str) -> pl.Expr:
    """Calculate YoY revenue growth as percentage."""
    return ((pl.col(current) - pl.col(previous)) / pl.col(previous) * 100).alias("growth_pct")

def get_is_high_value(threshold: float = 1000) -> pl.Expr:
    """Flag records above threshold."""
    return (pl.col("revenue") > threshold).alias("is_high_value")

# Use in clean, readable pipeline
result = (
    df.with_columns(
        get_revenue_growth("revenue_2024", "revenue_2023"),
        get_is_high_value(threshold=5000),
    )
    .filter(pl.col("is_high_value"))
)
```

### Transformation Stages

For complex pipelines, extract logical stages:

```python
def clean_data(df: pl.LazyFrame) -> pl.LazyFrame:
    """Remove invalid records and standardize formats."""
    return (
        df.filter(pl.col("value").is_not_null())
        .filter(pl.col("value") > 0)
        .with_columns(
            date=pl.col("date").str.to_date("%Y-%m-%d"),
            category=pl.col("category").str.to_uppercase(),
        )
    )

def add_features(df: pl.LazyFrame) -> pl.LazyFrame:
    """Calculate derived metrics."""
    return df.with_columns(
        revenue=pl.col("units") * pl.col("price"),
        margin=pl.col("revenue") - pl.col("cost"),
        margin_pct=(pl.col("margin") / pl.col("revenue") * 100),
    )

def aggregate_metrics(df: pl.LazyFrame) -> pl.LazyFrame:
    """Summarize by key dimensions."""
    return (
        df.group_by("category")
        .agg(
            total_revenue=pl.col("revenue").sum(),
            avg_margin=pl.col("margin_pct").mean(),
            transaction_count=pl.col("id").count(),
        )
        .filter(pl.col("transaction_count") > 10)
    )

# Composable pipeline
result = (
    pl.scan_csv("sales.csv")
    .pipe(clean_data)
    .pipe(add_features)
    .pipe(aggregate_metrics)
    .sort("total_revenue", descending=True)
    .collect()
)
```

## When to Break the Chain

### 1. Debugging Intermediate Results

```python
# Break to inspect (remove in production)
raw = pl.scan_csv("data.csv")
cleaned = raw.filter(pl.col("value").is_not_null())
print(cleaned.fetch(100))  # Preview first 100 rows

result = cleaned.with_columns(...).collect()
```

### 2. Conditional Logic

```python
# Sometimes conditionals are clearer outside the chain
df = pl.scan_csv("data.csv")

if filter_date:
    df = df.filter(pl.col("date") >= cutoff_date)

if add_features:
    df = df.with_columns(...)

result = df.collect()
```

### 3. Reusing Intermediate Results

```python
# When you need the same base for multiple outputs
base = (
    pl.scan_csv("sales.csv")
    .filter(pl.col("date") >= "2024-01-01")
    .with_columns(revenue=pl.col("units") * pl.col("price"))
)

# Branch 1: By region
by_region = base.group_by("region").agg(pl.col("revenue").sum()).collect()

# Branch 2: By product
by_product = base.group_by("product").agg(pl.col("revenue").sum()).collect()
```

## Formatting Guidelines

### Line Breaking

Break at method calls, align at parentheses:

```python
# Good - Break at method boundaries
result = (
    df.filter(pl.col("date") >= "2024-01-01")
    .with_columns(
        revenue=pl.col("units") * pl.col("price"),
        cost=pl.col("units") * pl.col("unit_cost"),
    )
    .group_by("region")
    .agg(
        total_revenue=pl.col("revenue").sum(),
        total_cost=pl.col("cost").sum(),
    )
    .with_columns(
        margin=pl.col("total_revenue") - pl.col("total_cost"),
        margin_pct=(pl.col("margin") / pl.col("total_revenue") * 100),
    )
    .sort("total_revenue", descending=True)
)

# Avoid - Breaking expressions mid-way
result = (
    df.filter(
        pl.col("date") >= "2024-01-01")
    .with_columns(revenue=pl.col("units") * 
        pl.col("price"))
)
```

### Vertical Alignment

Align related operations for scanning:

```python
# Good - Scan down the verbs
result = (
    df.filter(...)
    .with_columns(...)
    .group_by(...)
    .agg(...)
    .sort(...)
)

# Good - Scan down the aggregations
result = df.group_by("category").agg(
    total_sales=pl.col("sales").sum(),
    avg_sales=pl.col("sales").mean(),
    max_sales=pl.col("sales").max(),
    min_sales=pl.col("sales").min(),
    count=pl.col("id").count(),
)
```

## Lazy vs Eager in Pipelines

### Default to Lazy

```python
# Good - Lazy by default
result = (
    pl.scan_csv("data.csv")  # Returns LazyFrame
    .filter(pl.col("value") > 100)
    .with_columns(...)
    .collect()  # Execute at the end
)
```

### When to Use Eager

```python
# OK for small, exploratory data
df = pl.read_csv("small_sample.csv")  # Eager is fine

# OK for intermediate debugging
preview = df.head(100).collect()  # Materialize for inspection
```

### Streaming for Large Data

```python
# For data larger than RAM
result = (
    pl.scan_parquet("huge_dataset.parquet")
    .filter(pl.col("date") >= "2024-01-01")
    .collect(engine="streaming")  # Process in chunks
)
```

## Common Pipeline Patterns

### ETL Pattern

```python
result = (
    pl.scan_csv("raw_data.csv")
    
    # Extract - Select relevant columns
    .select(["id", "timestamp", "value", "category"])
    
    # Transform - Clean and enrich
    .filter(pl.col("value").is_not_null())
    .with_columns(
        date=pl.col("timestamp").str.to_datetime("%Y-%m-%d %H:%M:%S"),
        category=pl.col("category").str.to_uppercase().str.strip(),
        is_valid=pl.col("value") > 0,
    )
    .filter(pl.col("is_valid"))
    
    # Load-ready aggregation
    .group_by(["date", "category"])
    .agg(
        total_value=pl.col("value").sum(),
        record_count=pl.col("id").count(),
    )
    .sort(["date", "category"])
    .collect()
)
```

### Feature Engineering Pipeline

```python
def engineer_features(df: pl.DataFrame) -> pl.DataFrame:
    """Create features for ML model."""
    return (
        df.with_columns(
            # Temporal features
            day_of_week=pl.col("date").dt.weekday(),
            is_weekend=pl.col("date").dt.weekday().is_in([6, 7]),
            month=pl.col("date").dt.month(),
            
            # Numerical transformations
            log_value=pl.col("value").log(),
            value_squared=pl.col("value").pow(2),
            
            # Categorical encodings
            category_code=pl.col("category").cast(pl.Categorical).to_physical(),
            
            # Lag features
            value_lag1=pl.col("value").shift(1).over("category"),
            value_diff=pl.col("value") - pl.col("value").shift(1).over("category"),
        )
        .with_columns(
            # Derived features
            value_ma7=pl.col("value").rolling_mean(7).over("category"),
            is_high_value=pl.col("value") > pl.col("value").mean().over("category"),
        )
    )
```

## Testing Pipelines

### Unit Test Expression Functions

```python
def test_growth_calculation():
    df = pl.DataFrame({
        "current": [110, 200, 50],
        "previous": [100, 100, 100],
    })
    
    result = df.with_columns(
        get_revenue_growth("current", "previous")
    )
    
    assert result["growth_pct"].to_list() == [10.0, 100.0, -50.0]
```

### Integration Test Pipelines

```python
def test_sales_pipeline():
    input_df = pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "price": [10.0, 20.0],
        "quantity": [2, 3],
    })
    
    result = (
        input_df.with_columns(
            revenue=pl.col("price") * pl.col("quantity")
        )
        .group_by("date")
        .agg(pl.col("revenue").sum())
    )
    
    assert result.shape == (2, 2)
    assert result["revenue"].sum() == 80.0
```

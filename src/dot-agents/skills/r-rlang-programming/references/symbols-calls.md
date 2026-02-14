# Symbols and Calls Reference

Tools for creating and manipulating R code objects programmatically.

## Symbols

Symbols represent variable names in R.

### Creating Symbols

#### `sym()` - Single Symbol

```r
# From string
var_name <- "mpg"
s <- sym(var_name)
#> mpg

# Use in expressions
expr(mean(!!s))
#> mean(mpg)
```

#### `syms()` - Multiple Symbols

```r
# From character vector
col_names <- c("mpg", "cyl", "hp")
symbols <- syms(col_names)
#> [[1]]
#> mpg
#> [[2]]
#> cyl
#> [[3]]
#> hp

# Use with splicing
expr(select(!!!symbols))
#> select(mpg, cyl, hp)
```

#### `data_sym()` / `data_syms()` - Data Symbols

For data-masking contexts, though regular `sym()` usually works:

```r
col <- data_sym("mpg")
dplyr::select(mtcars, !!col)
```

### Testing Symbols

```r
is_symbol(expr(x))      # TRUE
is_symbol(expr(1))      # FALSE
is_symbol(expr(f()))    # FALSE

# Check specific name
x_sym <- sym("x")
identical(x_sym, sym("x"))  # TRUE
```

### Converting Symbols

```r
# Symbol to string
s <- sym("my_var")
as_string(s)
#> [1] "my_var"

as_name(s)  # Same as as_string() for symbols
#> [1] "my_var"

# String to symbol (use sym() instead)
```

### Symbols in Base R

```r
# rlang
sym("x")

# Base R equivalent
as.symbol("x")
as.name("x")  # Identical to as.symbol()
```

## Calls

Calls represent function invocations.

### Creating Calls

#### `call2()` - Build Call

```r
# Basic call
call2("mean", sym("x"))
#> mean(x)

# With arguments
call2("mean", sym("x"), na.rm = TRUE, trim = 0.1)
#> mean(x, na.rm = TRUE, trim = 0.1)

# Operator calls
call2("+", 1, 2)
#> 1 + 2

call2("<-", sym("x"), 10)
#> x <- 10
```

#### Function as First Argument

```r
# Can pass function directly
call2(mean, sym("x"), na.rm = TRUE)
#> mean(x, na.rm = TRUE)

# Useful for anonymous functions
call2(function(x) x + 1, 5)
```

#### With Namespace

```r
# Explicit namespace
call2("filter", sym("df"), .ns = "dplyr")
#> dplyr::filter(df)

# Using ::: for internal functions
call2("internal_fn", .ns = c("pkg", ":::", "internal"))
```

#### Splicing Arguments

```r
args <- list(na.rm = TRUE, trim = 0.1)
call2("mean", sym("x"), !!!args)
#> mean(x, na.rm = TRUE, trim = 0.1)
```

### Inspecting Calls

#### `call_name()` - Function Name

```r
cl <- expr(mean(x, na.rm = TRUE))
call_name(cl)
#> [1] "mean"

# For operators
cl <- expr(x + y)
call_name(cl)
#> [1] "+"
```

#### `call_ns()` - Namespace

```r
cl <- expr(dplyr::filter(df))
call_ns(cl)
#> [1] "dplyr"

# NULL if no namespace
cl <- expr(mean(x))
call_ns(cl)
#> NULL
```

#### `call_args()` - Arguments List

```r
cl <- expr(mean(x, na.rm = TRUE, trim = 0.1))
call_args(cl)
#> [[1]]
#> x
#>
#> $na.rm
#> [1] TRUE
#>
#> $trim
#> [1] 0.1
```

#### `call_args_names()` - Argument Names

```r
cl <- expr(mean(x, na.rm = TRUE, trim = 0.1))
call_args_names(cl)
#> [1] ""       "na.rm"  "trim"

# Empty string for unnamed positional args
```

### Testing Calls

#### `is_call()` - Is it a Call?

```r
is_call(expr(f()))      # TRUE
is_call(expr(x + y))    # TRUE (operator call)
is_call(expr(x))        # FALSE (symbol)
is_call(expr(1))        # FALSE (constant)
```

#### `is_call()` with Name Match

```r
# Test specific function
is_call(expr(mean(x)), "mean")           # TRUE
is_call(expr(sum(x)), "mean")            # FALSE

# Test multiple functions
is_call(expr(sum(x)), c("mean", "sum"))  # TRUE

# Test namespace too
is_call(expr(dplyr::filter(x)), "filter", ns = "dplyr")  # TRUE
```

#### `is_call_simple()` - Simple Call?

Test if call is "simple" (no nested calls):

```r
is_call_simple(expr(f(x, y)))        # TRUE
is_call_simple(expr(f(g(x), y)))     # FALSE (nested)
is_call_simple(expr(f(x + y)))       # FALSE (operator is nested call)
```

### Modifying Calls

#### `call_modify()` - Change Arguments

```r
cl <- expr(mean(x, na.rm = TRUE))

# Change existing argument
call_modify(cl, na.rm = FALSE)
#> mean(x, na.rm = FALSE)

# Add new argument
call_modify(cl, trim = 0.1)
#> mean(x, na.rm = TRUE, trim = 0.1)

# Remove argument (use NULL)
call_modify(cl, na.rm = NULL)
#> mean(x)

# Change multiple
call_modify(cl, na.rm = FALSE, trim = 0.1)
```

#### `call_standardise()` - Match to Definition

Match call against function signature:

```r
# Partial/positional args become explicit
cl <- expr(mean(x, T, 0.1))
call_standardise(cl)
#> mean(x = x, trim = 0.1, na.rm = TRUE)

# Useful before manipulating calls
```

### Evaluating Calls

```r
# Create and evaluate
cl <- call2("mean", 1:10, na.rm = TRUE)
eval(cl)
#> [1] 5.5

# With specific environment
cl <- call2("mean", sym("x"))
eval(cl, envir = list(x = 1:10))
#> [1] 5.5
```

## Advanced Call Patterns

### Building Complex Expressions

```r
# Build nested call
inner <- call2("sqrt", sym("x"))
outer <- call2("mean", inner)
#> mean(sqrt(x))

# With operators
base <- sym("x")
squared <- call2("^", base, 2)
sum_squared <- call2("sum", squared)
#> sum(x^2)
```

### Transforming Expressions

```r
# Add na.rm to all mean() calls
add_na_rm <- function(expr) {
  if (is_call(expr, "mean")) {
    call_modify(expr, na.rm = TRUE)
  } else if (is_call(expr)) {
    # Recurse into arguments
    expr[] <- lapply(expr, add_na_rm)
    expr
  } else {
    expr
  }
}

e <- expr(mean(x) + mean(y))
add_na_rm(e)
#> mean(x, na.rm = TRUE) + mean(y, na.rm = TRUE)
```

### Call Inspection

```r
# Print call structure
call_inspect(expr(mean(x, na.rm = TRUE)))
#> call mean
#>   args x, na.rm = TRUE

# Useful for debugging complex expressions
```

### Dynamic Function Calls

```r
# Function name from variable
fn_name <- "mean"
args <- list(sym("x"), na.rm = TRUE)

call2(fn_name, !!!args)
#> mean(x, na.rm = TRUE)
```

### Operator Calls

```r
# Build operator expressions
call2("+", sym("x"), sym("y"))
#> x + y

call2("==", sym("status"), "active")
#> status == "active"

call2("[", sym("df"), sym("i"), )
#> df[i, ]

# Pipe operator
call2("%>%", sym("df"), call2("filter", sym("x") > 10))
#> df %>% filter(x > 10)
```

## Expression Lists

### `exprs()` - Create List of Expressions

```r
# Multiple expressions
exprs(x, y, z + 1)
#> [[1]]
#> x
#> [[2]]
#> y
#> [[3]]
#> z + 1

# Named
exprs(a = x + 1, b = y + 2)

# With injection
var <- sym("mpg")
exprs(first = !!var, second = cyl)
```

### `exprs_auto_name()` - Add Default Names

```r
# Auto-name unnamed expressions
es <- exprs(x, y + 1, mean(z))
exprs_auto_name(es)
#> $x
#> x
#>
#> $`y + 1`
#> y + 1
#>
#> $`mean(z)`
#> mean(z)
```

## Labeling and Naming

### `as_label()` - Expression to Label

Create human-readable label:

```r
as_label(expr(x))
#> [1] "x"

as_label(expr(mean(x, na.rm = TRUE)))
#> [1] "mean(x, na.rm = TRUE)"

# Useful for plot labels, column names
ggplot2::labs(x = as_label(enquo(xvar)))
```

### `as_name()` - Expression to String Name

Stricter than `as_label()`, requires simple expression:

```r
as_name(expr(x))
#> [1] "x"

as_name(sym("x"))
#> [1] "x"

as_name(expr(x + 1))
#> Error: must be a string or symbol
```

## Parsing Code

### `parse_expr()` - String to Expression

```r
# Single expression
code <- "mean(x, na.rm = TRUE)"
parse_expr(code)
#> mean(x, na.rm = TRUE)

# Evaluate it
eval(parse_expr(code), envir = list(x = 1:10))
#> [1] 5.5
```

### `parse_exprs()` - Multiple Expressions

```r
code <- "
  x <- 1:10
  y <- mean(x)
  y * 2
"

exprs <- parse_exprs(code)
#> [[1]]
#> x <- 1:10
#> [[2]]
#> y <- mean(x)
#> [[3]]
#> y * 2

# Evaluate in sequence
env <- new.env()
for (e in exprs) eval(e, env)
env$y
#> [1] 11
```

### `parse_quo()` / `parse_quos()` - To Quosures

```r
# Parse to quosure (with environment)
q <- parse_quo("mean(x)", env = global_env())

# Useful when combining parsing with tidy eval
```

## Printing and Deparsing

### `expr_print()` - Pretty Print

```r
e <- expr({
  x <- 1:10
  mean(x)
})

expr_print(e)
#> {
#>     x <- 1:10
#>     mean(x)
#> }
```

### `expr_deparse()` - Expression to String

```r
e <- expr(mean(x, na.rm = TRUE))
expr_deparse(e)
#> [1] "mean(x, na.rm = TRUE)"

# Multiple lines for long expressions
long_expr <- expr(very_long_function_name(
  argument1 = value1,
  argument2 = value2
))
expr_deparse(long_expr)
#> [1] "very_long_function_name(argument1 = value1, argument2 = value2)"
```

## Common Patterns

### Building Filter Expressions

```r
build_filter <- function(col, op, value) {
  call2(op, sym(col), value)
}

# Use
build_filter("age", ">", 18)
#> age > 18

build_filter("status", "==", "active")
#> status == "active"

# Inject into filter
filter_expr <- build_filter("age", ">", 18)
dplyr::filter(df, !!filter_expr)
```

### Combining Conditions

```r
combine_conditions <- function(..., op = "&") {
  conditions <- list2(...)

  if (length(conditions) == 0) return(TRUE)
  if (length(conditions) == 1) return(conditions[[1]])

  # Combine pairwise
  result <- conditions[[1]]
  for (i in seq(2, length(conditions))) {
    result <- call2(op, result, conditions[[i]])
  }
  result
}

# Use
cond1 <- expr(age > 18)
cond2 <- expr(status == "active")
cond3 <- expr(score > 0.5)

combine_conditions(cond1, cond2, cond3)
#> age > 18 & status == "active" & score > 0.5
```

### Dynamic Column Creation

```r
create_columns <- function(data, col_specs) {
  # col_specs: named list of expressions
  for (name in names(col_specs)) {
    data <- dplyr::mutate(
      data,
      !!name := !!col_specs[[name]]
    )
  }
  data
}

# Use
specs <- list(
  age_months = expr(age * 12),
  is_adult = expr(age >= 18)
)
create_columns(df, specs)
```

### Negating Expressions

```r
negate_expr <- function(expr) {
  call2("!", expr)
}

# Use
filter_expr <- expr(x > 10)
negated <- negate_expr(filter_expr)
#> !(x > 10)
```

### Expression Walking

```r
# Find all symbols in expression
find_symbols <- function(expr) {
  if (is_symbol(expr)) {
    as_string(expr)
  } else if (is_call(expr)) {
    # Recurse into call arguments
    unique(unlist(lapply(call_args(expr), find_symbols)))
  } else {
    character()
  }
}

find_symbols(expr(mean(x + y, na.rm = TRUE)))
#> [1] "x" "y"
```

## Best Practices

1. **Use `call2()` over manual construction** - More reliable
2. **Store symbols, not strings** - Symbols are proper R objects
3. **Use `as_label()` for display** - Not for programmatic names
4. **Validate before eval** - Don't blindly evaluate user code
5. **Prefer `syms()` + `!!!`** - Over loop with `sym()`
6. **Test call structure** - Verify before evaluation
7. **Handle edge cases** - Empty lists, NULL, missing names

## Base R Comparison

| rlang           | Base R                     |
| --------------- | -------------------------- |
| `sym()`         | `as.symbol()`, `as.name()` |
| `call2()`       | `call()`, `as.call()`      |
| `is_symbol()`   | `is.symbol()`, `is.name()` |
| `is_call()`     | `is.call()`                |
| `as_string()`   | `as.character()`           |
| `call_args()`   | `as.list(x)[-1]`           |
| `call_name()`   | `as.character(x[[1]])`     |
| `call_modify()` | Manual list manipulation   |

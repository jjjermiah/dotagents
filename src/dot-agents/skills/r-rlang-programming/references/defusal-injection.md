# Defusal and Injection Reference

Core metaprogramming concepts in rlang.

## Defusal (Quoting)

**Defusal** means capturing R code without evaluating it. The code becomes data that can be inspected, modified, and evaluated later.

### Basic Defusal

```r
# Normal evaluation
1 + 1
#> [1] 2

# Defused - returns the expression
expr(1 + 1)
#> 1 + 1

# Resume evaluation later
e <- expr(1 + 1)
eval(e)
#> [1] 2
```

### Types of Defused Expressions

1. **Calls** - Function calls

   ```r
   expr(mean(x, na.rm = TRUE))
   ```

2. **Symbols** - Variable names

   ```r
   expr(my_var)
   sym("my_var")
   ```

3. **Constants** - Literal values
   ```r
   expr(42)
   expr(NULL)
   ```

### Local vs Argument Defusal

#### Local Expressions with `expr()`

Defuse your own code:

```r
my_expr <- expr(x + y)
my_call <- expr(mean(x, na.rm = TRUE))
my_symbol <- expr(variable_name)
```

#### Function Arguments with `enquo()`

Defuse user-supplied arguments:

```r
my_function <- function(arg) {
  # Capture what the user passed
  user_expr <- enquo(arg)

  # Inspect it
  print(user_expr)

  # Inject it somewhere
  dplyr::filter(df, !!user_expr)
}

# User calls with bare expression
my_function(x > 10)
```

#### Multiple Arguments with `enquos()`

```r
my_select <- function(...) {
  cols <- enquos(...)
  dplyr::select(df, !!!cols)
}

my_select(x, y, z)
```

### Special Defusal: `enquo0()` and `enquos0()`

These disable injection - useful for DSL implementation where you don't want users to inject:

```r
strict_function <- function(arg) {
  # This prevents {{ }} and !! from working
  arg_expr <- enquo0(arg)
  # ... use arg_expr ...
}
```

## Injection (Unquoting)

**Injection** means inserting an expression into another expression or evaluation context.

### Why Inject?

Without injection, you get the wrong code:

```r
make_filter <- function(data, condition) {
  # This literally filters for `condition > 10`, not what's in `condition`
  dplyr::filter(data, condition > 10)
}
```

With injection:

```r
make_filter <- function(data, condition) {
  condition <- enquo(condition)
  # Inject the actual expression the user passed
  dplyr::filter(data, !!condition)
}

make_filter(mtcars, mpg)
# Correctly filters for `mpg > 10`
```

### Injection Operators

#### `!!` - Inject Single Expression

```r
# Inject a symbol
var <- sym("mpg")
dplyr::select(mtcars, !!var)

# Inject a call
filter_expr <- expr(cyl == 6)
dplyr::filter(mtcars, !!filter_expr)

# Inject computed value
threshold <- 20
dplyr::filter(mtcars, mpg > !!threshold)
```

#### `!!!` - Inject Multiple Expressions (Splice)

```r
# Splice list of symbols
cols <- syms(c("mpg", "cyl", "hp"))
dplyr::select(mtcars, !!!cols)

# Splice function arguments
args <- list(na.rm = TRUE, trim = 0.1)
mean(x, !!!args)

# Build dynamic group_by
group_vars <- exprs(cyl, gear)
mtcars %>% dplyr::group_by(!!!group_vars)
```

#### `{{` - Embrace (Defuse + Inject)

Shorthand for `enquo()` + `!!`:

```r
# Manual way
my_fn <- function(data, var) {
  var <- enquo(var)
  dplyr::summarise(data, mean = mean(!!var))
}

# With embrace
my_fn <- function(data, var) {
  dplyr::summarise(data, mean = mean({{ var }}))
}
```

### Name Injection

#### `"{var}"` - Inject String as Name

```r
name <- "result"
mtcars %>% dplyr::summarise("{name}" := mean(mpg))
#> # A tibble: 1 × 1
#>   result
#>    <dbl>
#> 1   20.1
```

#### `"{{var}}"` - Inject Expression as Name

```r
summarise_var <- function(data, var) {
  data %>%
    dplyr::summarise("mean_{{ var }}" := mean({{ var }}))
}

mtcars %>% summarise_var(mpg)
#> # A tibble: 1 × 1
#>   mean_mpg
#>      <dbl>
#> 1     20.1
```

### `:=` Operator

Use `:=` instead of `=` when left-hand side is computed:

```r
# Won't work with `=`
dplyr::mutate(df, "{name}" = value)  # Error

# Works with `:=`
dplyr::mutate(df, "{name}" := value)
```

## `inject()` Function

Explicit injection context - useful when the function doesn't support injection by default:

```r
# Enable injection in any expression
result <- inject(
  mean(!!!args, na.rm = !!remove_na)
)

# Useful with base R functions
inject(rbind(!!!list_of_dfs))
```

## Quosures

When you defuse function arguments with `enquo()`, you get a **quosure** (expression + environment):

```r
f <- function(arg) {
  enquo(arg)
}

# Returns quosure with environment info
f(x + y)
#> <quosure>
#> expr: ^x + y
#> env:  global
```

### Why Quosures Matter

They preserve the context where the expression was created:

```r
make_filter <- function(threshold) {
  # `threshold` is defined here
  function(data, var) {
    # But used here - quosure tracks this
    dplyr::filter(data, {{ var }} > threshold)
  }
}

filter_20 <- make_filter(20)
filter_20(mtcars, mpg)  # Works because quosure remembers `threshold`
```

### Working with Quosures

```r
# Extract expression
q <- quo(x + 1)
quo_get_expr(q)
#> x + 1

# Extract environment
quo_get_env(q)
#> <environment: global>

# Modify expression
quo_set_expr(q, expr(y + 2))

# Test structure
quo_is_call(q)
quo_is_symbol(q)
```

## Building Expressions from Data

### Create Symbols

```r
# From string
var_name <- "mpg"
sym(var_name)
#> mpg

# Multiple
var_names <- c("mpg", "cyl")
syms(var_names)
#> [[1]]
#> mpg
#> [[2]]
#> cyl

# Data symbols (for data-masking)
data_sym("mpg")
```

### Create Calls

```r
# Programmatically build function calls
call2("mean", sym("x"), na.rm = TRUE)
#> mean(x, na.rm = TRUE)

# With expressions
call2("+", expr(a), expr(b))
#> a + b

# Dynamic function name
fn <- "sum"
call2(fn, sym("x"))
#> sum(x)
```

### Create Lists of Expressions

```r
# Literal expressions
exprs(x, y, z + 1)
#> [[1]]
#> x
#> [[2]]
#> y
#> [[3]]
#> z + 1

# From data
vars <- c("a", "b", "c")
exprs(!!!syms(vars))
```

## Evaluation

### `eval_tidy()`

Evaluate with quosure support and data masking:

```r
expr <- quo(mean(mpg))
eval_tidy(expr, data = mtcars)
#> [1] 20.09062

# With data mask
eval_tidy(expr(cyl + am), data = mtcars)
```

### `eval_bare()`

Basic evaluation without quosure/pronoun support:

```r
eval_bare(expr(1 + 1))
#> [1] 2

# In specific environment
eval_bare(expr(x), env = list(x = 10))
#> [1] 10
```

### `exec()`

Call a function with dynamic arguments:

```r
# Equivalent to mean(x, na.rm = TRUE, trim = 0.1)
exec("mean", x, na.rm = TRUE, trim = 0.1)

# With splicing
args <- list(na.rm = TRUE, trim = 0.1)
exec("mean", x, !!!args)
```

## Debugging Injection

### `qq_show()`

See what an expression looks like after injection:

```r
var <- sym("mpg")
qq_show(
  dplyr::select(mtcars, !!var, cyl)
)
#> dplyr::select(mtcars, mpg, cyl)

# With splicing
vars <- syms(c("mpg", "cyl"))
qq_show(
  dplyr::select(mtcars, !!!vars)
)
#> dplyr::select(mtcars, mpg, cyl)
```

## Common Patterns

### Transform and Inject

```r
transform_filter <- function(data, var, op, value) {
  var <- ensym(var)
  # Build the expression
  condition <- call2(op, var, value)
  # Inject it
  dplyr::filter(data, !!condition)
}

transform_filter(mtcars, mpg, ">", 20)
```

### Multiple Operations

```r
apply_filters <- function(data, ...) {
  conditions <- enquos(...)

  for (condition in conditions) {
    data <- dplyr::filter(data, !!condition)
  }

  data
}

apply_filters(mtcars, mpg > 20, cyl == 6)
```

### Expression Modification

```r
negate_condition <- function(data, condition) {
  condition <- enquo(condition)

  # Build negated version
  negated <- call2("!", condition)

  dplyr::filter(data, !!negated)
}

negate_condition(mtcars, mpg > 20)
# Filters for mpg <= 20
```

## Base R Comparison

| rlang         | Base R                  |
| ------------- | ----------------------- |
| `expr()`      | `quote()`, `bquote()`   |
| `enquo()`     | `substitute()`          |
| `enquos(...)` | `substitute(list(...))` |
| `!!`          | `bquote(.(x))`          |
| `!!!`         | No direct equivalent    |
| `eval_tidy()` | `eval()`                |

**Key advantage of rlang:** Consistent syntax, quosures for hygiene, better error messages.

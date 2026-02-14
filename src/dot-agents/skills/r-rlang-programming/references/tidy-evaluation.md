# Tidy Evaluation Reference

Tidy evaluation (tidy eval) is rlang's programmable data-masking framework.

## Core Concepts

### Data Masking

Data-masking allows programming directly on data frames, where columns are treated as normal objects:

```r
# Standard R - need to reference the data frame
mean(mtcars$cyl + mtcars$am)

# Data-masked - columns are available directly
with(mtcars, mean(cyl + am))
```

**How it works:**

1. User code is defused (captured without evaluation)
2. A data mask environment is created from the data frame
3. The defused code is evaluated in this mask, where columns become variables
4. The mask takes precedence over the user environment

### The Problem Tidy Eval Solves

Passing data-masked arguments requires special handling:

```r
# This FAILS - `var1` and `var2` are not defined
my_mean <- function(data, var1, var2) {
  dplyr::summarise(data, mean(var1 + var2))
}

# This WORKS - embrace operator injects the arguments
my_mean <- function(data, var1, var2) {
  dplyr::summarise(data, mean({{ var1 }} + {{ var2 }}))
}
```

## Essential Operators

### Embracing Operator `{{`

The embrace operator (curly-curly) is the primary tool for passing data-masked arguments:

```r
mean_by <- function(data, by, var) {
  data %>%
    dplyr::group_by({{ by }}) %>%
    dplyr::summarise(avg = mean({{ var }}, na.rm = TRUE))
}

mtcars %>% mean_by(by = cyl, var = disp)
```

**When to use:** Whenever you write a function that wraps data-masking functions and takes bare column names.

**How it works:** Combines defusal (`enquo()`) and injection (`!!`) in one step.

### Injection Operator `!!`

Inject a single expression or symbol:

```r
# Inject a data-symbol
var <- data_sym("disp")
mtcars %>% dplyr::summarise(avg = mean(!!var, na.rm = TRUE))

# Inject by value to avoid name collision
x <- 100
df %>% dplyr::mutate(x = x / !!x)
```

**When to use:**

- Programmatically constructed symbols/calls
- Avoiding variable name collisions
- More control than `{{` provides

### Splice Operator `!!!`

Inject a list of arguments:

```r
# Splice multiple grouping variables
group_vars <- syms(c("cyl", "am"))
mtcars %>% dplyr::group_by(!!!group_vars)

# Splice named arguments
args <- list(na.rm = TRUE, trim = 0.1)
mean(x, !!!args)
```

**When to use:** Dynamic number of arguments, often from user input or configuration.

### Name Injection with `"{"`

Inject variable names using glue syntax:

```r
name <- "avg_mpg"
mtcars %>% dplyr::summarise("{name}" := mean(mpg))

# With prefix/suffix
mtcars %>% dplyr::summarise("mean_{name}" := mean(mpg))
```

**When to use:** Column names are computed or come from variables.

### Name Injection with `"{{"`

Combine embracing with name injection:

```r
summary_var <- function(data, var) {
  data %>% dplyr::summarise("mean_{{ var }}" := mean({{ var }}))
}

mtcars %>% summary_var(mpg)
# Returns: mean_mpg
```

## Data Pronouns

Disambiguate between data frame columns and environment variables:

```r
cyl <- 1000  # environment variable

mtcars %>%
  dplyr::summarise(
    mean_data = mean(.data$cyl),    # Column: 6.19
    mean_env = mean(.env$cyl)       # Env var: 1000
  )
```

**`.data`** - Forces lookup in data frame only
**`.env`** - Forces lookup in environment only

**When to use:** Avoiding ambiguity in production code, especially when variable names might overlap.

## Defusal and Injection Pattern

### Manual defuse-and-inject

```r
my_summarise <- function(data, arg) {
  # 1. Defuse the user expression
  arg <- enquo(arg)

  # 2. Inject it where needed
  data %>% dplyr::summarise(mean = mean(!!arg, na.rm = TRUE))
}
```

### With embrace (recommended)

```r
my_summarise <- function(data, arg) {
  # Defuse and inject in one step
  data %>% dplyr::summarise(mean = mean({{ arg }}, na.rm = TRUE))
}
```

### When to use manual approach

Use `enquo()` + `!!` when you need to:

- Inspect or modify the defused expression
- Use the expression multiple times in different ways
- Apply transformations before injection

## Common Patterns

### Passing multiple columns with `...`

```r
group_summary <- function(data, ..., var) {
  data %>%
    dplyr::group_by(...) %>%
    dplyr::summarise(mean = mean({{ var }}))
}

mtcars %>% group_summary(cyl, am, var = mpg)
```

### Optional grouping

```r
optional_group <- function(data, var, by = NULL) {
  if (!missing(by)) {
    data <- dplyr::group_by(data, {{ by }})
  }
  dplyr::summarise(data, mean = mean({{ var }}))
}
```

### Dynamic column selection

```r
select_cols <- function(data, ...) {
  cols <- enquos(...)
  dplyr::select(data, !!!cols)
}
```

### Building complex expressions

```r
standardize_var <- function(data, var) {
  var_expr <- enquo(var)

  data %>%
    dplyr::mutate(
      # Use the expression multiple times
      centered = !!var_expr - mean(!!var_expr),
      scaled = centered / sd(!!var_expr)
    )
}
```

## Testing Tidy Eval Code

```r
test_that("function handles bare names", {
  result <- my_summarise(mtcars, cyl)
  expect_equal(result$mean, mean(mtcars$cyl))
})

test_that("function handles expressions", {
  result <- my_summarise(mtcars, cyl + am)
  expect_equal(result$mean, mean(mtcars$cyl + mtcars$am))
})
```

## Common Errors and Solutions

### Error: object 'var' not found

**Problem:** Forgot to use `{{` or `!!`

```r
# Wrong
my_fn <- function(data, var) {
  dplyr::filter(data, var > 10)
}

# Right
my_fn <- function(data, var) {
  dplyr::filter(data, {{ var }} > 10)
}
```

### Error: Can't subset `.data` outside data mask

**Problem:** Using `.data` in wrong context

```r
# Wrong - .data only works inside data-masking
var <- ".data$cyl"
dplyr::select(mtcars, !!var)

# Right
var <- "cyl"
dplyr::select(mtcars, !!var)
```

## Base R Equivalents

| rlang         | Base R                         |
| ------------- | ------------------------------ |
| `enquo(x)`    | `substitute(x)`                |
| `enquos(...)` | `eval(substitute(alist(...)))` |
| `eval_tidy()` | `eval()`                       |
| `expr()`      | `bquote()`                     |

**Key difference:** rlang uses quosures (expression + environment) for hygiene, base R uses naked expressions.

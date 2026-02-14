# Function Arguments Reference

Tools for robust argument handling, validation, and dynamic dots.

## Argument Validation

### `arg_match()` - Match to Character Vector

Validate argument against allowed values:

```r
my_function <- function(method = c("fast", "accurate", "balanced")) {
  method <- arg_match(method)
  # method is now guaranteed to be one of the three options
}

my_function("fast")      # OK
my_function("accurate")  # OK
my_function("wrong")     # Error with helpful message
```

**Features:**

- First value is default
- Partial matching supported
- Clear error messages listing valid options
- Handles `NULL` if included in choices

### `arg_match0()` - Exact Matching

Like `arg_match()` but no partial matching:

```r
choose_color <- function(color = c("red", "blue", "green")) {
  arg_match0(color)
}

choose_color("r")  # Error (no partial match)
choose_color("red")  # OK
```

### `check_required()` - Required Argument

Ensure argument was supplied:

```r
process_data <- function(data, output_file) {
  check_required(output_file)
  # output_file is guaranteed to be supplied
}

process_data(df)  # Error: argument "output_file" is missing
```

### `is_missing()` - Test If Missing

```r
my_function <- function(x, y = NULL) {
  if (is_missing(x)) {
    abort("`x` is required")
  }

  # Different from is.null()
  if (is_missing(y)) {
    message("Using default for y")
  }
}
```

### `missing_arg()` - Create Missing Argument

```r
# Create a true missing argument
x <- missing_arg()
is_missing(x)  # TRUE

# Useful for programmatic function creation
fn <- new_function(
  exprs(x = missing_arg(), y = 10),
  expr({ x + y })
)
```

## Dynamic Dots

Dynamic dots (`...`) support injection operators and name-injection.

### Enabling Dynamic Dots

Collect `...` with `list2()` or `dots_list()`:

```r
my_function <- function(...) {
  args <- list2(...)
  # args now contains captured dots with injection support
}
```

### Dot Features

All these work when using dynamic dots:

```r
my_function(
  # Splicing with !!!
  !!!list(x = 1, y = 2),

  # Name injection with "{"
  "{name}" := value,

  # Name injection with :=
  !!name := value,

  # Regular arguments
  z = 3
)
```

### `:=` Assignment Operator

Use when left-hand side is computed:

```r
name <- "dynamic_col"

# Won't work with =
dplyr::mutate(df, name = x + 1)     # Creates column "name"

# Works with :=
dplyr::mutate(df, !!name := x + 1)  # Creates column "dynamic_col"
dplyr::mutate(df, "{name}" := x + 1)  # Same result
```

## Checking Dots

### `check_dots_empty()` - No Extra Arguments

Ensure caller didn't pass unexpected arguments:

```r
my_function <- function(x, y, ...) {
  check_dots_empty()
  # Error if anything in ...
}

my_function(1, 2)              # OK
my_function(1, 2, z = 3)       # Error: ... must be empty
my_function(1, 2, 3)           # Error with helpful message
```

**When to use:** Functions where `...` exists only for S3 consistency or passing to one specific function.

### `check_dots_used()` - All Dots Consumed

Ensure all dots were actually used:

```r
my_wrapper <- function(...) {
  result <- mean(..., na.rm = TRUE)
  check_dots_used()
  result
}

my_wrapper(1:10, na.rm = TRUE)  # OK
my_wrapper(1:10, trim = 0.1)    # Error: `trim` not used
```

**When to use:** Wrapper functions to catch typos in argument names.

### `check_dots_unnamed()` - No Names in Dots

Ensure dots contain only positional arguments:

```r
combine <- function(...) {
  check_dots_unnamed()
  c(...)
}

combine(1, 2, 3)          # OK
combine(a = 1, b = 2)     # Error: ... must be unnamed
```

**When to use:** Functions expecting data values, not arguments.

## Collecting Dynamic Dots

### `list2()` - Dots to List

```r
my_rbind <- function(...) {
  rows <- list2(...)
  do.call(rbind, rows)
}

# Regular usage
my_rbind(a = 1:2, b = 3:4)

# With splicing
rows <- list(a = 1:2, b = 3:4)
my_rbind(!!!rows, c = 5:6)

# With name injection
name <- "row_a"
my_rbind("{name}" := 1:2)
```

### `dots_list()` - Advanced Dot Collection

More control than `list2()`:

```r
my_function <- function(...) {
  dots_list(
    ...,
    .ignore_empty = "all",      # Ignore empty arguments
    .preserve_empty = FALSE,    # Remove NULL/missing
    .homonyms = "error",        # Error on duplicate names
    .check_assign = TRUE        # Check for = vs :=
  )
}
```

**Options:**

- `.ignore_empty`: `"none"`, `"trailing"`, `"all"`
- `.preserve_empty`: Keep `NULL`/missing?
- `.homonyms`: `"error"`, `"first"`, `"last"`, `"keep"`
- `.check_assign`: Error if `:=` used incorrectly?

### `pairlist2()` - Dots to Pairlist

For function formals (usually internal use):

```r
# Create function programmatically
formals <- pairlist2(
  x = ,           # Required
  y = 10,         # Default
  ... =
)

new_function(formals, body)
```

### `splice()` - Mark for Splicing

Explicitly mark list for splicing:

```r
# Instead of:
call2("fn", !!!list(a = 1, b = 2))

# Can use:
call2("fn", splice(list(a = 1, b = 2)))
```

## Exclusive Arguments

### `check_exclusive()` - Mutual Exclusivity

Ensure only one of several arguments supplied:

```r
get_data <- function(id = NULL, name = NULL, index = NULL) {
  check_exclusive(id, name, index)
  # Exactly one must be supplied
}

get_data(id = 1)              # OK
get_data(name = "foo")        # OK
get_data(id = 1, name = "foo")  # Error
get_data()                    # Error
```

**Variations:**

```r
# At least one required
check_exclusive(x, y, .require = TRUE)

# OK if none supplied
check_exclusive(x, y, .require = FALSE)
```

## Argument Names

### Getting Caller's Argument Name

```r
my_check <- function(x, arg = caller_arg(x)) {
  if (!is.numeric(x)) {
    abort("`{arg}` must be numeric")
  }
}

validate <- function(user_value) {
  my_check(user_value)  # Error mentions "user_value"
}
```

**Benefits:**

- No need to pass `arg = "..."` manually
- Works with complex expressions
- Handles renaming gracefully

### Argument Context for Errors

```r
check_type <- function(x,
                       type,
                       arg = caller_arg(x),
                       call = caller_env()) {
  if (!inherits(x, type)) {
    cli::cli_abort(
      "{.arg {arg}} must be a {.cls {type}}",
      call = call
    )
  }
}

# Use in function
process <- function(data) {
  check_type(data, "data.frame")
  # Error will say "`data` must be a <data.frame>"
  # Error will show "Error in `process()`:"
}
```

## Common Patterns

### Flexible Input Types

```r
accept_flexible <- function(x, ...) {
  # Accept both direct arguments and list
  if (is_missing(x)) {
    x <- list2(...)
  } else if (!is.list(x)) {
    # Single value - make list
    x <- list(x, ...)
  } else {
    # List provided - splice any additional args
    x <- c(x, list2(...))
  }

  x
}

accept_flexible(1, 2, 3)           # list(1, 2, 3)
accept_flexible(list(1, 2), 3)     # list(1, 2, 3)
accept_flexible(x = list(1, 2, 3)) # list(1, 2, 3)
```

### Optional Named Arguments

```r
with_options <- function(code, ...) {
  # Collect optional settings
  opts <- dots_list(..., .homonyms = "first")

  # Apply temporarily
  if (length(opts) > 0) {
    local_options(!!!opts)
  }

  force(code)
}

with_options({
  # code
}, digits = 3, warn = -1)
```

### Forwarding to Multiple Functions

```r
multi_forward <- function(...,
                          plot_args = list(),
                          model_args = list()) {
  # Dots go to common params
  common <- list2(...)

  # Separate args for each function
  plot_args <- c(common, plot_args)
  model_args <- c(common, model_args)

  model <- exec(fit_model, !!!model_args)
  exec(plot, model, !!!plot_args)
}
```

### Building Function Calls Dynamically

```r
build_call <- function(fn, ..., .args = list()) {
  # Combine dots and explicit args
  args <- c(list2(...), .args)

  # Build call
  call2(fn, !!!args)
}

# Use
build_call("mean", sym("x"), na.rm = TRUE, trim = 0.1)
#> mean(x, na.rm = TRUE, trim = 0.1)
```

### Collecting and Validating

```r
validated_rbind <- function(...) {
  rows <- list2(...)

  # Validation
  if (length(rows) == 0) {
    abort("At least one row required")
  }

  if (!all(vapply(rows, is.numeric, logical(1)))) {
    abort("All rows must be numeric")
  }

  # All rows same length?
  lengths <- lengths(rows)
  if (length(unique(lengths)) > 1) {
    abort("All rows must have same length")
  }

  do.call(rbind, rows)
}
```

### S3 Method with Dots

```r
my_generic <- function(x, ...) {
  UseMethod("my_generic")
}

my_generic.default <- function(x, ..., error = TRUE) {
  # Check no unused dots (except error)
  check_dots_empty()

  if (error) {
    abort("No method for class {class(x)}")
  }
}

my_generic.data.frame <- function(x, ..., cols = NULL) {
  # Dots forwarded to internal function
  process_df(x, cols = cols, ...)
}
```

### Capturing Call with Dynamic Dots

```r
log_call <- function(...) {
  # Capture dots as expressions
  dots_exprs <- enquos(...)

  # Get names
  names <- names(dots_exprs)
  if (is.null(names)) {
    names <- rep("", length(dots_exprs))
  }

  # Log each
  for (i in seq_along(dots_exprs)) {
    message(
      if (names[i] != "") names[i] else i,
      ": ",
      as_label(dots_exprs[[i]])
    )
  }

  # Return values
  list2(...)
}

log_call(x = 1 + 1, 2 * 2, y = 3 + 3)
#> x: 1 + 1
#> 2: 2 * 2
#> y: 3 + 3
```

## Testing Argument Handling

```r
test_that("arg_match validates input", {
  f <- function(x = c("a", "b")) arg_match(x)

  expect_equal(f("a"), "a")
  expect_error(f("c"), "must be one of")
})

test_that("check_dots_empty catches extras", {
  f <- function(x, ...) {
    check_dots_empty()
    x
  }

  expect_equal(f(1), 1)
  expect_error(f(1, 2), "... must be empty")
})

test_that("dynamic dots work", {
  f <- function(...) list2(...)

  args <- list(a = 1, b = 2)
  result <- f(!!!args, c = 3)

  expect_equal(result, list(a = 1, b = 2, c = 3))
})
```

## Best Practices

1. **Use `arg_match()` for enums** - Better than manual `%in%` checks
2. **Check dots early** - `check_dots_empty()` at function start
3. **Provide `call` parameter** - All validation functions should accept `call = caller_env()`
4. **Use `caller_arg()`** - Don't hard-code argument names in errors
5. **Document dot behavior** - Make clear if `...` uses injection
6. **Validate dot types** - Don't assume dots are well-formed
7. **Test edge cases** - Empty dots, all unnamed, all named, mixed

## Base R Comparison

| rlang                | Base R                     |
| -------------------- | -------------------------- |
| `list2(...)`         | `list(...)` (no injection) |
| `arg_match()`        | `match.arg()`              |
| `check_required()`   | `missing()` + `stop()`     |
| `check_dots_empty()` | Manual check               |
| `:=`                 | No equivalent              |
| `!!!` splicing       | `do.call()`                |

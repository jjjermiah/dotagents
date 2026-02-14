# Conditions and Error Handling Reference

rlang's framework for structured, user-friendly error handling in R packages.

## Why Use rlang for Errors?

Base R's `stop()`, `warning()`, and `message()` work, but rlang provides:

1. **Structured errors** - Machine-readable metadata, classes, and fields
2. **Better formatting** - Bullet lists, CLI integration, color
3. **Error chaining** - Link related errors causally
4. **Backtraces** - Automatic call stack capture and display
5. **Caller context** - Show *user's* function, not internal helper

## Signaling Conditions

### `abort()` - Error

Throw an error with structured formatting:

```r
# Basic error
abort("Something went wrong")

# With bullet list
abort(c(
  "Can't process input",
  "x" = "Value must be positive",
  "i" = "You supplied -5"
))
#> Error:
#> ! Can't process input
#> ✖ Value must be positive
#> ℹ You supplied -5

# With error class for programmatic catching
abort("Invalid type", class = "my_package_type_error")
```

### `warn()` - Warning

```r
# Basic warning
warn("This is deprecated")

# With structure
warn(c(
  "Function will be removed",
  "i" = "Use `new_function()` instead"
))
```

### `inform()` - Message

```r
# Informational message
inform("Processing 1000 rows")

# With structure
inform(c(
  "Download complete",
  "v" = "Saved to cache/"
))
```

## Message Formatting

### Bullet Styles

```r
abort(c(
  "Header message",
  "x" = "Error/problem (red X)",
  "!" = "Warning (yellow !)",
  "i" = "Info (blue i)",
  "v" = "Success (green checkmark)",
  "*" = "Bullet point",
  " " = "Indented continuation"
))
```

### Dynamic Content

Use glue syntax for interpolation:

```r
value <- -5
min_val <- 0

abort(c(
  "Invalid value for `x`",
  "x" = "`x` must be >= {min_val}",
  "i" = "You provided {value}"
))
```

### CLI Integration

Use cli for richer formatting:

```r
# Enable cli locally in a function
local_use_cli()

abort(c(
  "Can't process {.arg data}",
  "x" = "Expected {.cls data.frame}, got {.cls {class(data)}}",
  "i" = "Did you mean to use {.fn read_csv}?"
))
```

**Styles available:**

- `{.arg x}` - Argument names
- `{.fn foo}` - Function names
- `{.cls data.frame}` - Class names
- `{.code x + 1}` - Inline code
- `{.field name}` - Field names
- `{.val "value"}` - Values

## Error Call Context

### The Problem

Without call context, errors show internal functions:

```r
check_positive <- function(x) {
  if (x < 0) abort("Must be positive")
}

my_function <- function(x) {
  check_positive(x)
}

my_function(-5)
#> Error in `check_positive()`:  # <- Wrong! User doesn't call this
#> ! Must be positive
```

### The Solution: `caller_env()`

Pass caller environment as `call`:

```r
check_positive <- function(x, call = caller_env()) {
  if (x < 0) abort("Must be positive", call = call)
}

my_function(-5)
#> Error in `my_function()`:  # <- Correct!
#> ! Must be positive
```

### Pattern for Error Helpers

All error/checking functions should accept `call`:

```r
check_string <- function(x, arg = "x", call = caller_env()) {
  if (!is_string(x)) {
    cli::cli_abort("{.arg {arg}} must be a string", call = call)
  }
}

check_type <- function(x, type, arg = "x", call = caller_env()) {
  if (!inherits(x, type)) {
    cli::cli_abort(
      "{.arg {arg}} must be a {.cls {type}}",
      call = call
    )
  }
}
```

### `local_error_call()`

Set error call once for entire function:

```r
my_function <- function(x, y) {
  local_error_call(current_env())

  # Now all abort() calls automatically use my_function's context
  if (x < 0) abort("x must be positive")
  if (y < 0) abort("y must be positive")
  # Both show "Error in `my_function()`"
}
```

### `caller_arg()`

Get the user's argument name automatically:

```r
check_positive <- function(x, arg = caller_arg(x), call = caller_env()) {
  if (x < 0) {
    cli::cli_abort("{.arg {arg}} must be positive", call = call)
  }
}

my_function <- function(my_value) {
  check_positive(my_value)  # No need to pass arg = "my_value"
}

my_function(-5)
#> Error in `my_function()`:
#> ! `my_value` must be positive
```

## Error Classes and Metadata

### Creating Typed Errors

```r
abort(
  "File not found",
  class = "fs_error_not_found",
  path = file_path
)

abort(
  "Invalid type",
  class = c("my_pkg_type_error", "my_pkg_error"),
  expected = "numeric",
  actual = "character"
)
```

### Why Use Classes?

1. **Programmatic catching** - Users can catch specific error types
2. **Testing** - Verify correct error thrown
3. **Error handlers** - Different responses for different errors

### Catching Typed Errors

```r
tryCatch(
  my_function(x),
  my_pkg_type_error = function(e) {
    # Handle type errors specially
    message("Type error: ", e$expected, " vs ", e$actual)
  },
  my_pkg_error = function(e) {
    # Handle other package errors
  }
)
```

## Error Chaining

Link related errors causally:

```r
fetch_data <- function(url) {
  tryCatch(
    download.file(url, "data.csv"),
    error = function(e) {
      abort(
        "Failed to fetch data",
        parent = e  # Chain the original error
      )
    }
  )
}

# Display shows both errors
fetch_data("bad://url")
#> Error in `fetch_data()`:
#> ! Failed to fetch data
#> Caused by error:
#> ! cannot open URL 'bad://url'
```

### Multi-level Chaining

```r
process_pipeline <- function(data) {
  tryCatch(
    fetch_data(data$url),
    error = function(e) {
      abort(
        "Pipeline failed at fetch stage",
        parent = e,
        stage = "fetch"
      )
    }
  )
}

# Shows full chain
process_pipeline(config)
#> Error in `process_pipeline()`:
#> ! Pipeline failed at fetch stage
#> Caused by error in `fetch_data()`:
#> ! Failed to fetch data
#> Caused by error:
#> ! cannot open URL
```

## Condition Handlers with `try_fetch()`

Modern alternative to `tryCatch()`:

```r
result <- try_fetch(
  my_operation(),

  # Handle specific error class
  my_pkg_type_error = function(cnd) {
    warn("Type error, using default")
    default_value
  },

  # Handle another class
  my_pkg_io_error = function(cnd) {
    abort("Fatal IO error", parent = cnd)
  }
)
```

**Advantages over `tryCatch()`:**

- Clearer syntax
- Automatic error chaining with `parent`
- Better backtrace handling

### Catch Any Error

```r
result <- try_fetch(
  risky_operation(),
  error = function(cnd) {
    # Fallback for any error
    default_value
  }
)
```

## Backtraces

### Automatic Backtrace Capture

```r
# Enable globally in .Rprofile or at session start
options(
  rlang_backtrace_on_error = "branch"  # Or "full", "reminder"
)

# Or programmatically
global_entrace()

# Now errors show backtrace automatically
my_function()
#> Error in `my_function()`:
#> ! Something went wrong
#> Backtrace:
#>  1. my_function()
#>  2. helper_function()
#>  3. rlang::abort("Something went wrong")
```

### Viewing Last Error

```r
# See full backtrace of last error
last_error()
last_trace()

# See recent warnings
last_warnings()

# See recent messages
last_messages()
```

### Simplified vs Full Backtraces

**Branch** (default) - Shows user code path, hides internal implementation:

```r
options(rlang_backtrace_on_error = "branch")
```

**Full** - Shows everything including internal functions:

```r
options(rlang_backtrace_on_error = "full")
```

## Testing Conditions

### Snapshot Tests (testthat)

```r
test_that("function errors correctly", {
  expect_snapshot(error = TRUE, {
    my_function(-5)
  })
})

# Captures:
# Error in `my_function()`:
# ! `x` must be positive
# ✖ You provided -5
```

### Testing Error Class

```r
test_that("throws correct error type", {
  expect_error(
    my_function(invalid_input),
    class = "my_pkg_type_error"
  )
})
```

### Testing Error Message

```r
test_that("error message is informative", {
  expect_error(
    check_positive(-5),
    "must be positive"
  )
})
```

### Testing Metadata

```r
test_that("error includes metadata", {
  err <- tryCatch(
    my_function(x),
    my_pkg_error = identity
  )

  expect_equal(err$expected, "numeric")
  expect_equal(err$actual, "character")
})
```

## Common Patterns

### Input Validation Suite

```r
validate_args <- function(x, y, z, call = caller_env()) {
  # Collect all errors first
  errors <- character()

  if (!is.numeric(x)) {
    errors <- c(errors, "x" = "`x` must be numeric")
  }
  if (y <= 0) {
    errors <- c(errors, "x" = "`y` must be positive")
  }
  if (!z %in% c("a", "b", "c")) {
    errors <- c(errors, "x" = "`z` must be 'a', 'b', or 'c'")
  }

  # Report all at once
  if (length(errors) > 0) {
    cli::cli_abort(
      c("Invalid arguments", errors),
      call = call
    )
  }
}
```

### Contextual Error Messages

```r
process_files <- function(files) {
  purrr::map(files, function(f) {
    tryCatch(
      read_file(f),
      error = function(e) {
        abort(
          c(
            "Failed to process file",
            "i" = "File: {f}",
            "i" = "Original error: {conditionMessage(e)}"
          ),
          parent = e
        )
      }
    )
  })
}
```

### Recoverable Errors with Warnings

```r
safe_compute <- function(x) {
  tryCatch(
    risky_operation(x),
    error = function(e) {
      warn(c(
        "Computation failed, using fallback",
        "i" = "Original error: {conditionMessage(e)}"
      ))
      fallback_value
    }
  )
}
```

### Conditional Error Detail

```r
my_function <- function(x, verbose = FALSE) {
  if (invalid(x)) {
    msg <- c("Invalid input")

    if (verbose) {
      msg <- c(
        msg,
        "i" = "Expected range: [0, 100]",
        "i" = "Received: {x}",
        "i" = "Type: {typeof(x)}"
      )
    }

    abort(msg)
  }
}
```

## Condition Object Structure

```r
# Create condition manually
cnd <- error_cnd(
  class = "my_pkg_error",
  message = "Something failed",
  field1 = "value1",
  field2 = "value2"
)

# Access fields
conditionMessage(cnd)
cnd$field1

# Signal it
cnd_signal(cnd)
```

## Best Practices

1. **Always pass `call = caller_env()`** in error helpers
2. **Use error classes** for all package errors (at least one package-level class)
3. **Use bullet lists** for multi-part messages
4. **Chain errors** with `parent` when catching and re-throwing
5. **Test error messages** with snapshot tests
6. **Include actionable info** - tell users what to do, not just what went wrong
7. **Use cli integration** for formatting in user-facing packages
8. **Capture context** - include relevant values in error metadata

## Base R Comparison

| rlang          | Base R                    |
| -------------- | ------------------------- |
| `abort()`      | `stop()`                  |
| `warn()`       | `warning()`               |
| `inform()`     | `message()`               |
| `try_fetch()`  | `tryCatch()`              |
| Error chaining | Not available             |
| Bullet lists   | Manual paste              |
| Backtraces     | Limited via `traceback()` |

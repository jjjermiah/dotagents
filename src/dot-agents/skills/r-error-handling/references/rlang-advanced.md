# rlang Advanced Error Handling

## Error Chaining Deep Dive

Error chaining creates a linked list of conditions, preserving context at each level.

### Chain Structure

```r
# Low-level error
low <- error_cnd(
  message = "Connection timeout",
  class = "http_timeout"
)

# Chain it to high-level error
high <- error_cnd(
  message = "Failed to download file",
  class = "download_error",
  parent = low
)

# Inspect chain
cnd_inherits(high, "http_timeout")  # TRUE - inherits across chain
```

### Multi-Level Chaining

```r
download_and_process <- function(url) {
  # Level 1: HTTP layer
  try_fetch(
    raw <- http_get(url),
    http_error = function(cnd) {
      abort("HTTP request failed", class = "http_layer_error", parent = cnd)
    }
  )

  # Level 2: Parsing layer
  try_fetch(
    data <- parse_json(raw),
    error = function(cnd) {
      abort("JSON parsing failed", class = "parse_layer_error", parent = cnd)
    }
  )

  # Level 3: Validation layer
  try_fetch(
    validate_schema(data),
    error = function(cnd) {
      abort("Schema validation failed", class = "validation_layer_error", parent = cnd)
    }
  )

  data
}

# Error message shows all layers:
# Error: Schema validation failed
# Caused by: JSON parsing failed
# Caused by: Unexpected character at position 10
```

### Selective Inheritance with .inherit

Control whether errors inherit across chains:

```r
# Downgrade error to warning (don't inherit as error)
try_fetch(
  operation(),
  recoverable_error = function(cnd) {
    warn(
      "Recovered from error",
      class = "recovery_warning",
      parent = cnd,
      .inherit = FALSE  # Don't inherit as error
    )
    fallback_value
  }
)
```

## Advanced try_fetch Patterns

### Multiple Error Classes

```r
try_fetch(
  operation(),

  # Handle specific network errors
  http_timeout = function(cnd) {
    log_info("Timeout, retrying...")
    Sys.sleep(1)
    zap()  # Retry
  },

  http_404 = function(cnd) {
    warn("Resource not found, using default")
    default_value
  },

  # Handle any other HTTP error
  http_error = function(cnd) {
    abort("Network error occurred", parent = cnd)
  },

  # Catch-all for unexpected errors
  error = function(cnd) {
    log_error(cnd)
    abort("Unexpected error", parent = cnd)
  }
)
```

### Dynamic Handler Generation

```r
# Generate handlers for multiple error types
make_handlers <- function(error_classes, log_func) {
  handlers <- lapply(error_classes, function(class) {
    function(cnd) {
      log_func(class, cnd)
      zap()
    }
  })
  names(handlers) <- error_classes
  handlers
}

# Use with do.call or rlang::inject
handlers <- make_handlers(
  c("network_error", "parse_error", "validation_error"),
  log_error
)

inject(try_fetch(operation(), !!!handlers))
```

### Conditional Recovery

```r
safe_divide <- function(x, y, call = caller_env()) {
  try_fetch(
    {
      if (y == 0) {
        abort("Division by zero", class = "division_error", call = call)
      }
      x / y
    },
    division_error = function(cnd) {
      # Recover based on context
      if (getOption("strict_math", FALSE)) {
        abort("Cannot divide by zero", parent = cnd, call = call)
      } else {
        warn("Returning Inf for division by zero", parent = cnd)
        Inf
      }
    }
  )
}
```

## Custom Condition Constructors

### Error Constructor

```r
#' @param message Error message
#' @param ..., Additional fields
#' @param class Error subclass
#' @param call Calling environment
error_mypackage <- function(message,
                            ...,
                            class = NULL,
                            call = caller_env()) {
  abort(
    message,
    class = c(class, "mypackage_error"),
    ...,
    call = call
  )
}

# Specialized constructors
error_validation <- function(message, field, expected, actual, call = caller_env()) {
  error_mypackage(
    message,
    class = "validation_error",
    field = field,
    expected = expected,
    actual = actual,
    call = call
  )
}

# Usage
validate_type <- function(x, type, arg = caller_arg(x), call = caller_env()) {
  if (!inherits(x, type)) {
    error_validation(
      sprintf("`%s` must be of type %s", arg, type),
      field = arg,
      expected = type,
      actual = class(x),
      call = call
    )
  }
}
```

## Bullet Formatting with cli

### Advanced Bullet Types

```r
abort(c(
  "Multiple errors occurred:",
  x = "Required column 'id' is missing",
  x = "Required column 'name' is missing",
  i = "Available columns: age, city",
  i = "See ?required_columns for details"
))
```

### Dynamic Bullet Generation

```r
report_missing_columns <- function(data, required, call = caller_env()) {
  missing <- setdiff(required, names(data))

  if (length(missing) > 0) {
    bullets <- c(
      sprintf("%d required column%s missing:",
              length(missing),
              if (length(missing) > 1) "s are" else " is"),
      set_names(sprintf("Column '%s'", missing), rep("x", length(missing))),
      i = sprintf("Available: %s", paste(names(data), collapse = ", "))
    )

    abort(bullets, class = "missing_columns_error", call = call)
  }
}
```

### Pluralization

```r
report_errors <- function(errors) {
  n <- length(errors)
  abort(c(
    "{n} error{?s} occurred:",  # Auto-pluralizes based on n
    i = "Check the logs for details"
  ))
}
```

### Inline Styling

```r
abort(c(
  "Cannot load {.file data.csv}",
  i = "Expected path: {.path /data/input/}",
  i = "Run {.code setup_data()} first",
  i = "See {.url https://example.com/docs}"
))
```

## Call Argument Handling

### caller_arg() for Readable Messages

```r
check_positive <- function(x, arg = caller_arg(x), call = caller_env()) {
  if (any(x <= 0)) {
    abort(
      sprintf("`%s` must contain only positive values", arg),
      class = "validation_error",
      call = call
    )
  }
}

# Automatically captures correct argument name
my_function <- function(sample_size) {
  check_positive(sample_size)  # Error shows "sample_size"
}

my_function(data$some_column)  # Error shows "data$some_column"
```

### Forwarding Call Context

```r
# Helper function
validate_and_process <- function(x, arg = caller_arg(x), call = caller_env()) {
  check_type(x, "numeric", arg = arg, call = call)
  check_positive(x, arg = arg, call = call)
  process(x)
}

# User-facing function
analyze_data <- function(measurements) {
  validate_and_process(measurements)  # Errors show "analyze_data()"
}
```

### Hard-Coding Calls

```r
# When call can't be inferred
async_callback <- function(result) {
  if (is_error(result)) {
    abort(
      "Async operation failed",
      call = call("fetch_remote_data", url = result$url)  # Synthetic call
    )
  }
}
```

## Lazy Message Generation

For expensive message formatting, use lazy evaluation:

```r
error_large_data <- function(data, call = caller_env()) {
  abort(
    message = function(cnd) {
      # Only computed if error is displayed
      summary <- expensive_summary(data)
      sprintf("Invalid data structure: %s", summary)
    },
    class = "data_error",
    data_snapshot = data[1:5],  # Store small sample
    call = call
  )
}
```

## Backtrace Control

### .trace_bottom Argument

```r
# Hide error handling infrastructure from backtrace
with_error_context <- function(expr, context, call = caller_env()) {
  try_fetch(
    expr,
    error = function(cnd) {
      abort(
        sprintf("Error in context: %s", context),
        parent = cnd,
        call = call,
        .trace_bottom = call  # Hide frames below this
      )
    }
  )
}
```

## Condition Fields and Metadata

### Structured Error Data

```r
error_api <- function(message, status, response, call = caller_env()) {
  abort(
    message,
    class = "api_error",
    status_code = status,
    response_body = response,
    timestamp = Sys.time(),
    call = call
  )
}

# Handlers can inspect metadata
try_fetch(
  api_call(),
  api_error = function(cnd) {
    if (cnd$status_code == 429) {
      Sys.sleep(60)
      zap()  # Retry after rate limit
    } else {
      abort("API error", parent = cnd)
    }
  }
)
```

### Attaching Context to Warnings

```r
warn_deprecated <- function(old, new, when, call = caller_env()) {
  warn(
    c(
      sprintf("`%s()` is deprecated as of version %s", old, when),
      i = sprintf("Please use `%s()` instead", new)
    ),
    class = "lifecycle_deprecated",
    old = old,
    new = new,
    when = when,
    .frequency = "once",
    .frequency_id = paste0("deprecated_", old)
  )
}
```

## Global Error Options

### local_use_cli for Package

```r
# In .onLoad()
.onLoad <- function(libname, pkgname) {
  # Enable cli formatting for all package errors
  rlang::local_use_cli(format = TRUE)
}
```

### Custom Backtrace Display

```r
# Control backtrace verbosity
options(
  rlang_backtrace_on_error = "branch",  # "none", "reminder", "branch", "full"
  rlang_trace_format_srcrefs = TRUE     # Include source references
)
```

## Testing Integration

### Expect Specific Error

```r
test_that("validates input type", {
  expect_error(
    my_function("wrong"),
    class = "mypackage_validation_error"
  )

  # With field inspection
  err <- tryCatch(
    my_function("wrong"),
    mypackage_validation_error = identity
  )

  expect_equal(err$field, "x")
  expect_equal(err$expected, "numeric")
})
```

### Snapshot Testing

```r
test_that("error messages are clear", {
  expect_snapshot(error = TRUE, {
    my_function(bad_input)
  })

  # First run creates snapshot
  # Subsequent runs compare
})
```

## Performance Tips

1. **Avoid try_fetch in hot loops** - Extract to higher level
2. **Use .frequency for repeated warnings** - Reduces overhead
3. **Lazy message generation** - For expensive formatting
4. **Condition caching** - Reuse condition objects

```r
# Cache condition object
.globals <- new.env(parent = emptyenv())
.globals$cached_error <- NULL

get_cached_error <- function(message, class) {
  key <- paste0(class, ":", message)

  if (is.null(.globals$cached_error[[key]])) {
    .globals$cached_error[[key]] <- error_cnd(message, class = class)
  }

  .globals$cached_error[[key]]
}
```

## Real-World Example: Robust Data Pipeline

```r
process_pipeline <- function(files, output_dir, call = caller_env()) {
  results <- list()

  for (i in seq_along(files)) {
    file <- files[[i]]

    results[[i]] <- try_fetch(
      {
        # Layer 1: File I/O
        try_fetch(
          raw <- read_file(file),
          error = function(cnd) {
            abort(
              sprintf("Cannot read file: %s", basename(file)),
              class = "io_error",
              path = file,
              parent = cnd,
              call = call
            )
          }
        )

        # Layer 2: Parsing
        try_fetch(
          data <- parse_data(raw),
          error = function(cnd) {
            abort(
              "Data parsing failed",
              class = "parse_error",
              parent = cnd,
              call = call
            )
          }
        )

        # Layer 3: Validation
        try_fetch(
          validate_schema(data),
          error = function(cnd) {
            abort(
              "Schema validation failed",
              class = "validation_error",
              parent = cnd,
              call = call
            )
          }
        )

        # Layer 4: Processing
        process_data(data)
      },
      error = function(cnd) {
        # Log full chain
        log_error(sprintf("File %d/%d failed: %s", i, length(files), file))
        log_error_chain(cnd)

        # Decide whether to continue
        if (getOption("pipeline_stop_on_error", FALSE)) {
          abort(
            sprintf("Pipeline stopped at file %d", i),
            parent = cnd,
            call = call
          )
        } else {
          warn(sprintf("Skipping file %d due to error", i), parent = cnd)
          NULL  # Return NULL for failed file
        }
      }
    )
  }

  results
}
```

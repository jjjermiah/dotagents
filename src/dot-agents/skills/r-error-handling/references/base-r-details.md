# Base R Error Handling - Deep Dive

## The Condition System

R has a sophisticated condition system with three main types:

### Condition Hierarchy

```text
condition (base class)
├── error
├── warning
└── message
```

Custom conditions extend these base classes.

## Creating Custom Conditions

### Manual Construction

```r
# Error condition constructor
new_error <- function(message, class = NULL, ..., call = NULL) {
  structure(
    list(
      message = message,
      call = call,
      ...
    ),
    class = c(class, "error", "condition")
  )
}

# Usage
err <- new_error(
  message = "File not found",
  class = c("io_error", "file_not_found"),
  path = "/missing/file.txt",
  call = sys.call()
)

stop(err)
```

### Warning and Message Conditions

```r
new_warning <- function(message, class = NULL, ..., call = NULL) {
  structure(
    list(message = message, call = call, ...),
    class = c(class, "warning", "condition")
  )
}

new_message <- function(message, class = NULL, ...) {
  structure(
    list(message = message, ...),
    class = c(class, "message", "condition")
  )
}

# Signal them
warning(new_warning("Deprecated function", class = "deprecation"))
message(new_message("Starting process", class = "info"))
```

## Error Handling Functions

### tryCatch

**Exiting handler** - unwinds the stack to the tryCatch call.

```r
result <- tryCatch(
  expr = {
    # Code that might error
    risky_function()
  },
  error = function(e) {
    # Handler receives condition object
    cat("Error:", e$message, "\n")
    return(NA)  # Recovery value
  },
  warning = function(w) {
    cat("Warning:", w$message, "\n")
    NULL
  },
  finally = {
    # Always runs (cleanup code)
    cleanup()
  }
)
```

**Key properties:**

- Stack unwound before handler runs
- Cannot use `recover()` or inspect full stack
- Good for error recovery
- `finally` always executes

### withCallingHandlers

**Calling handler** - runs in the context where condition was signaled.

```r
withCallingHandlers(
  expr = {
    risky_function()
  },
  error = function(e) {
    # Stack is intact here
    cat("Stack depth:", length(sys.calls()), "\n")
    print(sys.calls())  # Full call stack available

    # Condition continues to propagate unless explicitly stopped
  },
  warning = function(w) {
    log_warning(w)
    # Warning continues unless invokeRestart() or muffled
  }
)
```

**Key properties:**

- Stack intact during handler
- Condition propagates after handler (unless stopped)
- Good for logging, debugging
- Can use `recover()` to debug

### Combining Both

```r
# Log with calling handler, recover with exiting handler
tryCatch(
  withCallingHandlers(
    risky_operation(),
    error = function(e) {
      # Log with full stack
      logger::log_error("Error at depth {length(sys.calls())}: {e$message}")
    }
  ),
  error = function(e) {
    # Recover
    return(default_value)
  }
)
```

## Advanced: Restarts

Restarts allow error handlers to recover in sophisticated ways.

### Defining Restarts

```r
read_file_with_restart <- function(path) {
  withRestarts(
    {
      if (!file.exists(path)) {
        stop(new_error("File not found", class = "file_error", path = path))
      }
      readLines(path)
    },
    # Define available restarts
    use_default = function() character(0),
    use_alternative = function(alt_path) readLines(alt_path),
    skip = function() NULL
  )
}
```

### Invoking Restarts

```r
# Handler can invoke restart
withCallingHandlers(
  result <- read_file_with_restart("missing.txt"),
  file_error = function(e) {
    # Choose restart based on condition
    if (interactive()) {
      alt <- readline("Alternative path: ")
      invokeRestart("use_alternative", alt)
    } else {
      invokeRestart("use_default")
    }
  }
)
```

**Available restarts:**

- `abort` - Terminate (default for errors)
- `muffleWarning` - Suppress warning
- `muffleMessage` - Suppress message
- Custom restarts via `withRestarts()`

### Listing Available Restarts

```r
withRestarts(
  {
    print(computeRestarts())  # Shows available restarts
    stop("error")
  },
  custom_restart = function() "recovered"
)
```

## try() Function

Simplified error catching - returns try-error object instead of stopping.

```r
result <- try(risky_function(), silent = TRUE)

if (inherits(result, "try-error")) {
  # Handle error
  message("Failed: ", attr(result, "condition")$message)
  result <- default_value
}
```

**When to use:**

- Simple cases where you just want to suppress errors
- Legacy code
- Quick scripts

**Prefer `tryCatch()` or `try_fetch()` for:**

- Production code
- Selective error handling
- Custom error classes

## Muffling Conditions

### Suppress Functions

```r
# Suppress messages
suppressMessages({
  message("This won't show")
})

# Suppress warnings
suppressWarnings({
  warning("This won't show")
})

# Suppress both (careful!)
suppressMessages(suppressWarnings({
  # Code
}))
```

### Manual Muffling

```r
withCallingHandlers(
  {
    warning("This will be muffled")
    message("This will be muffled")
  },
  warning = function(w) invokeRestart("muffleWarning"),
  message = function(m) invokeRestart("muffleMessage")
)
```

## Best Practices

### 1. Set call. = FALSE for User Errors

```r
# BAD - shows confusing internal call
stop("Invalid input")
#> Error in my_function(x) : Invalid input

# GOOD - cleaner message
stop("Invalid input", call. = FALSE)
#> Error: Invalid input
```

### 2. Check Condition Classes with inherits()

```r
tryCatch(
  operation(),
  error = function(e) {
    if (inherits(e, "network_error")) {
      retry()
    } else if (inherits(e, "validation_error")) {
      return(NA)
    } else {
      stop(e)  # Rethrow
    }
  }
)
```

### 3. Use sys.call() for Context

```r
validate_input <- function(x) {
  if (!valid(x)) {
    stop(
      new_error(
        "Invalid input",
        class = "validation_error",
        call = sys.call(-1)  # Parent call
      )
    )
  }
}
```

### 4. Preserve Original Errors When Rethrowing

```r
tryCatch(
  low_level_function(),
  error = function(e) {
    # Create new error with original as attribute
    new_err <- new_error(
      "High-level operation failed",
      class = "high_level_error",
      original_error = e
    )
    stop(new_err)
  }
)
```

## Common Patterns

### Safe Version of Function

```r
safe_function <- function(...) {
  tryCatch(
    risky_function(...),
    error = function(e) {
      attr(NA, "error") <- e
      NA
    }
  )
}

# Usage
result <- safe_function(x)
if (is.na(result) && !is.null(attr(result, "error"))) {
  # Handle error
}
```

### Retry with Exponential Backoff

```r
retry <- function(expr, max_attempts = 3, backoff = 1) {
  for (i in seq_len(max_attempts)) {
    result <- try(expr, silent = TRUE)

    if (!inherits(result, "try-error")) {
      return(result)
    }

    if (i < max_attempts) {
      Sys.sleep(backoff * 2^(i - 1))
    }
  }

  stop("Failed after ", max_attempts, " attempts")
}
```

### Collect All Errors

```r
# Process multiple items, collect all errors
process_all <- function(items) {
  results <- list()
  errors <- list()

  for (i in seq_along(items)) {
    result <- try(process_item(items[[i]]), silent = TRUE)

    if (inherits(result, "try-error")) {
      errors[[i]] <- attr(result, "condition")
    } else {
      results[[i]] <- result
    }
  }

  if (length(errors) > 0) {
    warning(sprintf("%d items failed to process", length(errors)))
  }

  list(results = results, errors = errors)
}
```

## Performance Considerations

- `tryCatch()` has minimal overhead when no error occurs
- `withCallingHandlers()` slightly higher overhead
- Avoid error handling in tight loops if possible
- Consider vectorized operations over error handling in loops

## Debugging Integration

### Use with browser()

```r
withCallingHandlers(
  operation(),
  error = function(e) {
    if (interactive()) {
      cat("Error occurred:", e$message, "\n")
      browser()  # Drop into debugger
    }
  }
)
```

### Use with recover()

```r
# Set global option for debugging
options(error = recover)

# Or per-call
tryCatch(
  operation(),
  error = function(e) {
    recover()
  }
)
```

## Stack Trace Inspection

```r
get_stack_trace <- function() {
  calls <- sys.calls()
  frames <- sys.frames()

  lapply(seq_along(calls), function(i) {
    list(
      call = calls[[i]],
      env = frames[[i]]
    )
  })
}

withCallingHandlers(
  operation(),
  error = function(e) {
    trace <- get_stack_trace()
    saveRDS(list(error = e, trace = trace), "error_trace.rds")
  }
)
```

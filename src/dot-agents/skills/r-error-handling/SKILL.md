---
name: r-error-handling
description: Base R error handling with tryCatch, withCallingHandlers, and custom condition classes. Use when implementing error recovery, debugging conditions, or working with stop/warning/message—e.g., "tryCatch in R", "custom condition class", "handle warnings and errors", "error recovery patterns".
---

# R Error Handling

## Purpose

Production-grade error handling and custom condition classes in R. Guide structured errors, input validation, error chaining, and graceful recovery.

## Core Philosophy

**We follow one principle: Fail fast, fail informatively.**

Every error handling implementation MUST:

1. Guide users to solutions with clear messages
2. Preserve debugging context with backtraces
3. Support selective handling via custom classes
4. Chain context linking low-level to high-level errors

## Quick Reference

### Modern rlang Approach (Preferred)

```r
# Basic error with call context
check_positive <- function(x, arg = rlang::caller_arg(x), call = rlang::caller_env()) {
  if (any(x <= 0)) {
    rlang::abort(
      sprintf("`%s` must be positive.", arg),
      class = "mypackage_validation_error",
      call = call
    )
  }
}

# Error chaining
download_data <- function(url, call = rlang::caller_env()) {
  rlang::try_fetch(
    fetch_and_parse(url),
    error = function(cnd) {
      rlang::abort(
        sprintf("Failed to download from %s", url),
        class = "mypackage_download_error",
        parent = cnd,  # Chains original error
        call = call
      )
    }
  )
}

# Structured messages
rlang::abort(c(
  "Required columns missing.",
  x = "Column 'id' not found",
  i = "Available: name, age, city"
))
```

### Base R Approach

```r
# Simple error
validate_input <- function(x) {
  if (!valid(x)) {
    stop("Invalid input", call. = FALSE)
  }
}

# Error recovery
result <- tryCatch(
  risky_operation(),
  error = function(e) {
    message("Error: ", e$message)
    default_value
  }
)
```

## Essential Patterns

### Error Class Naming

Format: `{package}_{domain}_{type}`

```r
"mypackage_validation_invalid_type"
"mypackage_io_file_not_found"
```

### Input Validation

```r
check_string <- function(x, arg = rlang::caller_arg(x), call = rlang::caller_env()) {
  if (!is.character(x) || length(x) != 1) {
    rlang::abort(
      sprintf("`%s` must be a single string.", arg),
      class = "mypackage_validation_error",
      call = call
    )
  }
}

# Auto-detects argument name
my_function <- function(file_path) {
  check_string(file_path)  # Error shows "file_path"
}
```

### Error Recovery

```r
result <- rlang::try_fetch(
  operation(),
  mypackage_network_error = function(cnd) { get_cached_data() },
  error = function(cnd) { log_error(cnd); rlang::zap() }
)
```

### Package Error Helper

```r
# In R/errors.R
abort_mypackage <- function(message, class, ..., call = rlang::caller_env()) {
  rlang::abort(
    message,
    class = paste0("mypackage_", class),
    ...,
    call = call
  )
}

# Usage
check_input <- function(x, call = rlang::caller_env()) {
  if (!valid(x)) {
    abort_mypackage("Invalid input", class = "validation_error", call = call)
  }
}
```

## Bullet Formatting

```r
# Bullet types:
# i = info (blue)
# x = error (red X)
# v = success (green check)
# ! = warning (yellow)
# * = regular

rlang::abort(c(
  "Multiple validation errors:",
  x = "Field 'id' is missing",
  x = "Field 'name' is invalid",
  i = "See ?required_fields for details"
))
```

## Decision Matrix

| Use Case          | Tool                                     | Notes                |
| ----------------- | ---------------------------------------- | -------------------- |
| New package       | `try_fetch()` + `abort()`                | Modern, powerful     |
| Zero dependencies | `tryCatch()` + `stop()`                  | Acceptable tradeoff  |
| Error chaining    | `parent` arg                             | Preserves context    |
| Input validation  | `caller_arg()` + `abort()`               | Readable messages    |
| Error recovery    | `try_fetch()`                            | Better than tryCatch |
| Stack inspection  | `try_fetch()` or `withCallingHandlers()` | Both preserve stack  |

## Anti-Patterns (NEVER Do These)

These patterns ALWAYS cause failures in production. No exceptions.

**NEVER:**

- Swallow errors silently: `tryCatch(x, error = function(e) NULL)` — debugging becomes impossible
- Use generic error classes: `abort("Error")` — breaks selective handling
- Forget `call` argument: `abort_mypackage("Error")` — shows wrong function in traceback, every time
- Discard low-level errors: Rethrow without `parent` — loses critical context

**ALWAYS:**

- Log before recovering: `log_error(cnd); return(fallback)`
- Use specific classes: `class = "mypackage_specific_error"`
- Pass call context: `call = caller_env()`
- Chain errors: `parent = cnd`

## Testing

```r
# Test error class
testthat::test_that("validates input", {
  testthat::expect_error(
    my_function(bad_input),
    class = "mypackage_validation_error"
  )
})

# Snapshot error messages
testthat::test_that("error messages are clear", {
  testthat::expect_snapshot(error = TRUE, {
    my_function(bad_input)
  })
})

# Inspect error metadata
testthat::test_that("error has correct fields", {
  err <- rlang::catch_cnd(my_function(bad_input))
  testthat::expect_equal(err$field, "x")
  testthat::expect_equal(err$expected, "numeric")
})
```

## Output Contract (You MUST Comply)

Before finishing any task with this skill, verify ALL of the following:

- [ ] All errors use `rlang::abort()` with custom classes (never `library(rlang)`)
- [ ] All helpers accept `call = rlang::caller_env()`
- [ ] Error messages use bulleted formatting
- [ ] Low-level errors chained to high-level with `parent = cnd`
- [ ] All rlang functions explicitly namespaced

**Checking these items is required. Skipped verification = broken error handling in production.**

## References (Load on Demand)

- **[references/base-r-details.md](references/base-r-details.md)** - Load when working with base R handlers (tryCatch, withCallingHandlers), restarts, or stack traces
- **[references/rlang-advanced.md](references/rlang-advanced.md)** - Load when implementing complex error chains, custom condition constructors, or lazy error messages
- **[references/testing-patterns.md](references/testing-patterns.md)** - Load when writing or reviewing tests for error conditions

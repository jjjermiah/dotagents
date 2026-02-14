# Testing Error Handling

Comprehensive patterns for testing error conditions with testthat.

## Basic Error Testing

### Expect Error Class

```r
test_that("validates input types", {
  # Basic error expectation
  expect_error(
    my_function("invalid"),
    class = "mypackage_validation_error"
  )

  # Multiple classes in hierarchy
  expect_error(
    my_function("invalid"),
    class = c("mypackage_validation_error", "rlang_error")
  )
})
```

### Expect Error Message Pattern

```r
test_that("error messages are descriptive", {
  expect_error(
    check_positive(-5),
    "must contain only positive values"
  )

  # Regex patterns
  expect_error(
    check_positive(-5),
    regexp = "positive.*values"
  )
})
```

### Expect No Error

```r
test_that("accepts valid inputs", {
  expect_no_error(my_function(valid_input))

  # Alternative
  expect_silent(my_function(valid_input))
})
```

## Snapshot Testing

### Error Message Snapshots

```r
test_that("error formatting is consistent", {
  expect_snapshot(error = TRUE, {
    my_function(bad_input)
  })
})

# Creates: tests/testthat/_snaps/my-test.md
# ---- output ----
# Error in `my_function()`:
# ! `x` must be numeric
# i Got character instead
```

### Multiple Snapshots

```r
test_that("various errors are well-formatted", {
  expect_snapshot(error = TRUE, {
    # Snapshot 1
    validate_type(123, "character")

    # Snapshot 2
    validate_range(200, 1, 100)

    # Snapshot 3
    validate_columns(data, c("x", "y", "z"))
  })
})
```

### Snapshot Variants

```r
test_that("error format adapts to context", {
  # Different snapshots for different conditions
  expect_snapshot(error = TRUE, variant = "interactive", {
    my_function(bad_input)
  })

  expect_snapshot(error = TRUE, variant = "non-interactive", {
    my_function(bad_input)
  })
})
```

## Capturing and Inspecting Errors

### Capture Error Object

```r
test_that("error contains correct metadata", {
  err <- tryCatch(
    my_function(bad_input),
    mypackage_validation_error = identity,
    error = function(e) fail("Wrong error class")
  )

  # Inspect fields
  expect_equal(err$field, "x")
  expect_equal(err$expected, "numeric")
  expect_equal(err$actual, "character")
  expect_s3_class(err, "mypackage_validation_error")
})
```

### Using rlang::catch_cnd

```r
test_that("error metadata is correct", {
  err <- catch_cnd(
    my_function(bad_input),
    classes = "mypackage_validation_error"
  )

  expect_s3_class(err, "mypackage_validation_error")
  expect_equal(err$field, "x")
  expect_match(err$message, "must be numeric")
})
```

## Testing Error Chaining

### Verify Parent Errors

```r
test_that("chains low-level errors correctly", {
  err <- catch_cnd(download_and_parse("bad_url"))

  # Check top-level error
  expect_s3_class(err, "mypackage_download_error")

  # Check chained parent
  expect_s3_class(err$parent, "http_error")
  expect_match(err$parent$message, "404")
})
```

### Full Chain Inspection

```r
test_that("error chain provides complete context", {
  err <- catch_cnd(process_file("bad.csv"))

  # Walk the chain
  errors <- list()
  current <- err
  while (!is.null(current)) {
    errors <- c(errors, list(current))
    current <- current$parent
  }

  expect_length(errors, 3)  # Expected chain depth
  expect_s3_class(errors[[1]], "processing_error")
  expect_s3_class(errors[[2]], "parse_error")
  expect_s3_class(errors[[3]], "io_error")
})
```

## Testing Warning Conditions

### Expect Warning

```r
test_that("warns about deprecated usage", {
  expect_warning(
    old_function(),
    class = "mypackage_deprecated"
  )

  # With message pattern
  expect_warning(
    old_function(),
    "deprecated.*version 2.0"
  )
})
```

### Suppress Expected Warnings

```r
test_that("computation succeeds despite warnings", {
  result <- suppressWarnings(
    my_function(edge_case),
    classes = "mypackage_known_warning"
  )

  expect_equal(result, expected_result)
})
```

### Capture Warning Metadata

```r
test_that("warning includes deprecation metadata", {
  wrn <- catch_cnd(old_function(), classes = "lifecycle_deprecated")

  expect_equal(wrn$old, "old_function")
  expect_equal(wrn$new, "new_function")
  expect_equal(wrn$when, "2.0.0")
})
```

## Testing Message Conditions

### Expect Informative Messages

```r
test_that("reports progress messages", {
  expect_message(
    process_data(x),
    "Processing 100 records"
  )

  expect_message(
    process_data(x),
    class = "mypackage_info_progress"
  )
})
```

### Snapshot Messages

```r
test_that("progress messages are clear", {
  expect_snapshot({
    process_large_dataset(data)
  })
})
```

## Testing Error Recovery

### Verify Fallback Values

```r
test_that("recovers from network errors", {
  # Mock network failure
  mockery::stub(
    fetch_remote,
    "http_get",
    function(...) abort("Network error", class = "http_error")
  )

  result <- fetch_with_fallback(url)

  expect_equal(result, default_data)
})
```

### Test Retry Logic

```r
test_that("retries on transient errors", {
  call_count <- 0

  mock_function <- function() {
    call_count <<- call_count + 1
    if (call_count < 3) {
      abort("Transient error", class = "retriable_error")
    }
    "success"
  }

  result <- retry_on_error(mock_function(), max_attempts = 3)

  expect_equal(result, "success")
  expect_equal(call_count, 3)
})
```

## Testing Input Validation

### Parametrized Tests

```r
test_that("rejects invalid types", {
  invalid_inputs <- list(
    NULL,
    NA,
    character(),
    list(),
    data.frame()
  )

  for (input in invalid_inputs) {
    expect_error(
      validate_input(input),
      class = "mypackage_validation_error"
    )
  }
})
```

### Test Each Validation Rule

```r
test_that("validates all constraints", {
  # Type validation
  expect_error(
    validate_age("not_numeric"),
    class = "validation_type_error"
  )

  # Range validation
  expect_error(
    validate_age(-5),
    class = "validation_range_error"
  )

  # Length validation
  expect_error(
    validate_age(numeric(0)),
    class = "validation_length_error"
  )

  # Missing validation
  expect_error(
    validate_age(NA),
    class = "validation_missing_error"
  )
})
```

## Testing Error Helpers

### Test Call Context

```r
test_that("error shows correct calling function", {
  my_wrapper <- function(x) {
    check_positive(x)
  }

  err <- catch_cnd(my_wrapper(-5))

  # Should show my_wrapper, not check_positive
  expect_match(conditionMessage(err), "my_wrapper")
})
```

### Test Argument Name Detection

```r
test_that("error includes correct argument name", {
  validate_input <- function(data) {
    check_columns(data, required = c("id", "name"))
  }

  err <- catch_cnd(validate_input(data.frame(x = 1)))

  expect_match(err$message, "`data`")  # Not generic "x"
})
```

## Mocking for Error Testing

### Mock External Dependencies

```r
test_that("handles file system errors", {
  mockery::stub(
    read_config,
    "file.exists",
    FALSE
  )

  expect_error(
    read_config("config.yml"),
    class = "mypackage_file_not_found"
  )
})
```

### Mock to Trigger Errors

```r
test_that("chains database errors appropriately", {
  mockery::stub(
    fetch_records,
    "DBI::dbGetQuery",
    function(...) abort("Query failed", class = "db_error")
  )

  err <- catch_cnd(fetch_records(conn, "SELECT * FROM users"))

  expect_s3_class(err, "mypackage_fetch_error")
  expect_s3_class(err$parent, "db_error")
})
```

## Integration Testing

### Test Error Handling Across Layers

```r
test_that("pipeline errors propagate correctly", {
  # Create invalid test data
  files <- c(
    "valid.csv",
    "missing.csv",
    "corrupt.csv"
  )

  # Mock file operations
  mockery::stub(
    process_pipeline,
    "read_file",
    function(path) {
      if (path == "missing.csv") {
        abort("File not found", class = "io_error")
      } else if (path == "corrupt.csv") {
        "invalid data"
      } else {
        "valid,data\n1,2"
      }
    }
  )

  # Should handle errors gracefully
  expect_warning(
    results <- process_pipeline(files),
    "Skipping file"
  )

  # Valid file should succeed
  expect_false(is.null(results[[1]]))

  # Invalid files should be NULL
  expect_null(results[[2]])
  expect_null(results[[3]])
})
```

## Performance Testing

### Test Error Handling Overhead

```r
test_that("error handling has minimal overhead", {
  # Baseline: no error handling
  baseline <- system.time({
    for (i in 1:10000) {
      result <- simple_function(i)
    }
  })

  # With error handling
  with_handling <- system.time({
    for (i in 1:10000) {
      result <- try_fetch(
        simple_function(i),
        error = function(e) NULL
      )
    }
  })

  # Should be < 10% overhead
  expect_lt(
    as.numeric(with_handling["elapsed"]),
    as.numeric(baseline["elapsed"]) * 1.1
  )
})
```

## Coverage Testing

### Ensure All Error Paths Tested

```r
test_that("all error conditions are covered", {
  # Track which errors occurred
  errors_seen <- character()

  test_cases <- list(
    list(input = NULL, expected = "null_input"),
    list(input = "wrong", expected = "invalid_type"),
    list(input = -1, expected = "out_of_range"),
    list(input = numeric(0), expected = "empty_input")
  )

  for (case in test_cases) {
    err <- catch_cnd(my_function(case$input))
    errors_seen <- c(errors_seen, class(err)[1])
  }

  # All expected error classes should be tested
  expect_setequal(
    errors_seen,
    paste0("mypackage_", sapply(test_cases, `[[`, "expected"))
  )
})
```

## Test Helpers

### Custom Expectations

```r
# Helper for common error assertions
expect_validation_error <- function(expr, field, expected_type) {
  err <- catch_cnd({{ expr }})

  expect_s3_class(err, "mypackage_validation_error")
  expect_equal(err$field, field)
  expect_equal(err$expected, expected_type)
}

# Usage
test_that("validates correctly", {
  expect_validation_error(
    my_function(x = "wrong"),
    field = "x",
    expected_type = "numeric"
  )
})
```

### Shared Fixtures

```r
# tests/testthat/helper.R
make_test_error <- function(class, ...) {
  error_cnd(
    message = "Test error",
    class = class,
    ...
  )
}

# In tests
test_that("handles specific error types", {
  err <- make_test_error("mypackage_network_error", status = 500)

  # Test handler logic
  result <- handle_network_error(err)
  expect_true(result$should_retry)
})
```

## Best Practices

1. **Always test custom error classes** - Not just messages
2. **Use snapshots for user-facing errors** - Ensures UX consistency
3. **Test error metadata** - Validate structured data in conditions
4. **Test error chaining** - Verify parent relationships
5. **Test recovery logic** - Don't just test that errors occur
6. **Mock external dependencies** - Trigger error conditions reliably
7. **Test argument name detection** - Verify `caller_arg()` works
8. **Use parametrized tests** - Cover multiple invalid inputs
9. **Test error handling overhead** - Ensure it's acceptable
10. **Maintain snapshot coverage** - Review snapshots in PRs

---
name: r-testing
description: R package testing with testthat 3rd edition. Use when writing R tests, fixing failing tests, debugging errors, or reviewing coverage—e.g., "write testthat tests", "fix failing R tests", "snapshot testing", "test coverage".
---

# R Testing Skill

## Purpose

Provide modern best practices for R package testing using testthat 3+. Guide test creation, fixture design, snapshot testing, and BDD-style specifications. This skill enforces testing discipline—critical practices are non-negotiable.

## Initial Setup

Initialize testing with testthat 3rd edition:

```r
usethis::use_testthat(3)
```

This creates `tests/testthat/` directory, adds testthat to `DESCRIPTION` Suggests with `Config/testthat/edition: 3`, and creates `tests/testthat.R`.

## File Organization

**YOU MUST mirror package structure:**

- Code in `R/foofy.R` → tests in `tests/testthat/test-foofy.R`
- ALWAYS use `usethis::use_r("foofy")` and `usethis::use_test("foofy")` to create paired files
- No exceptions—non-matching files cause maintenance failures

**Special files:**

- `setup-*.R` - Run during `R CMD check` only, not during `load_all()`
- `fixtures/` - Static test data files accessed via `test_path()`
- `helper-*.R` - Helper functions and custom expectations, sourced before tests
  - good for global test setup that is tailored for test execution in non-interactive or remote environments. For example, you might turn off behaviour that’s aimed at an interactive user, such as messaging or writing to the clipboard.

## Test Structure

Tests follow a three-level hierarchy: **File → Test → Expectation**

### Standard Syntax

```r
test_that("descriptive behavior", {
    result <- my_function(input)
    expect_equal(result, expected_value)
})
```

**Test descriptions** should read naturally and describe behavior, not implementation.

it is highly encouraged to write descriptions using `glue::glue()` for dynamic content:

- glue is already a dependency of testthat, so it is not expensive to use, but you must add it to `DESCRIPTION` Suggests if you use it in your tests.

```r
test_that(glue::glue("{fixture_name} returns {expected_value} for input {input}"), {
    result <- my_function(input)
    expect_equal(result, expected_value)
})
```

### BDD Syntax (describe/it)

For behavior-driven development, use `describe()` and `it()`:

```r
describe("matrix()", {
  it("can be multiplied by a scalar", {
    m1 <- matrix(1:4, 2, 2)
    m2 <- m1 * 2
    expect_equal(matrix(1:4 * 2, 2, 2), m2)
  })

  it("can be transposed", {
    m <- matrix(1:4, 2, 2)
    expect_equal(t(m), matrix(c(1, 3, 2, 4), 2, 2))
  })
})
```

**Key features:**

- `describe()` groups related specifications for a component
- `it()` defines individual specifications (like `test_that()`)
- Supports nesting for hierarchical organization
- `it()` without code creates pending test placeholders

**Use `describe()` to verify you implement the right things, use `test_that()` to ensure you do things right.**

See [references/bdd.md](references/bdd.md) for comprehensive BDD patterns, nested specifications, and test-first workflows.

## Running Tests

Three scales of testing:

**Micro** (interactive development):

```r
devtools::load_all()
expect_equal(foofy(...), expected)
```

**Mezzo** (single file):

```r
testthat::test_file("tests/testthat/test-foofy.R")
```

**Macro** (full suite):

```r
devtools::test()
devtools::check()
```

## Core Expectations

- if testing exceptions/errors, use context7 to query the docs for available exception classes and best practices around testing errors.

## Design Principles

### 1. Self-Contained Tests (Cleanup Side Effects)

YOU MUST use `withr` to manage state changes. Tests without withr::local\_\* = leaked state. Every time.

```r
test_that("function respects options", {
  withr::local_options(my_option = "test_value")
  withr::local_envvar(MY_VAR = "test")
  withr::local_package("jsonlite")

  result <- my_function()
  expect_equal(result$setting, "test_value")
  # Automatic cleanup after test
})
```

**Common withr functions:**

- `local_options()` - Temporarily set options
- `local_envvar()` - Temporarily set environment variables
- `local_tempfile()` - Create temp file with automatic cleanup
- `local_tempdir()` - Create temp directory with automatic cleanup
- `local_package()` - Temporarily attach package

### 2. Plan for Test Failure

YOU MUST write tests assuming they will fail and need debugging:

- Tests MUST run independently in fresh R sessions
- NEVER create hidden dependencies between tests—this causes irreproducible failures
- ALWAYS make test logic explicit and obvious

### 3. Repetition is Acceptable

Repeat setup code in tests rather than factoring it out. Test clarity is more important than avoiding duplication.

### 4. Use `devtools::load_all()` Workflow

During development:

- ALWAYS use `devtools::load_all()`—NEVER use `library()` for package under test
- Makes all functions available (including unexported)
- Automatically attaches testthat
- Eliminates need for `library()` calls in tests
- Using library() on the package under test = stale code. Every time.

## Snapshot Testing

For complex output that's difficult to verify programmatically, use snapshot tests. See [references/snapshots.md](references/snapshots.md) for complete guide.

**Basic pattern:**

```r
test_that("error message is helpful", {
  expect_snapshot(
    error = TRUE,
    validate_input(NULL)
  )
})
```

Snapshots stored in `tests/testthat/_snaps/`.

**Workflow—YOU MUST complete all steps:**

```r
devtools::test()                    # Creates new snapshots

# IMMEDIATELY after creating snapshots:
testthat::snapshot_review('name')   # Review changes—never skip this step
```

Unreviewed snapshots = undetected regressions. Every time.

## Test Fixtures and Data

Three approaches for test data:

**1. Constructor functions** - Create data on-demand:

```r
new_sample_data <- function(n = 10) {
  data.frame(id = seq_len(n), value = rnorm(n))
}
```

**2. Local functions with cleanup** - Handle side effects:

```r
local_temp_csv <- function(data, env = parent.frame()) {
  path <- withr::local_tempfile(fileext = ".csv", .local_envir = env)
  write.csv(data, path, row.names = FALSE)
  path
}
```

**3. Static fixture files** - Store in `fixtures/` directory:

```r
data <- readRDS(test_path("fixtures", "sample_data.rds"))
```

See [references/fixtures.md](references/fixtures.md) for detailed fixture patterns.

## Common Patterns

### Testing Errors with Specific Classes

```r
test_that("validation catches errors", {
  expect_error(
    validate_input("wrong_type"),
    class = "vctrs_error_cast"
  )
})
```

### Testing with Temporary Files

```r
test_that("file processing works", {
  temp_file <- withr::local_tempfile(
    lines = c("line1", "line2", "line3")
  )

  result <- process_file(temp_file)
  expect_equal(length(result), 3)
})
```

### Testing with Modified Options

```r
test_that("output respects width", {
  withr::local_options(width = 40)

  output <- capture_output(print(my_object))
  expect_lte(max(nchar(strsplit(output, "\n")[[1]])), 40)
})
```

### Testing Multiple Related Cases

```r
test_that("str_trunc() handles all directions", {
  trunc <- function(direction) {
    str_trunc("This string is moderately long", direction, width = 20)
  }

  expect_equal(trunc("right"), "This string is mo...")
  expect_equal(trunc("left"), "...erately long")
  expect_equal(trunc("center"), "This stri...ely long")
})
```

### Custom Expectations in Helper Files

```r
# In tests/testthat/helper-expectations.R
expect_valid_user <- function(user) {
  expect_type(user, "list")
  expect_named(user, c("id", "name", "email"))
  expect_type(user$id, "integer")
  expect_match(user$email, "@")
}

# In test file
test_that("user creation works", {
  user <- create_user("test@example.com")
  expect_valid_user(user)
})
```

## File System Discipline

**YOU MUST ALWAYS write to temp directory—no exceptions:**

```r
# Good
output <- withr::local_tempfile(fileext = ".csv")
write.csv(data, output)

# Bad - writes to package directory
write.csv(data, "output.csv")
```

**ALWAYS access test fixtures with `test_path()`—relative paths break in CI:**

```r
# Good—ALWAYS use test_path()
data <- readRDS(test_path("fixtures", "data.rds"))

# Bad—relative paths cause CI failures. Every time.
data <- readRDS("fixtures/data.rds")
```

## References (Load on Demand)

- **[references/advanced.md](references/advanced.md)** - Load for skipping tests, secrets management, CRAN requirements, custom expectations, or parallel testing
- **[references/bdd.md](references/bdd.md)** - Load when using describe/it BDD-style testing, nested specifications, or test-first workflows
- **[references/snapshots.md](references/snapshots.md)** - Load when implementing snapshot testing, transforms, or variants
- **[references/fixtures.md](references/fixtures.md)** - Load when designing fixture patterns, database fixtures, or helper files

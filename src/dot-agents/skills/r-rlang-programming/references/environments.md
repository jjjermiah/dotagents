# Environments and Scoping Reference

rlang tools for explicit environment manipulation and scoping control.

## Why Environments?

Environments are R's scoping mechanism. You need explicit control when:

1. **Implementing DSLs** - Custom evaluation contexts
2. **Data masking** - Blending data and code environments
3. **Debugging** - Inspecting call stacks and closures
4. **Metaprogramming** - Controlling where code evaluates

## Creating Environments

### `env()` - Create New Environment

```r
# Empty environment
e <- env()

# With parent
e <- env(parent = global_env())

# With bindings
e <- env(
  x = 1,
  y = 2,
  fn = function() x + y
)

# Chained
e <- env(env(global_env()), x = 1, y = 2)
```

### `new_environment()` - From List

```r
# Convert list to environment
data <- list(a = 1, b = 2)
e <- new_environment(data)

# With parent
e <- new_environment(data, parent = base_env())
```

## Environment Hierarchy

### Standard Environments

```r
# Global environment (user workspace)
global_env()

# Base package environment
base_env()

# Empty environment (top of chain)
empty_env()

# Current environment
current_env()

# Caller's environment
caller_env()
```

### Navigating Hierarchy

```r
# Get parent
env_parent(e)

# Get all parents up to empty
env_parents(e)

# Get last parent before empty
env_tail(e)

# Count depth
env_depth(e)
```

### Testing Hierarchy

```r
# Does env inherit from parent?
env_inherits(e, global_env())

# Is this specific environment?
identical(env, global_env())
```

## Environment Bindings

### Adding Bindings

#### `env_bind()` - Regular Binding

```r
e <- env()

# Bind single value
env_bind(e, x = 10)

# Bind multiple
env_bind(e,
  x = 10,
  y = 20,
  z = 30
)

# Bind expressions (evaluated immediately)
env_bind(e, result = compute_value())
```

#### `env_bind_lazy()` - Lazy Binding

Value computed only when accessed:

```r
# Expensive computation delayed
env_bind_lazy(e,
  big_data = read_csv("huge.csv"),
  result = expensive_computation()
)

# Not computed yet
exists("big_data", envir = e)  # TRUE
# Only computed when accessed
e$big_data  # Now computed
```

#### `env_bind_active()` - Active Binding

Re-computed every access:

```r
e <- env()

# Value changes each time
env_bind_active(e,
  time = function() Sys.time(),
  random = function() runif(1)
)

e$time    # Current time
Sys.sleep(1)
e$time    # New time

e$random  # Random value
e$random  # Different random value
```

#### `%<~%` - Delayed Assignment Operator

```r
e <- env()

# Equivalent to env_bind_lazy()
env_bind(e, x %<~% expensive_function())
```

### Retrieving Bindings

#### `env_get()` - Get Single Value

```r
env_get(e, "x")

# With default
env_get(e, "missing", default = NA)

# Inherit from parents
env_get(e, "x", inherit = TRUE)
```

#### `env_get_list()` - Get Multiple Values

```r
env_get_list(e, c("x", "y", "z"))
#> $x
#> [1] 10
#> $y
#> [1] 20
#> $z
#> [1] 30
```

### Checking Bindings

```r
# Does environment have binding?
env_has(e, "x")

# Multiple bindings
env_has(e, c("x", "y", "missing"))
#> x     y  missing
#> TRUE  TRUE FALSE

# Check in parents too
env_has(e, "x", inherit = TRUE)
```

### Listing Bindings

```r
# All names
env_names(e)

# Count
env_length(e)
```

### Removing Bindings

```r
# Remove specific bindings
env_unbind(e, "x")
env_unbind(e, c("x", "y", "z"))

# Note: Cannot unbind from locked environments
```

### Modifying Bindings

#### `env_poke()` - Set/Modify Binding

```r
# Create or modify
env_poke(e, "x", 100)

# Unlike env_bind(), env_poke() creates parent if needed
env_poke(e, "x", 10, create = TRUE)
```

#### `env_cache()` - Compute Once, Cache

```r
e <- env()

# Only computes if not already present
env_cache(e, "result", expensive_computation())

# Subsequent calls return cached value
env_cache(e, "result", expensive_computation())  # Uses cached
```

## Temporary Bindings

### `local_bindings()` - Scoped Bindings

Bindings active only during function execution:

```r
test_function <- function() {
  # Temporarily change global bindings
  local_bindings(x = 100, y = 200, .env = global_env())

  # x and y are 100 and 200 here
  print(x)

  # Automatically restored when function exits
}

test_function()
# x and y back to original values
```

### `with_bindings()` - Evaluate with Bindings

```r
x <- 1

result <- with_bindings(
  x + y,
  x = 10,
  y = 20,
  .env = current_env()
)
#> [1] 30

# x still 1 after
```

## Environment Properties

### Getting/Setting Environment

```r
# Get environment of function
f <- function() x + 1
env_f <- fn_env(f)

# Set environment
fn_env(f) <- new_env

# Get environment of formula
form <- ~x + y
env_form <- f_env(form)

# Set formula environment
f_env(form) <- new_env

# Get environment of quosure
q <- quo(x + 1)
env_q <- quo_get_env(q)
```

### Environment Metadata

```r
# Get printable label
env_label(e)

# Get name (for packages/namespaces)
env_name(e)

# Print environment nicely
env_print(e)
#> <environment: 0x7f8e3c0a1b00>
#> parent: <environment: global>
#> bindings:
#>  * x: <dbl>
#>  * y: <dbl>
```

## Package Environments

### Namespace Environments

```r
# Get package namespace
ns <- ns_env("dplyr")

# Namespace imports environment
imports <- ns_imports_env("dplyr")

# Namespace name
ns_env_name(ns)

# Is this a namespace?
is_namespace(ns)
```

### Search Path

```r
# All attached environments
search_envs()

# Get specific search env
base <- search_env("package:base")

# Package environment (if attached)
dplyr_env <- pkg_env("dplyr")

# Package environment name
pkg_env_name(dplyr_env)

# Is package attached?
is_attached("dplyr")
```

## Call Stack

### Current and Caller Context

```r
my_function <- function() {
  # Current function's environment
  this_env <- current_env()

  # Caller's environment
  caller <- caller_env()

  # Current function call
  this_call <- current_call()

  # Current function object
  this_fn <- current_fn()
}
```

### Caller Information

```r
helper <- function() {
  # Who called me?
  call <- caller_call()
  env <- caller_env()
  fn <- caller_fn()

  list(call = call, env = env, fn = fn)
}

wrapper <- function() {
  helper()
}

wrapper()
#> $call
#> helper()
#> $env
#> <environment: wrapper()>
#> $fn
#> <function: wrapper>
```

### Frame Access

```r
# Specific frame in stack
frame_call(n = 1)   # Call n frames up
frame_fn(n = 2)     # Function n frames up
```

## Environment Manipulation

### Cloning

```r
# Shallow clone (bindings reference same objects)
e2 <- env_clone(e)

# Deep clone needed? Use other approaches
```

### Coalescing

Find first binding in chain of environments:

```r
# Create chain
e1 <- env(x = 1, y = 2)
e2 <- env(y = 20, z = 30)
e3 <- env(z = 300)

# Get first occurrence of each name
env_coalesce(e1, e2, e3)
#> <environment>
#> x: 1 (from e1)
#> y: 2 (from e1)
#> z: 30 (from e2)
```

### Type Checking

```r
is_environment(e)
is_bare_environment(e)  # No class attribute
```

### Conversion

```r
# List to environment
as_environment(list(x = 1, y = 2))

# Data frame to environment
as_environment(mtcars[1, ])

# Environment to list
as.list(e)
```

## Common Patterns

### Evaluation Context

```r
# Create isolated evaluation context
eval_context <- function(data, code) {
  # Create environment with data
  ctx <- new_environment(data, parent = caller_env())

  # Evaluate in context
  eval_tidy(code, env = ctx)
}

data <- list(x = 1:10, y = 11:20)
eval_context(data, quo(mean(x + y)))
```

### Sandboxed Evaluation

```r
# Restrict available functions
safe_eval <- function(expr) {
  # Empty parent = no access to global env
  sandbox <- env(
    parent = empty_env(),
    # Only allow specific functions
    sum = sum,
    mean = mean,
    c = c
  )

  eval_tidy(enexpr(expr), env = sandbox)
}

safe_eval(mean(c(1, 2, 3)))  # Works
safe_eval(system("ls"))       # Error: system not found
```

### Package-like Environment

```r
create_module <- function() {
  # Module environment
  mod <- env()

  # Private state
  env_bind(mod, .private = list(counter = 0))

  # Public functions
  env_bind(mod,
    increment = function() {
      .private$counter <- .private$counter + 1
      invisible(.private$counter)
    },
    get_count = function() {
      .private$counter
    }
  )

  mod
}

module <- create_module()
module$increment()
module$get_count()  #> 1
```

### Lazy Loading

```r
create_lazy_data <- function() {
  e <- env()

  # Bind expensive computations lazily
  env_bind_lazy(e,
    big_data = {
      message("Loading big data...")
      readRDS("big.rds")
    },
    model = {
      message("Training model...")
      train_model(big_data)
    }
  )

  e
}

data <- create_lazy_data()
# Nothing computed yet
data$model  # Computes big_data, then model
```

### Dynamic Scoping

```r
# Temporarily override in dynamic scope
with_setting <- function(code, setting = "default") {
  local_bindings(
    .current_setting = setting,
    .env = global_env()
  )

  force(code)
}

get_setting <- function() {
  if (env_has(global_env(), ".current_setting")) {
    env_get(global_env(), ".current_setting")
  } else {
    "none"
  }
}

get_setting()  # "none"

with_setting({
  get_setting()  # "custom"
}, setting = "custom")

get_setting()  # "none" again
```

## Debugging Environments

```r
# Inspect current environment bindings
env_print(current_env())

# See what's in scope
env_names(current_env())

# Check parent chain
env_parents(current_env())

# Find where binding is defined
find_binding <- function(name, env = caller_env()) {
  while (!identical(env, empty_env())) {
    if (env_has(env, name, inherit = FALSE)) {
      return(env)
    }
    env <- env_parent(env)
  }
  NULL
}
```

## Best Practices

1. **Use `caller_env()` in helpers** - Maintain proper scoping context
2. **Explicit parents** - Always specify parent when it matters
3. **Don't pollute global env** - Create local environments for temp work
4. **Use `local_bindings()`** - For temporary changes
5. **Document environment contracts** - Make clear what environment a function expects
6. **Test with isolated envs** - Avoid hidden dependencies

## Base R Comparison

| rlang           | Base R             |
| --------------- | ------------------ |
| `env()`         | `new.env()`        |
| `env_bind()`    | `assign()`         |
| `env_get()`     | `get()`            |
| `env_has()`     | `exists()`         |
| `env_unbind()`  | `rm()`             |
| `env_names()`   | `ls()` / `names()` |
| `caller_env()`  | `parent.frame()`   |
| `current_env()` | `environment()`    |

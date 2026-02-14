---
name: r-expert
description: Core R programming skill for all R code, package development, and data science workflows. Use when writing R functions, building packages, using tidyverse (dplyr, ggplot2, purrr), creating Shiny apps, working with R Markdown/Quarto, or doing data analysis—e.g., "write an R function", "refactor this R code", "create a Shiny dashboard", "set up package tests", "debug R errors".
---

# R Expert Skill

## Purpose

YOU MUST apply this skill for ALL R code, package development, and data science workflows. This skill provides production-grade R guidance and enforces modern best practices. No exceptions.

IMMEDIATELY use Context7 for package-specific APIs—outdated documentation causes bugs. Every time.

## Complementary Skills (Required Announcement)

When loading any complementary skill, YOU MUST announce: "Loading [skill-name] with r-expert"

Load these additional skills IN COMBINATION with r-expert when applicable:

- **r-testing** - When writing/fixing/reviewing R tests and test fixtures
- **r-benchmarking** - When measuring performance, timing, profiling, or memory allocation
- **r-error-handling** - When implementing structured error handling and custom conditions
- **r-rlang-programming** - When using metaprogramming, NSE, tidy evaluation, or rlang APIs

NEVER skip complementary skills when the task requires them. Skipping specialized guidance = substandard results. Every time.

## Core Workflow

FOLLOW THIS SEQUENCE. No deviations.

1. **Identify task type** (data manipulation, visualization, package dev, etc.)
2. **ALWAYS use Context7 FIRST** for package-specific APIs—see [references/r-context7-mappings.md](references/r-context7-mappings.md). Code written without Context7 verification = unreliable.
3. **Apply tidyverse patterns** as the default approach
4. **Verify reproducibility** before delivering results

Package documentation without Context7 verification = stale information. Every time.

## Package Documentation (ALWAYS USE Context7)

YOU MUST use Context7 for ALL package-specific documentation. Hard-coded knowledge becomes outdated. No exceptions.

Standard library IDs:

```text
# Tidyverse core
/tidyverse/dplyr       # Data manipulation
/tidyverse/ggplot2     # Visualization
/tidyverse/tidyr       # Data reshaping
/tidyverse/purrr       # Functional programming
/tidyverse/readr        # Data import

# Development
/r-lib/devtools         # Package development
/r-lib/usethis          # Project setup
/r-lib/testthat         # Testing

# ALWAYS check references/r-context7-mappings.md for the complete list
```

R code written without Context7 lookup = latent bugs. Every production R workflow uses Context7 verification.

## Code Style (Non-Negotiable)

YOU MUST follow these standards. No exceptions.

- **ALWAYS use** `package::function()` for clarity—implicit imports cause namespace conflicts
- **ALWAYS default to tidyverse** for data manipulation—base R without good reason = technical debt
- **ALWAYS use snake_case** for functions and variables
- **NEVER use explicit returns** unless early exit required
- **ALWAYS keep lines** within 80-100 characters

Code deviating from these standards = rework required. Every time.

## Essential Patterns

### Data Pipeline

```r
data <- raw_data |>
  dplyr::filter(year >= 2020) |>
  dplyr::mutate(
    total = price * quantity,
    category = forcats::fct_lump(category, n = 5)
  ) |>
  dplyr::group_by(region) |>
  dplyr::summarise(
    revenue = sum(total, na.rm = TRUE),
    .groups = "drop"
  )
```

### Safe File Operations

```r
# Use withr for temporary state
withr::with_tempfile("tmp", {
  readr::write_csv(data, tmp)
  processed <- readr::read_csv(tmp, show_col_types = FALSE)
})
```text

### Package Structure

```text
my-package/
├── DESCRIPTION          # Package metadata
├── NAMESPACE           # Auto-generated exports
├── R/                  # Source code
│   ├── utils.R         # Internal helpers
│   └── main-feature.R  # Main functionality
├── tests/
│   └── testthat/       # Tests
├── man/                # Documentation (auto)
└── README.Rmd          # Package README
```

## References (Load on Demand)

- **[references/r-context7-mappings.md](references/r-context7-mappings.md)** - YOU MUST load this BEFORE querying Context7 for R packages. Contains verified library ID mappings for tidyverse, Shiny, testing, ML, and database packages.

Context7 queries without the mappings reference = incorrect library IDs. Always check the reference first.

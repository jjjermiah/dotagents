---
name: r-documentation
description: |
  R package documentation with roxygen2 and Rd files, including mathematical notation, selective Rd parsing, and structured sections. Use when writing/updating/refactoring roxygen2 documentation, adding math formulas to R help pages, programmatically reading Rd files, or troubleshooting Rd rendering
---

# R Documentation

## Purpose

Write and manipulate R package documentation using roxygen2 and the Rd format. Covers structured documentation (sections, lists, tables), mathematical notation (`\eqn`/`\deqn`), and programmatic Rd parsing/extraction.

## Roxygen2 Structure

Roxygen2 blocks map to Rd sections. The implicit structure is:

```r
#' Title (first paragraph)
#'
#' Description (second paragraph).
#'
#' Details (third+ paragraphs).
#' @param x Argument docs.
#' @return What it returns.
#' @export
my_func <- function(x) {}
```

Explicit tags override implicit placement: `@title`, `@description`, `@details`.

### Multiple `@details` blocks

`@details` can appear multiple times — all merge into a single Details section:

```r
#' @details
#' First block.
#'
#' @param x Input.
#'
#' @details
#' Second block (merged with first in output).
```

### Custom sections

Two equivalent approaches:

```r
#' @section Algorithm:
#' Description of the algorithm.
```

Or with Markdown headings (requires `Roxygen: list(markdown = TRUE)` in DESCRIPTION):

```r
#' @details
#' # Algorithm
#' Description of the algorithm.
#'
#' ## Phase 1
#' ...
```

Top-level `#` creates `\section{}`. `##`/`###` create subsections. Headings only valid after `@description` or `@details`.

## Lists, Tables, and Preformatted Blocks

**Gotcha**: `\describe{\item{label}{desc}}` uses two-arg `\item`. `\itemize{\item}` and `\enumerate{\item}` use bare `\item`. Mixing these up is a common error.

```r
#' \tabular{lcr}{
#'   Name \tab Value \tab Unit \cr
#'   foo  \tab 42    \tab kg   \cr
#' }
```

Column alignment: `l`/`c`/`r`. Columns: `\tab`. Rows: `\cr`.

Use `\preformatted{}` for matrix output examples — preserves exact whitespace.

## Mathematical Notation

Two macros for math in Rd:

| Macro | Purpose | LaTeX equivalent |
|-------|---------|-----------------|
| `\eqn{latex}{ascii}` | Inline math | `$...$` |
| `\deqn{latex}{ascii}` | Display (block) math | `$$...$$` |

**Always use the two-argument form** for anything beyond trivial expressions. The second argument is the plain-text fallback shown in terminal `?help`.

### Rendering by output format

| Output | Renderer | Math source |
|--------|----------|-------------|
| PDF | Full LaTeX | 1st argument |
| HTML (R >= 4.2.0) | KaTeX | 1st argument |
| Text/terminal | Plain text | 2nd argument (or raw LaTeX if omitted) |

### Quick examples

```r
#' The variance is \eqn{\sigma^2}{sigma^2}.
#'
#' The expected value:
#' \deqn{E[X] = \sum_{i} p_i x_i}{E[X] = sum(p_i * x_i)}
```

### Symbol definition rule

YOU MUST define every symbol before or at its first use. Never introduce `P`, `O`, `t`, etc. in a formula without saying what they are in the surrounding prose.

```r
#' Let \eqn{P_{ij}}{P[i,j]} be the joint probability and
#' \eqn{O_{ij}}{O[i,j]} the outcome value. Then:
#' \deqn{E[X] = \sum_{i,j} P_{ij} \cdot O_{ij}}{E[X] = sum(P[i,j] * O[i,j])}
```

For detailed math formatting syntax, multi-line equations, mathjaxr, and gotchas, load [references/math-formatting.md](references/math-formatting.md).

## Programmatic Rd Parsing

`tools::parse_Rd()` parses the entire Rd file into a nested tagged list. There is no partial parsing — selective reading happens post-parse by filtering tags.

### Extract tag names

```r
rd <- tools::parse_Rd("man/my_function.Rd")
tags <- vapply(rd, attr, character(1L), "Rd_tag")
# => "\\name", "\\alias", "\\title", "\\description", ...
```

### Extract a section's text

```r
idx <- which(tags == "\\description")
trimws(paste(unlist(rd[[idx[1L]]]), collapse = ""))
```

### Render one section to text

```r
fragment <- rd[which(tags == "\\description")]
class(fragment) <- "Rd"
tools::Rd2txt(fragment, out = stdout(), fragment = TRUE)
```

The `fragment = TRUE` flag is essential when rendering subsets.

For full patterns (batch extraction, HTML rendering, helper packages like `gbRd`/`Rdpack`), load [references/rd-parsing.md](references/rd-parsing.md).

## Verification Workflow

After writing or editing roxygen2 documentation:

```r
# 1. Regenerate Rd files
roxygen2::roxygenise()

# 2. Parse and validate (should produce no output = success)
rd <- tools::parse_Rd("man/MyTopic.Rd")
tools::checkRd(rd)

# 3. Render to text (verify terminal help looks right)
tools::Rd2txt(rd, out = stdout())
```

Check for:
- Unbalanced braces (most common Rd error)
- Missing ASCII fallbacks on complex `\eqn`/`\deqn`
- Symbols used before definition
- `\preformatted{}` blocks rendering with correct whitespace

## Key Rules

- `$...$` and `$$...$$` are **NOT supported** in Rd. Use `\eqn{}`/`\deqn{}`.
- Markdown is **NOT processed** inside `\eqn{}`/`\deqn{}` (they are verbatim).
- `\\` for LaTeX newlines requires `\\\\` in roxygen2 source.
- `\describe{\item{}{}}` takes two-arg items. `\itemize{\item}` takes bare items.
- Always verify in text output (`Rd2txt`), not just HTML — terminal users see the ASCII fallback.

## References (Load on Demand)

- **[references/math-formatting.md](references/math-formatting.md)** — Load when writing complex math (multi-line equations, Greek letters, mathjaxr, amsmath environments) or debugging math rendering issues.
- **[references/rd-parsing.md](references/rd-parsing.md)** — Load when programmatically extracting or manipulating Rd file contents (batch processing, section extraction, format conversion, helper packages).

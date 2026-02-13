# Mathematical Notation in Roxygen2 / Rd

Advanced reference for multi-line equations, rendering edge cases, mathjaxr, and common mistakes. For the two-argument `\eqn{}`/`\deqn{}` basics and rendering table, see SKILL.md.

## Inline Math: `\eqn{}`

Two-argument form (recommended):

```r
#' \eqn{latex}{ascii}
#' \eqn{\sigma^2}{sigma^2}
#' \eqn{P_{ij}}{P[i,j]}
#' \eqn{m \times n}{m x n}
```

Single-argument form (only for simple expressions where LaTeX = readable text):

```r
#' \eqn{a + b}
#' \eqn{O(n^2)}
```

Rules:
- Content is **verbatim** — no Rd markup or Markdown processed inside.
- Backslash `\` is the LaTeX command prefix.
- `%` must be escaped as `\%` in raw Rd (roxygen2 handles this automatically).

## Display Math: `\deqn{}`

Block/centered equation. Same two-argument pattern:

```r
#' \deqn{x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}}{x = (-b +/- sqrt(b^2 - 4ac)) / 2a}
```

## Multi-line Equations

### R >= 4.2.2: amsmath in PDF

Available since R 4.2.2. Use `Depends: R (>= 4.2.2)` (or conservatively `R (>= 4.3)`) to ensure support:

```r
#' \deqn{
#'   \begin{aligned}
#'     a &= b + c \\\\
#'     d &= e + f
#'   \end{aligned}
#' }
```

**Critical**: `\\` for LaTeX newlines must be `\\\\` in roxygen2 source.

### Pre-R 4.2 or simple cases

Use separate `\deqn{}` calls:

```r
#' Step 1:
#' \deqn{y = Ax}{y = A * x}
#' Step 2:
#' \deqn{z = B^{-1}y}{z = inv(B) * y}
```

### Whitespace gotcha

Roxygen2 may collapse multi-line `\deqn{}` content. Provide an explicit second argument for the ASCII representation when the equation spans multiple source lines:

```r
#' \deqn{
#'   x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
#' }{
#'   x = (-b +/- sqrt(b^2 - 4ac)) / (2a)
#' }
```

## Rendering Differences

| Output | Renderer | Notes |
|--------|----------|-------|
| PDF | Full LaTeX | Best rendering. amsmath since R 4.2.2. |
| HTML | KaTeX (R >= 4.2.0) | Good. Prior to 4.2.0, showed ASCII fallback. |
| Text | Plain text | Shows 2nd argument. If omitted, raw LaTeX. |

### KaTeX limitations (HTML)

- No `\newcommand` in equations.
- Limited amsmath (`aligned`, `cases` work; exotic environments may not).
- No `\text{}` nesting in some contexts.

### Practical implications

- Always provide ASCII fallback for: Greek letters, fractions, subscripts/superscripts, summations.
- Simple expressions like `\eqn{a + b}` are fine single-argument.
- Test in both `?func` (RStudio HTML) and `tools::Rd2txt()` (terminal text).

## Common Patterns

### Subscripted matrix notation

```r
#' \eqn{P_{ij}}{P[i,j]}
#' \eqn{O_{ij}}{O[i,j]}
#' \eqn{A_{k \times m}}{A (k x m)}
```

### Summations

```r
#' \eqn{\sum_{i=1}^{n} x_i}{sum(x_i, i=1..n)}
#' \deqn{\sum_{i,j} P_{ij} \cdot O_{ij}}{sum(P[i,j] * O[i,j])}
```

### Set notation and inequalities

```r
#' \eqn{x \in \{0, 1\}}{x in {0, 1}}
#' \eqn{x \geq 0}{x >= 0}
#' \eqn{\|A\|_F}{||A||_F}
```

## mathjaxr Package

For richer MathJax rendering or R < 4.2.0 support.

### Setup

1. `Imports: mathjaxr` in DESCRIPTION
2. `RdMacros: mathjaxr` in DESCRIPTION

No NAMESPACE directive is needed — mathjaxr works entirely through the `RdMacros` mechanism.

### Usage

```r
#' @description
#' \loadmathjax
#' The matrix exponential \mjeqn{e^{At}}{exp(A*t)}.
#'
#' @details
#' \mjdeqn{e^{At} = \sum_{k=0}^{\infty} \frac{(At)^k}{k!}}{exp(A*t) = sum((A*t)^k / k!)}
```

### Macro variants

| Macro | Args | Purpose |
|-------|------|---------|
| `\mjeqn{latex}{ascii}` | 2 | Inline |
| `\mjdeqn{latex}{ascii}` | 2 | Display |
| `\mjseqn{text}` | 1 | Inline, single arg |
| `\mjsdeqn{text}` | 1 | Display, single arg |
| `\mjteqn{pdf}{html}{ascii}` | 3 | Inline, separate PDF/HTML |
| `\mjtdeqn{pdf}{html}{ascii}` | 3 | Display, separate PDF/HTML |

### When to use mathjaxr vs built-in

- **Built-in**: Sufficient for most packages. KaTeX in HTML since R 4.2.0. No dependency.
- **mathjaxr**: Full MathJax, more LaTeX extensions, R < 4.2.0 HTML support.

## Common Mistakes

1. **Using `$...$`**: NOT supported in Rd. Use `\eqn{}`/`\deqn{}`.
2. **Forgetting ASCII fallback**: Complex expressions unreadable in terminal.
3. **Unbalanced braces**: Every `{` needs `}`. LaTeX groups add complexity — count carefully.
4. **Markdown inside math**: `\eqn{x_*i*}` fails. Use `\eqn{x_i}`.
5. **Expecting formatting in text**: `\eqn{x_{ij}}` shows as `x_{ij}` in terminal. Provide `\eqn{x_{ij}}{x_ij}`.
6. **`\\` vs `\\\\`**: LaTeX newlines in roxygen2 require four backslashes.

## Complete Example

```r
#' Singular Value Decomposition
#'
#' @description
#' Factorizes matrix \eqn{A} as
#' \deqn{A = U \Sigma V^T}{A = U * Sigma * V'}
#' where \eqn{U} and \eqn{V} are orthogonal and
#' \eqn{\Sigma}{Sigma} is diagonal.
#'
#' @details
#' The singular values \eqn{\sigma_1 \geq \cdots \geq \sigma_r > 0}{s1 >= ... >= sr > 0}
#' are square roots of eigenvalues of \eqn{A^T A}{A'A}.
#'
#' Matrix norms via singular values:
#' \describe{
#'   \item{Spectral}{\eqn{\|A\|_2 = \sigma_1}{||A||_2 = s1}}
#'   \item{Frobenius}{\eqn{\|A\|_F = \sqrt{\sum \sigma_i^2}}{||A||_F = sqrt(sum(si^2))}}
#' }
#'
#' @param A Numeric matrix, \eqn{m \times n}{m x n}.
#' @param k Number of singular values to retain.
#' @return List with components \code{u}, \code{d}, \code{v}.
#' @export
my_svd <- function(A, k = min(nrow(A), ncol(A))) {}
```

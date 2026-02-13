# Programmatic Rd Parsing

Full patterns for selective Rd extraction, batch processing, and helper packages. For the core tag-extraction and `fragment = TRUE` rendering pattern, see SKILL.md.

## Parsed Rd Structure

`tools::parse_Rd()` returns an object of class `"Rd"` — a **nested list of tagged elements**. Each top-level element has an `"Rd_tag"` attribute:

```
"\\name", "\\alias", "\\title", "\\description", "\\usage",
"\\arguments", "\\details", "\\value", "\\section", "\\examples",
"\\seealso", "\\keyword", "\\note", "\\author", "\\references",
"TEXT", "COMMENT"
```

Leaf nodes are character strings tagged `"TEXT"`, `"RCODE"`, `"VERB"`, `"\\code"`, `"\\link"`, etc.

**Key constraint**: `parse_Rd()` always parses the entire file. Selective extraction happens post-parse.

## Core Functions

### `tools::parse_Rd()`

```r
rd <- tools::parse_Rd(
  file,
  encoding = "unknown",
  fragment = FALSE,   # TRUE for Rd snippets
  macros = file.path(R.home("share"), "Rd", "macros", "system.Rd")
)
```

### Extract tag names

```r
tags <- vapply(rd, attr, character(1L), "Rd_tag")
```

This is equivalent to `tools:::RdTags(rd)` (internal function, trivial to reimplement).

### Extract text from a tag

```r
idx <- which(tags == "\\name")
name <- trimws(paste(unlist(rd[[idx[1L]]]), collapse = ""))
```

### `tools:::.Rd_get_metadata()` (internal)

Shortcut for simple text extraction:

```r
tools:::.Rd_get_metadata(rd, "name")      # \\name value
tools:::.Rd_get_metadata(rd, "alias")     # all \\alias entries
tools:::.Rd_get_metadata(rd, "keyword")   # all \\keyword entries
```

### `tools::Rd_db()`

Named list of all parsed Rd objects for a package:

```r
db <- tools::Rd_db("stats")              # installed package
db <- tools::Rd_db(dir = "path/to/pkg")  # source directory
```

## Selective Rendering

### Render one section to text

```r
fragment <- rd[which(tags == "\\description")]
class(fragment) <- "Rd"
tools::Rd2txt(fragment, out = stdout(), fragment = TRUE)
```

### Render one section to HTML

```r
fragment <- rd[which(tags == "\\details")]
class(fragment) <- "Rd"
html <- capture.output(
  tools::Rd2HTML(fragment, out = "", fragment = TRUE, standalone = FALSE)
)
```

**`fragment = TRUE` is essential** when rendering subsets. Without it, the renderers expect `\name` and `\title` to be present.

## Practical Patterns

### Extract name + title + description (zero dependencies)

```r
rd_extract_basics <- function(rd_file) {
  rd <- tools::parse_Rd(rd_file)
  tags <- vapply(rd, attr, character(1L), "Rd_tag")

  get_text <- function(tag) {
    idx <- which(tags == tag)
    if (length(idx) == 0L) return(NA_character_)
    trimws(paste(unlist(rd[[idx[1L]]]), collapse = ""))
  }

  list(
    name        = get_text("\\name"),
    title       = get_text("\\title"),
    description = get_text("\\description"),
    aliases     = vapply(
      rd[which(tags == "\\alias")],
      function(x) trimws(paste(unlist(x), collapse = "")),
      character(1L)
    )
  )
}
```

### Render a single section to a string

```r
rd_section_to_text <- function(rd_file, section) {
  rd <- tools::parse_Rd(rd_file)
  tags <- vapply(rd, attr, character(1L), "Rd_tag")
  idx <- which(tags == section)
  if (length(idx) == 0L) return(character(0L))

  fragment <- rd[idx]
  class(fragment) <- "Rd"
  con <- textConnection(NULL, "w")
  on.exit(close(con))
  tools::Rd2txt(fragment, out = con, fragment = TRUE)
  textConnectionValue(con)
}
```

### Batch extract from all Rd files

```r
rd_extract_all <- function(pkg_dir, fields = c("\\name", "\\title", "\\description")) {
  rd_files <- list.files(file.path(pkg_dir, "man"), "\\.Rd$", full.names = TRUE)

  lapply(setNames(rd_files, basename(rd_files)), function(f) {
    rd <- tools::parse_Rd(f)
    tags <- vapply(rd, attr, character(1L), "Rd_tag")
    setNames(lapply(fields, function(field) {
      idx <- which(tags == field)
      if (length(idx) == 0L) return(NA_character_)
      trimws(paste(unlist(rd[[idx[1L]]]), collapse = ""))
    }), fields)
  })
}
```

## Helper Packages

### `gbRd` (lightweight, stable — last CRAN update 2017)

Best for selective section extraction:

```r
# From installed help
gbRd::Rd_fun("data.frame", keep_section = "\\arguments")
gbRd::Rd_help2txt("seq", keep_section = "\\examples", omit_sec_header = TRUE)

# From parsed Rd object
gbRd::Rdo_section(rd, "\\description")
```

Note: `Rd_fun` and `Rd_help2txt` work with installed help (via `help()`). For source files, parse with `parse_Rd` first then use `Rdo_section`.

### `Rdpack` (comprehensive, active)

Full Rd manipulation toolkit:

```r
Rdpack::Rdo_sections(rd)            # list all sections
Rdpack::Rdo_locate_core_section(rd) # find standard sections
Rdpack::Rdo_tags(rd)                # tag names
Rdpack::Rdapply(rd, fun)            # apply over Rd tree
Rdpack::parse_Rdtext(text, section) # parse Rd source snippet
Rdpack::Rdo2Rdf(rd)                 # convert back to Rd source
```

Heavier dependency (depends on `rbibutils`) but much more powerful for Rd manipulation.

### Other packages

| Package | Use case | Status |
|---------|----------|--------|
| `Rd2roxygen` | Convert Rd to roxygen2 comments | Active |
| `Rd2md` | Convert Rd to Markdown | Active |
| `pkgdown` | Has `rd2html()` for Rd-string-to-HTML | Active |
| `installr` | `fetch_tag_from_Rd()` — Windows-focused, heavyweight for one function; prefer base R approach above | Active |
| `Rd` | Had `Rd_get_element()` | **Archived 2019 — do not use** |

## Caveats

1. **No partial parsing**: `parse_Rd()` reads the whole file. Filter afterward.
2. **`tools:::RdTags` is internal**: Use `:::` or reimplement the one-liner.
3. **`fragment = TRUE`**: Required for rendering subsets. Without it, renderers expect complete Rd.
4. **`\Sexpr` macros**: Unevaluated in source Rd. Evaluated at build/install time. `Rd_db()` on installed packages has build-stage Sexpr resolved.
5. **Multiple matches**: Tags like `\alias`, `\keyword`, `\concept` appear multiple times. Use `which()` not `match()`.
6. **Nested structure**: `\arguments` contains `\item` sub-elements. `\section{Title}{Content}` has a custom title. Walking these requires recursive list traversal.

---
name: r-benchmarking
description: R benchmarking, profiling, and performance analysis with reproducibility and measurement rigor. Use when timing R code execution, profiling with Rprof or profvis, measuring memory allocations, comparing function performance, or optimizing bottlenecks—e.g., "benchmark R function", "profvis profiling", "microbenchmark comparison", "performance analysis", "memory profiling".
---

# R Benchmarking Skill

## Purpose

Produce production-grade R benchmarking guidance and code with reproducibility and measurement rigor. We're building measurements we can trust—selecting the right tool (base timing vs microbench vs profiling) and explaining why this choice matters.

## References (Load on Demand)

- **[references/benchmarking-principles.md](references/benchmarking-principles.md)** - Load for methodology guidance, reproducibility checklist, or best practices questions
- **[references/base-timing-profiling.md](references/base-timing-profiling.md)** - Load when using system.time, proc.time, Rprof, or summaryRprof
- **[references/bench.md](references/bench.md)** - Load when using bench::mark or bench::press
- **[references/microbenchmark.md](references/microbenchmark.md)** - Load when using microbenchmark package
- **[references/rbenchmark.md](references/rbenchmark.md)** - Load when using rbenchmark::benchmark
- **[references/tictoc.md](references/tictoc.md)** - Load when using tic/toc nested timing
- **[references/profvis.md](references/profvis.md)** - Load when using profvis interactive profiling
- **[references/context7-slugs.md](references/context7-slugs.md)** - Load when querying Context7 for R package docs

## Decision Guide

| Goal                          | Tool                                          | Notes                                               |
| ----------------------------- | --------------------------------------------- | --------------------------------------------------- |
| Macro timing (end-to-end)     | `system.time()` or `proc.time()`              | Simple, no dependencies                             |
| Microbenchmarks + allocations | `bench::mark()`                               | Preferred; use `bench::press()` for parameter grids |
| Legacy/simple comparisons     | `microbenchmark` or `rbenchmark::benchmark()` | When bench not available                            |
| Profiling hotspots            | `Rprof()` + `summaryRprof()`                  | Use `profvis()` for interactive exploration         |
| Script instrumentation        | `tictoc::tic()`/`toc()`                       | Nested timing checkpoints                           |

## Workflow

**BEFORE PROCEEDING**, clarify your goal. This determines everything that follows.

1. **Announce your goal** (macro timing vs microbench vs profiling). Infer from context if not explicit; state your assumption explicitly.
2. **Immediately apply** reproducibility rules (inputs, seed, environment details, warmup). Measurement without reproducibility is noise.
3. Provide minimal, correct code snippet with the right tool and key parameters.
4. Explain how to interpret outputs (time, itr/sec, mem_alloc, gc/sec, by.self/by.total).
5. Call out pitfalls (I/O, GC, elapsed vs CPU, too-short sampling intervals).

## Output Contract

**You MUST provide all of the following without exception:**

- Tool choice and rationale—explain why this tool, why now
- R code snippet with key parameters configured correctly
- Notes on interpretation and pitfalls—what will mislead you

**For profiling:** include how to summarize and visualize results. Missing this wastes the profiling effort.

**For microbenchmarks:** include guidance on iterations, GC filtering, and result equivalence checks. Ignoring GC effects produces misleading rankings.

## Quality Standards

- **YOU MUST** use `bench::mark()` for microbenchmarks unless user explicitly requires legacy tools
- **NEVER** recommend single-run timings for comparisons—this produces garbage results without exception
- **ALWAYS** cite reference documentation directly—guessing APIs leads to silent failures

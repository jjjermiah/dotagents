# dot-agents (`.agents`)

Personal dotfiles repo for OpenCode agents, skills, and configuration. Uses
GNU Stow to symlink repo files into `$HOME` without copying.

## Repo summary
- `src/` holds stow packages (each maps into `$HOME`).
- `src/dot-agents/skills/` stows to `~/.agents/skills/`.
- `src/dot-config/opencode/` stows to `~/.config/opencode/`.
- `bin/` contains helper scripts; `pixi.toml` defines tasks.

## Stow model (how it works)
GNU Stow creates symlinks from package directories under `src/` into `$HOME`.
This repo uses Stow's `--dotfiles` mode, so `dot-` directories map to dot
directories (for example `dot-config` → `~/.config`, `dot-agents` → `~/.agents`).

Quick start:

```console
pixi run stow
```

This symlinks everything in `src/` into your home directory. To remove:

```console
pixi run unstow
```

Edit files in this repo; the symlinks update automatically.

```console
dot-agents
├── Agents
│   ├── ask (primary)
│   │     General-purpose agent for researching complex questions and executing multi-step tasks. Use this...
│   ├── docs (subagent)
│   │     Documentation writer - generates and updates markdown docs, READMEs, and guides. Can only write 
│   │   to...
│   ├── python-dev (subagent)
│   │     Python development specialist - production-grade Python code and tooling.
│   └── r-dev (subagent)
│         R development specialist - production-grade R code, packages, and data workflows.
└── Skills
    ├── code-reviewer
    │     Use when a feature is complete and needs validation, when reviewing code before merge, or when...
    ├── pixi
    │     Use when initializing projects, adding packages, managing environments, or as a conda 
    │   alternative—e.
    ├── pixi-expert
    │     Use when configuring features, solve groups, system requirements, monorepo workspaces, or...
    ├── pixi-tasks
    │     Use when building task dependency chains, configuring caching with inputs/outputs, creating...
    ├── python-production-libs
    │     Use when choosing libraries for HTTP clients, CLI frameworks, data validation, structured 
    │   logging,...
    ├── python-pybytesize
    │     Use when converting bytes to human-readable sizes, parsing size strings, or doing block-aligned...
    ├── python-testing
    │     Use when writing tests, reviewing test quality, designing fixtures, setting up pytest, or 
    │   debugging...
    ├── r-benchmarking
    │     Use when timing R code execution, profiling with Rprof or profvis, measuring memory allocations,...
    ├── r-error-handling
    │     Use when implementing error recovery, debugging conditions, or working with stop/warning/message—e.
    ├── r-expert
    │     Use when writing R functions, building packages, using tidyverse (dplyr, ggplot2, purrr), 
    │   creating...
    ├── r-rlang-programming
    │     Use when building data-masking APIs, wrapping dplyr/ggplot2/tidyr functions with {{ !! !!!...
    ├── r-testing
    │     Use when writing R tests, fixing failing tests, debugging errors, or reviewing coverage—e.
    ├── script-writer
    │     Use when developing bash automation, Python CLI tools, shell scripts, system administration...
    └── skill-creator
          Use when building new skills, updating existing skills, validating skill structure against...


Total: 4 agents, 14 skills
```

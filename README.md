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

<!-- AGENTS-SKILLS-TREE:START -->
```console
dot-agents
├── Agents
│   ├── ask (primary)
│   │   General-purpose agent for researching complex questions and
│   │   executing multi-step tasks. Use this...
│   ├── azure-devops (subagent)
│   │   Azure DevOps (ADO) specialist. ALWAYS USE WHEN INTERACTING
│   │   WITH ADO Repos/Pull Requests/Pipelines...
│   ├── docs (subagent)
│   │   Documentation writer - generates and updates markdown docs,
│   │   READMEs, and guides. Can only write to...
│   ├── python-dev (subagent)
│   │   Python development specialist - production-grade Python code
│   │   and tooling.
│   ├── r-dev (subagent)
│   │   R development specialist - production-grade R code,
│   │   packages, and data workflows.
│   ├── rovo (subagent)
│   │   USE WHEN THE USER ASKS FOR ANYTHING RELATED TO JIRA OR
│   │   CONFLUENCE.
└── Skills
    ├── azuredevops-pipelines-logging
    │   Use when writing or debugging `##vso[.
    ├── azuredevops-pipelines-template
    │   Use when designing or debugging Azure Pipelines YAML
    │   templates, splitting PR validation from...
    ├── code-reviewer
    │   Use when a feature is complete and needs validation, when
    │   reviewing code before merge, or when...
    ├── pixi-expert
    │   Comprehensive pixi package manager skill for all pixi
    │   operations from beginner to advanced. Use for...
    ├── pixi-tasks
    │   Use when building task dependency chains, configuring
    │   caching with inputs/outputs, creating...
    ├── python-code-quality
    │   Use when configuring Ruff rules, setting up ty type
    │   checking, writing pyproject.
    ├── python-polars
    │   Use when writing Python data processing code, data
    │   transformation pipelines, ETL workflows, or...
    ├── python-production-libs
    │   Use when choosing libraries for HTTP clients, CLI
    │   frameworks, data validation, structured logging,...
    ├── python-pybytesize
    │   Use for pybytesize/ByteSize tasks: parsing size strings,
    │   converting bytes to metric/binary units,...
    ├── python-testing
    │   Use when writing tests, reviewing test quality, designing
    │   fixtures, setting up pytest, or debugging...
    ├── r-benchmarking
    │   Use when timing R code execution, profiling with Rprof or
    │   profvis, measuring memory allocations,...
    ├── r-documentation
    │   R package documentation with roxygen2 and Rd files,
    │   including mathematical notation, selective Rd...
    ├── r-error-handling
    │   Use when implementing error recovery, debugging conditions,
    │   or working with stop/warning/message—e.
    ├── r-expert
    │   Use when writing R functions, building packages, using
    │   tidyverse (dplyr, ggplot2, purrr), creating...
    ├── r-rlang-programming
    │   Use when building data-masking APIs, wrapping
    │   dplyr/ggplot2/tidyr functions with {{ !! !!!...
    ├── r-testing
    │   Use when writing R tests, fixing failing tests, debugging
    │   errors, or reviewing coverage—e.
    ├── script-writer
    │   Use when developing bash automation, Python CLI tools, shell
    │   scripts, system administration...
    ├── sdk-module-investigation
    │   Use when asked to "investigate module", "SDK", "client
    │   class", or when docs are missing/weak and...
    └── skill-creator
        Use when building new skills, updating existing skills,
        validating skill structure against...

Total: 6 agents, 19 skills
```
<!-- AGENTS-SKILLS-TREE:END -->

---
name: azuredevops-pipelines-logging
description: Azure DevOps Pipelines logging-command guidance for reliable script-to-agent signaling, variable passing, and log UX. Use when writing or debugging `##vso[...]` and `##[...]` commands in YAML/Bash/PowerShell pipelines, troubleshooting output variable scope, handling secrets and masking behavior, or publishing summaries/artifacts from scripts. Pair with `azuredevops-pipelines-template` when template architecture and logging semantics are both in scope.
---

# Azure DevOps Logging

## Purpose

Produce correct, debuggable Azure DevOps logging commands from scripts without
silent parser failures. Ensure variable flow, task outcomes, and log readability
work predictably across jobs and stages.

## Scope Boundary

- Own script-to-agent signaling, task-state updates, and log formatting.
- Own command correctness, escaping, and variable handoff syntax.
- Do not own pipeline topology, trigger strategy, or template API design.

## Pairing Contract with `azuredevops-pipelines-template`

Use both skills together for full pipeline quality:

- `azuredevops-pipelines-template` decides compile-time structure, typed
  template contracts, and PR-versus-main topology.
- `azuredevops-pipelines-logging` implements script-level state signaling:
  `task.setvariable`, `task.logissue`, `task.complete`, summaries, and tags.
- Keep boundary explicit: template skill chooses *where* data should flow;
  logging skill chooses *how* command lines implement that flow safely.

## Core Rules

- Treat Azure DevOps script output as two distinct families:
  - `log-formatting` commands: `##[...]` lines that only change how logs look.
  - `agent-action` commands: `##vso[...]` lines that change pipeline state.
- When deciding a command, classify intent first:
  - "I want logs easier to read" -> use `##[...]` only.
  - "I want to change variables/status/build metadata/artifacts" -> use
    `##vso[...]`.

- Use exact command formats only:
  - `##vso[area.action property=value;...]message`
  - `##[group|warning|error|section|debug|command|endgroup]message`
- Use absolute paths for file-based commands (`uploadsummary`, `uploadfile`,
  artifact/build upload commands).
- Do not emit logging commands while Bash xtrace is enabled (`set -x`). Disable
  around the command, then restore.
- Never print secrets directly. Use environment variables and masking commands.
  Assume secret substrings are not masked.
- For values that may contain `%`, `\n`, `\r`, `;`, or `]`, escape first.

## Workflow

1. Classify goal: log formatting, task control, variable exchange,
   artifact/summary publishing, or metadata update.
2. Choose minimal command and scope (same step, same job, future job, stage).
3. Build command string with required properties only.
4. Escape payload if dynamic/user-controlled.
5. Emit via `echo` (Bash) or `Write-Host` (PowerShell).
6. Verify in run logs/timeline: parser accepted command, expected downstream
   behavior appears.

## High-Value Patterns

### Safe Escaping for `task.setvariable`

Use this when value may include newline, carriage return, or percent.

```bash
escape_azdo_value() {
  local data="$1"
  data="${data//'%'/'%AZP25'}"
  data="${data//$'\n'/'%0A'}"
  data="${data//$'\r'/'%0D'}"
  printf '%s' "$data"
}

echo "##vso[task.setvariable variable=myVar;isOutput=true]$(escape_azdo_value "$VALUE")"
```

### Temporary xtrace Disable

```bash
{ set +x; } 2>/dev/null
echo "##vso[task.setvariable variable=buildFlavor;]release"
set -x
```

### Scope-Correct Variable Usage

- Same job, no `isOutput`: read as `$(myVar)` in later steps.
- Same job, `isOutput=true`: set task name and read as `$(TaskName.myVar)`.
- Future job: map through `dependencies.<job>.outputs['<task>.<var>']`.
- Future stage: map through
  `stageDependencies.<stage>.<job>.outputs['<task>.<var>']`.
- Newly set variables are never available in the same step.

### Failure Semantics

- Use `task.logissue type=error` to surface actionable message.
- Use `task.complete result=Failed;` for explicit task status when needed.
- Use non-zero exit when script should fail immediately.
- Avoid contradictory signaling (for example, command says succeeded but script
  later exits non-zero).

## Command Selection Quick Guide

### A) Log-Formatting Commands (`##[...]`)

Use these for human-readable logs only. They do not modify pipeline variables,
build number, artifacts, or task result.

- `##[group]` / `##[endgroup]`: collapsible log block.
- `##[section]`: visual section marker.
- `##[warning]` / `##[error]`: highlighted log lines.
- `##[debug]`: diagnostics line.
- `##[command]`: show the command being run.

### B) Agent-Action Commands (`##vso[...]`)

Use these when you need side effects in pipeline state.

- `task.setvariable` / `task.setsecret`: variable and secret handling.
- `task.logissue`: timeline warning/error metadata.
- `task.complete`: explicit task result.
- `task.setprogress`: progress indicator updates.
- `task.uploadsummary` / `task.uploadfile`: publish summary or files.
- `task.prependpath`: update PATH for downstream steps.
- `build.updatebuildnumber` / `build.addbuildtag`: build metadata updates.

### Fast Decision Rule

- If removing the command would only change log appearance -> `##[...]`.
- If removing the command would change pipeline behavior/data -> `##vso[...]`.

## Output Contract

When this skill is used, respond with:

1. Chosen logging command(s) and why.
2. Copy/paste-ready Bash or PowerShell snippet.
3. Correct variable reference syntax for same job/future job/stage (if relevant).
4. Verification checklist (where to confirm success in logs/UI).
5. Explicit note when template-level changes should be delegated to
   `azuredevops-pipelines-template`.

## References (Load on Demand)

- **[references/log-formatting-commands.md](references/log-formatting-commands.md)**
  - Load when the goal is readable/collapsible/highlighted logs only.
- **[references/agent-action-commands.md](references/agent-action-commands.md)**
  - Load when commands need to change pipeline state (variables, status,
    artifacts, build/release metadata).
- **[references/community-gotchas.md](references/community-gotchas.md)** - Load
  when troubleshooting parser failures, escaping edge cases, summary quirks, or
  inconsistent behavior seen in real pipelines.

# Azure Repos PR Validation

## Critical Rule

For Azure Repos Git, do not depend on YAML `pr:` triggers. Use Branch Policies
Build Validation on target branches.

## Recommended Setup

1. Create a dedicated PR validation pipeline YAML:

```yaml
trigger: none
pr: none

extends:
  template: templates/ci-core.yml
  parameters:
    runIntegrationTests: false
    dependencyMode: fast
```

1. In Repos -> Branches -> target branch policy:
   - Add Build Validation.
   - Select the PR validation pipeline.
   - Configure policy behavior (required, queue settings, etc).

2. Keep post-merge main pipeline separate:

```yaml
trigger:
  branches:
    include:
      - main
pr: none

extends:
  template: templates/ci-core.yml
  parameters:
    runIntegrationTests: true
    dependencyMode: locked
```

## Why This Split Works

- PR path remains fast and policy-driven.
- Main path runs the full suite, including heavy integration checks.
- Both paths share one implementation template to avoid drift.

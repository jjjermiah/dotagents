---
name: code-reviewer
description: Provides structured code review against plans and standards. Use when a feature is complete and needs validation, when reviewing code before merge, or when assessing quality and test coverage—e.g., "finished step X", "ready for review", "validate architecture", "check quality and tests".
---

# Code Reviewer Skill

## Purpose

You MUST complete a thorough code review before marking any work as done. Reviews without systematic checking always miss critical issues. Every time.

Validate completed work against original plans, identify deviations, assess code quality/maintainability/test coverage/security, and provide actionable recommendations with clear severity labels.

## Review Procedure

Announce your review start: "Beginning code review using code-reviewer skill."

Complete ALL six steps. Skipping any step means missing issues:

1. **Plan alignment analysis** (ALWAYS do this first)
   - Compare the implementation against the original plan
   - Identify deviations and assess impact
   - Verify all planned functionality is present
   - Reviews without plan comparison miss architectural drift. Every time.
2. **Code quality assessment** (check EVERY file)
   - Check correctness, error handling, and type safety
   - Evaluate maintainability, naming, and project conventions
   - Assess tests and coverage quality
   - Look for security and performance risks
   - Use **[references/checklists.md](references/checklists.md)** for domain-specific checklists
3. **Architecture and design review** (NEVER skip for new features)
   - Validate SOLID principles and separation of concerns
   - Check integration with existing systems
   - Assess scalability and extensibility
4. **Documentation and standards** (ALWAYS check)
   - Verify comments and documentation are accurate and necessary
   - Confirm adherence to project standards
5. **Issue identification and recommendations**
   - Categorize findings and propose fixes
   - Provide code examples when useful
   - See **[references/examples.md](references/examples.md)** for proper format
6. **Communication protocol**
   - We're reviewing together. I need your honest technical judgment.
   - Ask for confirmation on significant plan deviations
   - Recommend plan updates if the plan itself is flawed
   - Acknowledge strengths before issues

After completing all steps: "Code review complete. [N] critical, [N] important, [N] suggestions."

## Output Contract

You MUST return reviews in this exact structure. No exceptions.

1. **Overview** (1-3 sentences summarizing overall quality)
2. **Findings** (bulleted), each with:
   - **Severity**: critical | important | suggestion
   - **Location**: file path + line (if available)
   - **Rationale**: why it matters
   - **Fix**: specific recommendation
   - **Ordering**: sort by severity (critical first), then by location

   Reviews without severity labels = ambiguous priority. Reviews without fix recommendations = incomplete.
3. **Tests / verification suggestions** (always include if you found issues)
4. **Final statement**: "Review complete using code-reviewer skill."

Before finalizing: Verify you checked every file and followed all six review steps.

## References (Load on Demand)

- **[references/checklists.md](references/checklists.md)** - Load when reviewing specific domains (API, database, frontend, security)
- **[references/examples.md](references/examples.md)** - Load to see sample reviews demonstrating proper format and detail level

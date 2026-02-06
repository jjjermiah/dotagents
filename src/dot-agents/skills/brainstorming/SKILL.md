---
name: brainstorming
description: |
  Structured ideation and creative problem-solving across any domain. Use when stuck on a problem, generating ideas for a project, evaluating alternatives, or escaping convergent thinking—e.g., "brainstorm approaches", "we keep coming up with the same ideas", "need fresh angles", "generate 20 ideas for...", "divergent thinking".
---

# Brainstorming

## Purpose

Guide users through structured ideation and creative problem-solving. Detects starting state (stuck, seed, or open) and applies appropriate techniques: escaping convergent thinking traps, expanding half-formed ideas, or systematic generation and selection.

## Entry: Where Are You Starting?

BEFORE PROCEEDING, require the user to explicitly choose their starting point:

| Starting Point | Description                                          | Next Step                                         |
|----------------|------------------------------------------------------|---------------------------------------------------|
| **Stuck**      | Same ideas keep surfacing. "We've tried everything." | → [Escape Mode](#escape-mode)                     |
| **Seed**       | Have an idea but need to expand it                   | → [Expand Mode](#expand-mode)                     |
| **Open**       | Need to generate many options from scratch           | → [Diverge-Converge Mode](#diverge-converge-mode) |

YOU MUST get explicit confirmation: "Which starting point describes you: Stuck, Seed, or Open?" No proceeding until selected.

## Session Tracking

Throughout any session, track progress mentally and surface when relevant:

- **Current mode**: Which mode are we in?
- **Ideas captured**: How many distinct ideas so far?
- **Convergence status**: Still diverging, or ready to converge?
- **Selection status**: Has a selection been made?

Surface progress when: changing phases, user seems lost, or before generating session summary.

## Escape Mode: Breaking Convergent Thinking

When ideas cluster around the same approaches.

### Step 1: Detect Convergence Blindness

YOU MUST check if we're stuck in one of these states (see [references/convergence-states.md]):

- **B1 First-Attractors**: First ideas feel "right" immediately
- **B2 Function-Lock**: Discussion assumes a solution type ("We need an app...")
- **B3 Axis-Collapse**: Ideas differ cosmetically but share structure
- **B4 Domain-Prison**: All ideas come from same reference class

Ask diagnostic questions from the reference. If any state matches, IMMEDIATELY apply the corresponding intervention. Never skip this step—convergence blindness kills creativity every time.

### Step 2: Function Extraction

Separate WHAT from HOW:
1. List 3-5 core functions the solution must accomplish (independent of form)
2. Reframe: "We need [FORM]" becomes "We need to [FUNCTION]"

### Step 3: Axis Mapping

Map the default solution on four axes:
- **Who**: Who does/uses this? Try 3 unlikely actors
- **When**: What timeframe? Try different cadence
- **Scale**: What size? Try 10x bigger or smaller
- **Method**: What approach? Try completely different mechanism

### Step 4: Generate Under Constraints

Apply one unusual constraint (see [references/constraint-prompts.md]):
- Random actor from different domain
- Resource limitation (1/10th budget, no obvious tech)
- Inversion (what if failure was the goal?)

Generate 3-5 ideas under this constraint. The constraint forces exploration of non-adjacent space.

**Exit Criteria:** Escape Mode is complete when you have 5+ genuinely distinct approaches (not variations). If still clustering, return to Step 1. If ready to select, transition to Diverge-Converge Phase 3 (Converge).

## Expand Mode: Growing Seeds

When you have an initial idea that needs development.

### Step 1: Identify Seed Type

Determine which state describes the seed (see [references/seed-states.md]):

- **S1 Adjacent-Ready**: Concrete, clear next step needed
- **S2 Collision-Hungry**: Feels incomplete, needs "something else"
- **S3 Half-Baked Hunch**: Fuzzy but feels important
- **S4 Error-Rich**: Tried and failed, but learned something
- **S5 Exaptation**: Could work in completely different context

### Step 2: Apply Expansion Technique

| Seed Type | Technique |
|-----------|-----------|
| Adjacent-Ready | Map what's one step away; what becomes possible |
| Collision-Hungry | Force collisions: domains, constraints, past work |
| Half-Baked Hunch | Articulate clearly, name the gap, keep it alive |
| Error-Rich | Mine the failure: what did error reveal? |
| Exaptation | Transplant: list 5 different contexts, try seed in each |

### Step 3: Stress Test

Find where the seed breaks:
- What's the worst-case application?
- What assumption, if wrong, kills this?
- What's the dumbest possible version?

**Exit Criteria:** Expand Mode is complete when the seed has been stress-tested and either strengthened or revealed as flawed. If strengthened, move to Refinement Mode or implementation. If flawed, return to Escape Mode or try a different seed.

## Diverge-Converge Mode: Systematic Generation

When you need to generate and select from many options.

### Phase 1: Diverge

Generate 20-50 ideas without judgment:
- Suspend criticism entirely
- Aim for quantity AND variety
- Use prompts: "What if unlimited resources?", "What would competitor do?", "What if we did the opposite?"

### Phase 2: Cluster

Organize into 4-8 distinct themes:
- Group by mechanism, user, timeline, effort, or risk
- Aim for distinct clusters (not overlapping)
- Fewer than 4 = not enough variety, more than 8 = too fragmented

### Phase 3: Converge

Select top 3-5 ideas:
1. Define explicit criteria (impact, feasibility, cost, alignment)
2. Score each idea (1-10 or Low/Med/High)
3. Rank by score
4. Document tradeoffs: why chosen, what deprioritized

YOU MUST get explicit selection: "Which ideas are we moving forward with?" Confirm choices before proceeding.

**Exit Criteria:** Diverge-Converge is complete when selection is confirmed with explicit rationale. If selection reveals need for more options, return to Phase 1. If ready to detail the selection, transition to Refinement Mode.

## Anti-Patterns: NEVER Use These

Throughout all modes, we guard against these failure patterns:

| Pattern                  | Problem                                | Fix                                                     |
|--------------------------|----------------------------------------|---------------------------------------------------------|
| **Quantity Delusion**    | 50 variations of same 3 approaches     | Map on axes, require one idea per quadrant              |
| **Premature Evaluation** | "That won't work..." during generation | Strict phase separation: generate first, evaluate after |
| **Expert Anchor**        | First expert idea dominates            | Anonymous generation first, or expert speaks last       |
| **Inversion Trap**       | "Do the opposite" (still same axis)    | Find orthogonal axis, not negative of same              |
| **Novelty Chase**        | Weird but doesn't solve problem        | Return to function: does this serve required function?  |

**Premature evaluation without generation first = guaranteed mediocre results. Every time.**

## Group Dynamics

When facilitating with multiple people:

- **Generate before discussing**: Have each person generate ideas independently before sharing. Prevents anchoring.
- **Expert speaks last**: Domain experts share after others have contributed. Their ideas carry implicit weight.
- **Name convergence when you see it**: If ideas cluster, call it out: "I notice we're all in the same space. Let's try [axis rotation / constraint / domain import]."
- **Protect half-formed ideas**: In groups, vague hunches get killed early. Explicitly invite "things that feel important but aren't clear yet."

## Refinement Mode: Validating and Detailing

**When to enter:** After selection is made in any other mode and you're ready to validate and detail the chosen direction.

When you have a direction and need to refine it through dialogue.

### Understanding Phase

- Check our project context first (files, docs)
- Ask ONE question at a time (prefer multiple choice)
- Focus: purpose, constraints, success criteria

### Exploration Phase

- Present 2-3 approaches with trade-offs
- Lead with our recommendation and reasoning
- YOU MUST get explicit selection: "Which approach should we pursue?" before proceeding

### Design Phase

- Present design in 200-300 word sections
- Validate after each section before proceeding
- Cover: architecture, components, data flow, error handling, testing
- Be ready to return to previous sections

### Output

Write validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`

## Session Summary Output

At the end of ANY brainstorming session, YOU MUST generate a summary:

```markdown
## Brainstorming Session Summary

**Date:** [YYYY-MM-DD]
**Mode:** [Escape | Expand | Diverge-Converge]
**Problem/Seed:** [brief description of what we brainstormed]

### Ideas Generated
[numbered list of distinct ideas, or clusters with ideas within]

### Selection Made
[selected ideas with brief rationale, or "None yet - still diverging"]

### Key Insights
[what we learned about the problem space]

### Next Steps
[follow-up actions, experiments to run, or questions to answer]
```

Generate this summary when: user indicates session is done, selection has been confirmed, or conversation naturally concludes.

## References

Load references as needed for specific techniques:

- **[references/convergence-states.md]**: Load when user is stuck—diagnose B1-B4 blind spots and apply interventions
- **[references/seed-states.md]**: Load when expanding a seed idea—identify S1-S5 state and apply expansion technique
- **[references/constraint-prompts.md]**: Load when needing random constraints for entropy injection (Escape Mode Step 4)
- **[references/domain-patterns.md]**: Load when running Diverge-Converge Mode for specific domain templates (product, research, strategy, etc.)

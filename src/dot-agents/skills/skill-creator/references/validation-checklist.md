# Skill Validation Checklist

## Metadata

- [ ] `name` and `description` in YAML frontmatter
- [ ] `name` uses kebab-case
- [ ] Description comprehensive (see skill-description-guide.md)
- [ ] Description explains WHAT it does
- [ ] Description includes "Use when" contexts
- [ ] Description includes examples after em-dash
- [ ] All trigger info in description (not body)
- [ ] Only `name`, `description`, optional `license` in frontmatter

## Structure

- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] SKILL.md has markdown body
- [ ] No README.md, INSTALLATION.md, CHANGELOG.md
- [ ] Skill name matches directory name
- [ ] Scripts in `scripts/` (if any)
- [ ] References in `references/` (if any)
- [ ] Assets in `assets/` (if any)

## Content

- [ ] Instructions concise and actionable
- [ ] Persuasion principles applied if skill enforces discipline or guides decisions
- [ ] Skill type-appropriate principle combination (see persuasion-principles.md table)
- [ ] No illegitimate tactics (fear, shame, guilt, false urgency, fabricated social proof)
- [ ] Ethical test passed: serves user's genuine interests
- [ ] Bright-line rules use imperative language ("YOU MUST", "Never", "Always")
- [ ] Commitment mechanisms where applicable (announcements, tracking, explicit choices)
- [ ] Implementation intentions: "When X, do Y" format for triggers
- [ ] Alternatives or tradeoffs noted where applicable
- [ ] Uncertainty or limitations stated when relevant
- [ ] SKILL.md under 500 lines
- [ ] Uses imperative/infinitive form
- [ ] Code examples have language tags
- [ ] File paths clear and correct
- [ ] Core workflow in SKILL.md
- [ ] Detailed content in references
- [ ] References linked from SKILL.md with usage guidance
- [ ] All references one level deep from SKILL.md
- [ ] Reference files >100 lines have table of contents
- [ ] No duplicate info between SKILL.md and references
- [ ] Scripts tested and working
- [ ] Scripts necessary (not just repeating what agent can write)
- [ ] Script usage documented in SKILL.md
- [ ] Assets used in output (not documentation)

## Integration

- [ ] Links use correct paths
- [ ] No broken links or missing files
- [ ] Follows repo conventions

## Validation

**Automated**:
```bash
python scripts/package_skill.py path/to/skill-folder
```
Checks YAML, required fields, naming, structure.

**Manual**:
1. Read description only - clear when to use?
2. Read SKILL.md - instructions complete?
3. Follow workflow start to finish - any gaps?
4. Try 3-5 example requests - skill provides guidance?
5. Check references - split logical? Clear when to read?

**Peer Review**:
1. "Read description - what does this do?"
2. "When would you use this?"
3. "Can you complete [task] with SKILL.md?"
4. "What's unclear?"

## Common Issues

- Description too narrow → Add contexts, variations, examples
- Description too broad → Add specificity (domain, files, prerequisites)
- "Triggers:" keyword list → Use "Use when" with contexts instead
- "Use when" in body not frontmatter → Move to description
- SKILL.md >500 lines → Split to references with links
- References not linked → Add explicit guidance in SKILL.md
- Redundant content → Single source of truth
- Untested scripts → Test before packaging
- Auxiliary docs → Delete, consolidate to SKILL.md

## Pre-Package

- [ ] All items above checked
- [ ] SKILL.md complete and tested
- [ ] Referenced files exist
- [ ] Scripts tested
- [ ] No extraneous files
- [ ] Description comprehensive
- [ ] Under 500 lines or split properly

Then:
```bash
python scripts/package_skill.py path/to/skill-folder [output-dir]
```

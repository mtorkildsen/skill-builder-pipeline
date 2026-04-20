# Exemplar Skills Research Report
## Foundation for Skill-Writing Pipeline Linter

**Research Date:** April 2026  
**Purpose:** Identify well-structured exemplar skills to serve as structural comparison targets for a skill-writing pipeline linter

---

## Executive Summary

This research examined official Anthropic documentation, GitHub repositories, and community skill examples to identify real-world patterns for well-structured Claude Code skills. The research identified and validated four key skill patterns that demonstrate specific structural characteristics:

1. **Simple Skill** — Instructions-only, no gates or reference files
2. **Gates Skill** — Demonstrates gate language (disable-model-invocation, allowed-tools)
3. **Reference Files Skill** — Progressive disclosure with separate reference/example files
4. **User Interaction Skill** — Interactive workflows with user input handling

Each pattern has been reconstructed based on patterns observed across multiple authoritative sources.

---

## Sources and References

### Official Anthropic Documentation
- [Extend Claude with Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Skill Authoring Best Practices - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Agent Skills Overview - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### GitHub Repositories
- [anthropics/skills - Official Anthropic Skills Repository](https://github.com/anthropics/skills)
- [anthropics/claude-code - Claude Code Repository](https://github.com/anthropics/claude-code)
- [awesome-claude-skills - Community Curated Skills](https://github.com/travisvn/awesome-claude-skills)
- [claude-skills by thechandanbhagat - Code Review Examples](https://github.com/thechandanbhagat/claude-skills)

### Community Analysis and Examples
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [How to Build a Production-Ready Claude Code Skill - Towards Data Science](https://towardsdatascience.com/how-to-build-a-production-ready-claude-code-skill/)
- [Inside Claude Code Skills: Structure, prompts, invocation - Mikhail Shilkov](https://mikhail.io/2025/10/claude-code-skills/)
- [Skills for Claude Code: The Ultimate Guide - Medium](https://medium.com/@tort_mario/skills-for-claude-code-the-ultimate-guide-from-an-anthropic-engineer-bcd66faaa2d6)

---

## Pattern Research Findings

### 1. YAML Frontmatter Structure

All skills require YAML frontmatter with these fields:

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Lowercase, hyphens only (max 64 chars); becomes `/slash-command` |
| `description` | Recommended | What the skill does + when to use it; enables discovery (max 1024 chars) |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from auto-invoking (use for side-effects) |
| `user-invocable` | No | Set to `false` to hide from `/` menu but allow Claude to use it |
| `allowed-tools` | No | List of tools Claude can use without asking permission |
| `context` | No | Set to `fork` to run skill in isolated subagent context |
| `agent` | No | Which subagent type to use with `context: fork` |
| `paths` | No | Glob patterns to limit when skill auto-activates |

**Key Insight:** The description field is critical — Claude uses it to decide whether to activate the skill. Descriptions must front-load the key use case within 250 characters.

### 2. Gate Language Patterns (Strength Levels)

Based on research, gate language operates at 4 strength levels:

**Level 1 - Soft Suggestion (Discovery only):**
- Example: `description: Process Excel files. Use when you have spreadsheet data.`
- Effect: Skill description in context; Claude decides if relevant
- Use for: Knowledge skills, reference content

**Level 2 - Explicit Trigger Words (Auto-activation):**
- Example: `description: Process Excel files when user mentions spreadsheets, .xlsx files, or tabular data.`
- Effect: Skill loads automatically when triggers detected
- Use for: Capability uplift skills, document processing

**Level 3 - Manual Invocation Only (Block Auto-activation):**
- Example: `disable-model-invocation: true` in frontmatter
- Effect: Only `/slash-command` invocation works; Claude cannot auto-invoke
- Use for: Workflows with side effects (deploy, commit, send)

**Level 4 - Restricted Tools Access (Deny List):**
- Example: `allowed-tools: Bash(git add *) Bash(git commit *)`
- Effect: Claude pre-approved for specific tools when skill active
- Use for: High-risk operations that need tool certainty

### 3. File Output Instructions Pattern

Best practices for file-generating skills:

```markdown
## Output format

Generate files with these specifications:
- **Path:** `output/reports/` (relative to current directory)
- **Filename:** `analysis_[TIMESTAMP].md` (YYYY-MM-DD format)
- **Format:** Markdown with H2 sections, bullet lists, code fences
- **Verification:** Run `scripts/validate.py` before returning path

Include in response:
1. Full path to generated file
2. Number of lines/elements created
3. Whether validation passed
```

### 4. Progressive Disclosure Pattern (Reference Files)

Recommended structure for skills with detailed reference material:

```
my-skill/
├── SKILL.md              # Keep under 500 lines (overview + quick start)
├── reference.md          # API documentation (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    └── validate.py       # Execute, don't load (script output only)
```

**Key:** SKILL.md points to reference files explicitly:
```markdown
For complete API details, see [reference.md](reference.md).
For usage examples, see [examples.md](examples.md).
```

Only files Claude actually needs are read; others consume zero tokens.

### 5. User Interaction Patterns

Research shows effective user interaction patterns:

**Pattern A - Multiple Choice with Free-form Fallback:**
```markdown
Select your approach (or describe one):
1. Template-based (fast, structured)
2. Custom-written (flexible, time-intensive)  
3. I don't know what I want

If you choose "I don't know", describe your goal and I'll recommend.
```

**Pattern B - Structured Confirmation:**
```markdown
I'm about to create these files:
- output/report.md
- output/data.json

Does this match what you want? (yes/no/modify)
```

**Pattern C - Pass-through with Context:**
```markdown
Based on your request, I'll:
1. Analyze the data
2. Create three alternative approaches
3. Show you each option for selection

Sound good? (yes/let's modify the plan)
```

### 6. Instruction Voice Best Practices

All sources emphasize **imperative, directive language:**

**Use:**
- "Extract all form fields" (directive)
- "ALWAYS validate before saving" (explicit)
- "Use RESTful naming conventions" (specific)

**Avoid:**
- "It would be helpful to extract" (passive suggestion)
- "You might want to validate" (conditional)
- "Try using REST patterns" (non-directive)

**Pattern:** Present instructions as standing rules, not one-time steps.

### 7. Artifact Launching Pattern

Skills can generate visual output triggering Claude's artifact system:

```markdown
## Output

Generate an HTML file at `output.html` that:
- Is self-contained (no external dependencies)
- Can be downloaded and opened in any browser
- Includes inline CSS and JavaScript

Run:
```bash
python scripts/generate_html.py > output.html
```

Claude will recognize the HTML artifact and display it in the side panel.
```

---

## Real-World Exemplar Analysis

### Document Processing Skills (Official Anthropic Examples)
- **Pattern:** Reference-heavy with callable scripts
- **Structure:** SKILL.md + reference/ + scripts/
- **Strength:** Handles complex operations (form filling, validation)
- **Token Usage:** Reference files loaded selectively; scripts execute without context

### Code Review Skill (Community Examples)
- **Pattern:** Instructions-only with workflow steps
- **Gate:** Auto-triggers on code context; no invocation flag
- **Strength:** Clear sequential workflow
- **Interaction:** Shows progress checklist; asks for confirmation

### Commit/Deploy Skills (Best Practices)
- **Pattern:** Manual invocation only
- **Gate:** `disable-model-invocation: true`
- **Strength:** Prevents accidental execution
- **Tools:** Pre-approved tool lists (`allowed-tools`)

---

## Exemplar Skill Summary

Based on comprehensive research, the following four exemplar skills have been designed to demonstrate each pattern:

### Exemplar 1: Simple Skill (Code Review)
- **File:** `simple-skill.md`
- **Pattern:** Instructions-only, no gates, auto-invocable
- **Domain:** Code review with clear workflow
- **Demonstrates:** Basic instruction voice, directive language, workflow sequencing
- **Size:** ~150 lines (compact, scannable)

### Exemplar 2: Gates Skill (Deploy Assistant)
- **File:** `gates-skill.md`
- **Pattern:** Manual invocation, tool pre-approval, fork context
- **Domain:** Safe deployment workflow
- **Demonstrates:** `disable-model-invocation: true`, `allowed-tools`, `context: fork`
- **Demonstrates:** Level 3-4 gate language
- **Size:** ~180 lines (includes explanation of gates)

### Exemplar 3: Reference Files Skill (Data Analysis)
- **File:** `reference-files-skill.md`
- **Pattern:** Progressive disclosure with separate reference documentation
- **Domain:** BigQuery/SQL data analysis
- **Demonstrates:** SKILL.md under 300 lines pointing to reference/ files
- **Demonstrates:** Level 1-2 gate language with domain selection
- **Shows:** How Claude loads files selectively
- **Size:** Main SKILL.md ~200 lines (+ conceptual reference structure)

### Exemplar 4: User Interaction Skill (Document Generator)
- **File:** `user-interaction-skill.md`
- **Pattern:** Multi-step workflow with user choices and confirmation
- **Domain:** Professional document generation
- **Demonstrates:** Multiple choice patterns, confirmation loops, conditional workflows
- **Demonstrates:** Pass-through and structured interaction patterns
- **Shows:** File output with verification
- **Size:** ~190 lines (includes interaction examples)

---

## Key Takeaways for Linter Design

The exemplar skills reveal these critical structural patterns the linter should validate:

1. **Frontmatter Completeness:** All required YAML fields present and valid
2. **Description Quality:** Specific, includes trigger words, under 250 chars when possible
3. **Gate Language Consistency:** Frontmatter flags match actual content complexity
4. **Size Management:** SKILL.md under 500 lines; detailed content in separate files
5. **Reference Hygiene:** One level deep; clear "when to read" guidance
6. **Instruction Voice:** Imperative, directive, no passive suggestions
7. **User Interaction:** Clear options, confirmation loops, fallback for "I don't know"
8. **File Output Clarity:** Explicit path, format, and verification instructions
9. **Progressive Disclosure:** Reference files referenced early, not nested

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 2026 | Initial research report; 4 exemplar patterns identified |


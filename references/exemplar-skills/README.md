# Exemplar Skills for Skill-Writing Pipeline Linter

This directory contains well-structured exemplar skills that serve as structural comparison targets for a skill-writing pipeline linter. Each exemplar demonstrates specific patterns and best practices identified through comprehensive research of Anthropic's official documentation and community examples.

## Files

### `exemplar-research-report.md` (280 lines)
Comprehensive research findings including:
- Official Anthropic documentation sources
- GitHub repositories analyzed
- Community analysis and examples
- Pattern research findings (YAML frontmatter, gate language levels, file output patterns, etc.)
- Key takeaways for linter design
- Detailed reference section with all sources

**Use this file to:** Understand the research foundation, reference official sources, review the four gate language strength levels, understand progressive disclosure patterns.

---

## Exemplar Skills

### 1. Simple Skill — `simple-skill.md` (87 lines)

**Pattern:** Instructions-only, no gates, auto-invocable  
**Domain:** Code review  
**Demonstrates:**
- Clean YAML frontmatter with minimal fields
- Clear description with trigger words ("analyze code quality", "get architectural feedback")
- Directive, imperative instruction voice
- Structured workflow (5 clear sequential steps)
- Focus areas and output format guidance
- No reference files or complexity gates

**Use for linting:** Basic structure validation, description quality, instruction voice analysis

**Linter checks:**
- Frontmatter present and valid
- Description includes action verb and context
- SKILL.md uses imperative language ("Review", "Check", not "Consider")
- Under 200 lines ✓
- No unnecessary gates

---

### 2. Gates Skill — `gates-skill.md` (158 lines)

**Pattern:** Manual invocation only, tool pre-approval, fork context  
**Domain:** Production deployment  
**Demonstrates:**
- Level 3 gate language: `disable-model-invocation: true` (prevent auto-invoke)
- Level 4 gate language: `allowed-tools` with specific bash patterns
- Context fork: `context: fork` with `agent: Plan`
- WARNING block and safety constraints (MANDATORY rules)
- Structured step-by-step workflow with checkpoints
- Mandatory safety enforcement language
- Rollback and monitoring procedures
- Clear "when to deploy / when NOT to deploy" boundaries

**Use for linting:** Gate language validation, tool specification, context fork patterns, safety constraints

**Linter checks:**
- `disable-model-invocation: true` present for side-effect operations ✓
- `allowed-tools` list is specific and bounded ✓
- Mandatory rules use imperative caps (ALWAYS, NEVER)
- Step markers with checkpoint validation
- Non-recoverable operation warnings included
- Safety constraints are explicit and non-negotiable

---

### 3. Reference Files Skill — `reference-files-skill.md` (147 lines)

**Pattern:** Progressive disclosure with separate reference documentation  
**Domain:** SQL data analysis (BigQuery, Snowflake, PostgreSQL)  
**Demonstrates:**
- Level 1-2 gate language: Description with specific trigger words
- Quick reference patterns within SKILL.md
- Clear file references: "See [reference/bigquery.md](reference/bigquery.md) for..."
- Progressive disclosure: Points to external files only when relevant
- Conditional navigation: "Which database are you using?"
- Common patterns with SQL examples
- Documentation table showing where to find information
- Under 300-line SKILL.md, assumes reference/ directory structure

**Use for linting:** Reference file structure, progressive disclosure patterns, documentation organization

**Linter checks:**
- Reference files are one level deep (reference/bigquery.md, not nested deeper)
- Each reference is introduced with "See [file.md](file.md) for..."
- Quick start content is inline, detailed content is referenced
- File references indicate what to read and when ("for table schemas", "for optimization")
- Table of contents organizing external resources
- No nested reference chains

---

### 4. User Interaction Skill — `user-interaction-skill.md` (192 lines)

**Pattern:** Multi-step workflow with user choices and confirmation  
**Domain:** Business proposal generation  
**Demonstrates:**
- Three-question guided workflow before starting
- Multiple choice patterns with free-form fallback ("Or describe:")
- Confirmation loops before final generation
- Option patterns (A: Approve, B: Modify, C: Change, D: Help)
- File output specification (filename format, location, verification checklist)
- Common patterns with examples
- Tips section for user success
- Clear invocation patterns and when to use

**Use for linting:** User interaction patterns, confirmation workflows, file output clarity

**Linter checks:**
- Multiple choice options provided with free-form escape hatches
- Confirmation loop before irreversible actions
- File output includes explicit path, format, and verification steps
- Pattern-based guidance (Quick proposal, Comprehensive, Visual)
- Clear "when to use" and "what to provide" sections
- Pass-through options for user uncertainty

---

### 5. Artifact Skill — `artifact-skill.md` (~120 lines)


**Pattern:** Generates a downloadable artifact and launches it correctly
**Domain:** Weekly status report generation (.docx)
**Demonstrates:**
- Confirmation loop before generating the artifact
- Explicit file-output contract: filename convention, location, format
- Correct artifact launch pattern: save with Write/docx skill + `present_files`
  call to surface the file
- "Do not output inline" instruction paired with the Write instruction
- Alternative side-panel artifact pattern (for review-and-iterate flows)
- Common artifact failure modes (silent creation, inline dump, wrong extension)
- Post-launch confirmation prompt ("did the file load correctly?")

**Use for linting:** Artifact launching validation, file-output contracts, present_files
usage, inline-vs-artifact guidance

**Linter checks:**
- Every file-producing step ends with a `present_files` call (or explicit link instruction)
- "Do not output inline" instruction present whenever an artifact is launched
- Filename pattern is specific (includes skill-specific variables like date/name)
- Environment-appropriate tool chosen (Write for disk files, artifact tool for side panel)
- Post-launch confirmation prompt to catch silent-failure cases

---

### 6. Subagent Skill — `subagent-skill.md` (~100 lines)

**Pattern:** Multi-stage orchestrator that launches sub-agents via Agent tool
**Domain:** Codebase health reporting (security + dependency audit)
**Demonstrates:**
- Agent tool invocation with explicit prompt and model selection
- Context passing to sub-agents (scope, return format)
- Per-sub-agent model selection (Opus for deep analysis, Sonnet for retrieval)
- Gating after each Agent call before using the result
- Synthesizing sub-agent outputs into a single report
- Failure handling when a sub-agent errors

**Use for linting:** Agent tool usage, context isolation, model selection per sub-agent, synthesis patterns

**Linter checks:**
- Agent prompt specifies scope explicitly (sub-agents share no context)
- Return format described in each Agent prompt
- Gate after each Agent call (error check before synthesis)
- Model selection documented per sub-agent
- Synthesis step combines results — does not pass sub-agent raw output to user directly

---

### 7. MCP Skill — `mcp-skill.md` (~100 lines)

**Pattern:** Skill that calls MCP tools for external API data
**Domain:** GitHub PR review queue
**Demonstrates:**
- MCP connectivity check before starting the workflow
- MCP tool call syntax and error handling (401, 404, generic)
- Sequential calls when one depends on another (list PRs → fetch reviews per PR)
- Explicit fallback when MCP server is unavailable
- "Never fabricate data" rule for missing fields
- Distinguishing MCP tools from Bash CLI substitutes

**Use for linting:** MCP tool usage, error handling, connectivity checks, no-fabrication rule

**Linter checks:**
- MCP connectivity verified before workflow depends on it
- Each MCP error case handled with a distinct user message
- Sequential ordering enforced for dependent calls
- Fallback defined for MCP unavailability
- No instructions to substitute Bash CLI silently for MCP

---

### 8. Composition Skill — `composition-skill.md` (~100 lines)

**Pattern:** Skill that composes two other skills via Skill tool, with a hand-off gate
**Domain:** Research brief generation (researcher → writer pipeline)
**Demonstrates:**
- Skill tool invocation with args
- Structured output passing between skills (named fields, not prose)
- Gate between Stage 1 and Stage 2 (check for empty/error output)
- Progress logging ("Running web-researcher now…")
- End-state summary after both skills complete
- Decision guidance: when to compose vs. inline

**Use for linting:** Skill tool usage, inter-skill hand-off, structured output discipline, gate placement

**Linter checks:**
- Skill tool invocations use structured args (not free-form prose)
- Gate present after Stage 1 result — checks for empty or error before Stage 2
- User notified at each stage transition
- End-state summary produced after both skills complete
- "When to compose" decision criteria documented

---

## How to Use These Exemplars

### For Linter Development
Use these exemplars as:

1. **Baseline reference:** Compare freshly-written skills against these patterns
2. **Pattern library:** Extract structural patterns for linting rules
3. **Best practice validation:** Verify skills follow the patterns demonstrated
4. **Gate language checking:** Validate frontmatter matches content complexity

### For Skill Authors
Use these exemplars as:

1. **Templates:** Copy the structure for similar skill types
2. **Examples:** See how good skills are organized and written
3. **Reference:** Check instruction voice, user interaction patterns, and documentation organization

## Key Patterns Demonstrated Across Exemplars

### Frontmatter Completeness
| Field | Simple | Gates | Reference | Interaction | Artifact | Subagent | MCP | Composition |
|-------|--------|-------|-----------|-------------|----------|----------|-----|-------------|
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `description` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `disable-model-invocation` | — | ✓ | — | — | — | — | — | — |
| `allowed-tools` | — | ✓ | — | — | — | — | — | — |
| `context: fork` | — | ✓ | — | — | — | — | — | — |

### Gate Language Strength
| Level | Example | Demonstrated In |
|-------|---------|-----------------|
| 1 | Description discovery | Simple, Reference, Artifact, MCP |
| 2 | Trigger word activation | All eight |
| 3 | Manual invocation only | Gates |
| 4 | Tool pre-approval | Gates |

### Content Organization
| Pattern | Simple | Gates | Reference | Interaction | Artifact | Subagent | MCP | Composition |
|---------|--------|-------|-----------|-------------|----------|----------|-----|-------------|
| Instructions only | ✓ | — | — | — | — | — | — | — |
| Workflow steps | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Reference files | — | — | ✓ | — | — | — | — | — |
| User interaction | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Examples/samples | ✓ | — | ✓ | ✓ | ✓ | — | — | — |
| Output format | — | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Artifact launching | — | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Sub-agent invocation | — | — | — | — | — | ✓ | — | — |
| MCP tool calls | — | — | — | — | — | — | ✓ | — |
| Skill composition | — | — | — | — | — | — | — | ✓ |

### Instruction Voice
All exemplars demonstrate:
- **Imperative language:** "Review code", "Deploy application", "Analyze data", "Generate proposal"
- **Directive style:** "ALWAYS run tests", "NEVER deploy with uncommitted changes", "Select your approach"
- **Specific over vague:** "Function names accurately describe behavior" not "Make sure things are clear"
- **No passive suggestions:** "Use RESTful naming" not "You might want to use RESTful naming"

---

## Research Sources

All exemplars are based on patterns identified in the comprehensive research documented in `exemplar-research-report.md`.

Key sources include:
- Official Anthropic: Claude Code Docs, Agent Skills overview, Best practices documentation
- GitHub: anthropics/skills, anthropics/claude-code, community skill examples
- Community analysis: Deep dives, production-ready skill guides, design patterns

See `exemplar-research-report.md` for complete source citations and detailed pattern analysis.

---

## Linter Integration

To use these exemplars in a linter:

### 1. Extract structural patterns
```
For each exemplar:
  - Parse YAML frontmatter
  - Count instruction lines
  - Identify gate language patterns
  - Extract reference file structure
  - Catalog instruction voice patterns
  - Document user interaction flows
```

### 2. Create comparison rules
```
Fresh skill should match:
  - Frontmatter completeness relative to content complexity
  - Gate language strength appropriate to skill type
  - File structure following progressive disclosure
  - Instruction voice consistency
  - User interaction patterns (when applicable)
```

### 3. Grade skill quality
```
Score skill against exemplars:
  - Does frontmatter match content complexity?
  - Are gates appropriate for side effects/automation?
  - Is reference structure one level deep?
  - Does instruction voice use imperatives consistently?
  - Are user interactions explicit and guided?
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 2026 | Initial exemplar research and creation; 4 exemplar patterns |
| 1.1 | April 2026 | Added pattern #5 — artifact-skill.md (artifact launching + file output) |
| 1.2 | April 2026 | Added patterns #6–8 — subagent-skill.md, mcp-skill.md, composition-skill.md |

---

**Last updated:** April 20, 2026
**Status:** Complete and ready for linter integration

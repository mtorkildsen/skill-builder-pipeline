---
name: skill-calibrator
description: Audit any SKILL.md for writing-pattern violations, auto-fix unambiguous issues in place, and report findings needing human attention. Use when linting a SKILL.md before release, when build-sesh finishes a draft and needs a quality gate, or for a standalone audit of any skill regardless of how it was built. Invoke as /skill-calibrator <path> or ask to "lint this skill". Always invoke this skill when a SKILL.md draft is complete and needs a final check.
metadata:
  version: "1.0.0"
---

# Skill Calibrator

Audits a `SKILL.md` against the pipeline's skill-writing patterns, auto-fixes
unambiguous issues in place, and returns a structured report of findings that require
human attention.

---

## When to Use This Skill

- Final quality gate after build-sesh finishes a build (in-pipeline mode)
- Standalone audit on any SKILL.md — older skills, externally authored skills,
  in-progress drafts
- Pre-release check before packaging a skill

---

## Entry Point

Identify the invocation surface, then proceed:

**A. Called by build-sesh (in-pipeline):**
- Inputs provided: path to the finished SKILL.md + target-skill root directory
- Run all checks, auto-fix safe issues, save report at
  `<target-skill-root>/build-sesh/workspace/linter-reports/final.md`
- Return exactly one line: `skill-calibrator: N auto-fixed, M need human. Report at <path>.`
- Do not loop or prompt — build-sesh manages resolution

**B. User invoked directly (standalone):**
- Input: path to a SKILL.md. Optional: `--out <report-path>` to override report location
- If path is not provided, ask: "Which SKILL.md should I audit? Provide the path."
- Run all checks, show diff before writing any auto-fixes, confirm with user before saving
- Save report at `<skill-dir>/linter-report.md` unless `--out` overrides
- Print multi-line summary to user after completing

---

## Reading Reference Files

Before running any checks, read:

1. `${CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md` — authoritative rule
   source for all checks. Changes here change what the linter enforces; the linter
   does not embed rules beyond "here is how to apply them"
2. `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml` — canonical paths registry;
   used in path-citation checks to verify exact registered paths
3. `${CLAUDE_PLUGIN_ROOT}/references/exemplar-skills/` — read all `.md` files except
   `README.md` and `exemplar-research-report.md`; used for structural comparison

---

## Checks

Run all 6 categories. For each finding: record line number, category, issue, and whether
it was auto-fixed or needs human attention.

### 1. Frontmatter

- `name` present, kebab-case, matches the skill's folder name
- `description` present, ≤ 1,024 chars; uses a concrete action verb; contains specific
  trigger phrases; is "pushy" enough per `description-optimization.md` patterns
- `metadata.version` (if present) is valid semver (e.g., `"1.0.0"`)

### 2. Structure

- Required sections present: `## When to Use This Skill`, `## Entry Point`, at least one
  workflow section
- Section headings use Title Case consistently
- No empty sections (heading immediately followed by another heading or `---`)
- SKILL.md body ≤ 500 lines; heavy content belongs in `references/` files, not inlined
- Every reference file is loaded with an explicit Read instruction before the step that
  uses it — not "refer to" or "consult"

### 3. Instruction Voice

- Procedural sections use imperative voice ("Read...", "Save...", "Spawn...", "Ask...")
- Flag passive voice and hedged language: "The skill will...", "Claude should
  consider...", "you may want to...", "consider", "try to", "feel free to"
- Gate language present at decision points; check against the 4 strength levels in
  `skill-writing-patterns.md` Section 1 and gate patterns in `exemplar-skills/gates-skill.md`
  — flag any gate below the recommended level for its risk
- Every file-producing step specifies: exact relative path, filename, format, and
  verification instruction ("After saving, confirm the file exists")
- All visual or downloadable outputs specify their launch method; no silent creation

### 4. Path Citations

- Every plugin-shared path uses `${CLAUDE_PLUGIN_ROOT}/...` (Form A)
- No bare `references/...` outside Form B context (bare relative from target-skill root)
- No absolute paths: `C:\`, `/sessions/`, `~/.claude/`, `/mnt/`
- No backslashes in path literals
- Every canonical-registry file cited by its exact registered path — compare against
  `canonical-paths.yaml` entries

### 5. Forbidden Patterns

Flag any occurrence of:
- `design-doc-[` — slug-drift pattern
- `qa-template.docx` — wrong extension (file ships as `.html`)
- `/sessions/...` — hardcoded Cowork absolute path
- Backslash characters in path literals

### 6. Gate Discipline

For every decision point or pass/fail gate:
- Explicit pass-action defined
- Explicit fail-action defined
- No "ask the user" without specifying exactly what to ask
- Compare against `exemplar-skills/gates-skill.md` patterns

---

## Auto-Fix Policy

Auto-fix only when the correct replacement is unambiguous. Always show a diff before
writing in standalone mode; write silently in in-pipeline mode (diff included in report).

**Auto-fix without asking:**
- Trailing whitespace; missing blank lines between sections
- Bare `references/<filename>` path → add `${CLAUDE_PLUGIN_ROOT}/` prefix, when the file
  exists in plugin `references/` and not in the target-skill tree
- `qa-template.docx` → `qa-template.html`
- Backslashes → forward slashes in path literals
- Weak Level-1 or Level-2 gates before file writes → escalate to Level 3 per
  `skill-writing-patterns.md` Section 1
- `"refer to references/X.md"` / `"consult references/X.md"` →
  `"Read \`references/X.md\`"` when the path is unambiguous

**Report, do not auto-fix:**
- Instruction voice issues where the correct rewrite depends on intent
- Missing required sections (fix requires authoring new content)
- Description improvements (trigger scope is author's decision)
- Ambiguous path citations where the bare form could resolve in multiple places
- Gate discipline issues that require the author to decide pass/fail behavior
- Any structural deviation that could be an intentional design choice

When in doubt, report. A wrong auto-fix is harder to catch than a manual fix.

---

## Output Artifacts

### Report (`linter-report.md`)

Save at:
- **In-pipeline:** `<target-skill-root>/build-sesh/workspace/linter-reports/final.md`
- **Standalone:** `<skill-dir>/linter-report.md` (or `--out` path)

```
# skill-calibrator report — <path-to-SKILL.md>
Run: <ISO date-time>
skill-writing-patterns.md version: <version>

## Summary
- N auto-fixed (saved to <path>)
- M need human attention

## Auto-fixed (N)
1. Line <n>: <what was changed and why>
2. ...

## Needs human attention (M)
1. Line <n>: <issue description>
   Suggestion: <concrete action the author can take>
   Reference: <path to the pattern that defines this rule>
2. ...
```

### Short Summary (in-pipeline return message)

```
skill-calibrator: N auto-fixed, M need human. Report at <path>.
```

### Multi-line Summary (standalone)

```
skill-calibrator audit of <path>:
  PASSED [cleanly | with findings].
  N issues auto-fixed (diff above).
  M issues need your decision.
  Full report: <report-path>
```

---

## In-Pipeline Escalation (build-sesh manages the loop)

Skill-linter returns results; it does not loop. Skill-creator drives resolution:

1. If `M = 0`: Build is clean — declare done and hand off to qa-sesh
2. If `M > 0`: build-sesh reads the report, presents each issue to the user one at a
   time, applies approved fixes, then re-invokes skill-calibrator
3. After 3 rounds with `M > 0`: build-sesh STOPs and escalates — present the full
   report and ask the user whether to override or resolve remaining issues before proceeding

---

## Canonical Paths Registry

At startup, read `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`. Key ids:

- `skill-writing-patterns` — authoritative quality patterns (Form A)
- `canonical-paths` — this registry (Form A)
- `exemplar-gates`, `exemplar-reference-files`, `exemplar-user-interaction`,
  `exemplar-simple` — structural comparison exemplars (Form A)
- `linter-reports-dir` — report save location in in-pipeline mode (Form B)
- `description-optimization` — description pattern reference (Form A)

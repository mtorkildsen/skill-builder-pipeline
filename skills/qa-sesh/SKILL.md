---
name: qa-sesh
metadata:
  version: "1.1.0"
description: >
  The release pipeline for skills. Picks up after build-sesh finishes building or
  revising a SKILL.md — enforces versioning, changelog documentation, generates a
  manual QA template as .html with colored PASS/FAIL/N/A highlighting, and packages
  into a distributable .skill file with version archive. Use this skill whenever a user says
  "run post QA", "post QA loop", "start post QA", "test and package this skill", or
  anything about versioning + testing + packaging a skill together. Also activate when
  a user asks about 2+ of: version bump, changelog, test cases, packaging, .skill file
  — offer to take over rather than auto-launching. This skill does NOT edit SKILL.md
  content (it tests, versions, documents, and packages — it doesn't fix). If something
  fails, it reports findings for build-sesh to address.
---

# QA Sesh

<!-- Version 1.1.0 — Changed manual QA template from .docx to .html with versioned file
     naming convention ({skill-name}-v{version}-manual-qa.html). Updated packaging to
     manual zip when package_skill.py is unavailable. -->

<!-- Version 1.0.0 — Pipeline redesign: cut re-testing upstream artifacts, coverage gap
     analysis, automated evals with grading, fresh session requirement. Added manual QA
     template as .html, version in metadata block, cross-reference against verification
     checklist. Rewrote all directory references to pipeline-directory-map.md conventions -->

The release pipeline for skills. You pick up after build-sesh finishes building or
revising a SKILL.md. The skill arriving from build-sesh is already tested through the
build iteration loop. Your job is to enforce versioning, document changes, generate a
manual QA template, and package the skill for distribution.

## Responsibility Boundary

**QA Sesh ships skills. It does not edit them.**

You version, document, test manually, and package. When you find failures during manual
QA, you report findings with enough specificity that build-sesh can act on them
without re-running the tests. You never attempt repairs to the skill's instructions.

The only writes you make to SKILL.md are metadata: version bump in the `metadata` block
in YAML frontmatter (Step 2). This is a metadata change, not a content change.

Why this boundary matters: if this skill started fixing things it found, it would enter
an internal fix-test loop that's uncontrollable and could silently degrade the skill.
Separation of concerns keeps the feedback loop legible to the user.

## Entry Point

The user provides two things:
1. **Skill root path** — so you can find SKILL.md and all build artifacts. All paths are
   relative to this root.
2. **Revision summary** — what changed (pasted text or file path)

If either is missing, ask for it.

## Main Workflow

Six steps, three gates. Work through them in order.

### Step 1: Intake

Locate the skill directory from the user-provided path. Validate that SKILL.md exists.
Parse frontmatter to extract `name`, `description`, and the `metadata.version` field.

Accept the revision summary as pasted text or a file path (read the file if it's a path).

If the revision summary is missing or too vague to classify the change type, ask the
user to elaborate. If they can't provide one, fall back to auto-diffing SKILL.md against
any previous version you can find. The diff approach is less reliable than a human
summary but better than guessing.

### Step 2: Version Bump

Read the current version from `metadata.version` in SKILL.md frontmatter. If there's no
version field or no metadata block (first-ever build), initialize at `1.0.0`.

The version lives inside the `metadata` block, not as a top-level frontmatter key:

```yaml
---
name: my-skill
metadata:
  version: "1.1.0"
description: >
  ...
---
```

Analyze the revision summary to propose a version bump:

- **Patch** (x.x.+1) — Bug fixes, typo corrections, formatting changes, wording tweaks.
- **Minor** (x.+1.0) — New features, new steps, expanded capabilities.
- **Major** (+1.0.0) — Breaking changes to workflow, removed steps, renamed inputs/outputs.

If the revision summary contains signals for multiple levels, pick the highest.

Present the proposed version at Gate 1 alongside the changelog entry.

### Step 3: Changelog

If `CHANGELOG.md` exists at the skill root, read it. If not (first build), create it.
After writing or updating `CHANGELOG.md`, confirm the file exists at the skill root.

Generate an entry from the revision summary using Keep a Changelog categories (Added,
Changed, Fixed, Removed, Deprecated, Security). Format:

```markdown
## [version] — YYYY-MM-DD

### Category
- Bullet summary of each change
```

Prepend new entries at the top (newest first). Present at Gate 1 alongside the version.

### → Gate 1: Version + Changelog Confirmation

Present the proposed version number, change type classification with your reasoning, and
the formatted changelog entry.

**STOP. Do not continue until the user explicitly confirms the version and changelog.**

The user can confirm, override the version level, edit the changelog wording, or reject
entirely. If they override the version level, recalculate the version number.

After confirmation:
- Write the version bump to SKILL.md frontmatter (`metadata.version`)
- Write or update `CHANGELOG.md` at the skill root
- Create the versioned output folder: `qa-sesh/v{version}/`

### Step 4: Manual QA Template

Generate a manual QA template as a static `.html` file. Write the HTML directly — do
not use the docx skill.

**File naming convention:** `{skill-name}-v{version}-manual-qa.html`

Example: `resume-optimizer-v5.0.0-manual-qa.html`

Read `handoff-sesh/verification-checklist.md` from the skill root before generating.
Cross-reference the verification checklist against the actual SKILL.md to produce test
cases that cover every step's failure modes.

The HTML template structure:

- **Title:** `QA: {Skill Name} v{version}`
- **Header fields:** Date, Time, Ver #
- **Test Conditions section:** placeholder for model used, input type, workflow path
- **Feature Summary:** one paragraph describing the skill, then a bulleted list of
  what this version changes (tag each with `[v{version}]` in blue bold)
- **Test Scope:** what to test, what to focus regression testing on
- **Test cases organized by workflow step** (`<h2>` per step), with each test case as:
  - Numbered ID (step-prefix: 1-1, 1-2, 2-1, etc.)
  - Description of what to test
  - Inline `PASS | FAIL | N/A` with colored backgrounds (PASS = green `#90EE90`,
    FAIL = yellow `#FFFF00`, N/A = orange `#FFD580`)
  - Notes field below each test case
  - Version-specific test cases tagged with `[v{version}]` in blue bold
- **End marker after each step section** (`– End --`) followed by:
  - Step Gate/Message field
  - User reply field
  - Step Notes field
- **Cross-cutting sections** as separate `<h2>` groups (e.g., Tone, Formatting,
  Gate Discipline, Reference File Usage, Integrity) — each with their own test
  cases and end marker
- **Overall section:** Total PASS/FAIL/N/A counts, critical failures (blocks ship),
  minor failures (log for next iteration)
- **Acceptance Criteria Summary:** Critical path success checklist + Quality gates
  checklist

CSS styling: Arial font, max-width 900px, centered. Use CSS classes for PASS/FAIL/N/A
highlighting. Version tags use blue bold (`color: #0066cc`).

If `handoff-sesh/verification-checklist.md` does not exist, generate the template from
SKILL.md directly — walk through each step and identify gates, file outputs, reference
reads, and format requirements.

Present the template to the user using the `present_files` tool so they can open it
directly. If `present_files` is not available, provide a `computer://` link to the file.

**STOP. Do not continue until the user approves the QA template.**

After approval, save to `qa-sesh/v{version}/{skill-name}-v{version}-manual-qa.html`.
After saving, confirm the file exists.

### → Gate 2: Manual QA Pass/Fail

The user tests the packaged skill against the manual QA template.

If pass → proceed to Step 5.

If fail → log what went wrong and route back to build-sesh with specific failure
details. Track the cycle count. After 3 failure cycles, escalate: repeated patches may
not be converging, and the issues might be at the design level. Recommend revisiting the
design document before another revision.

How to detect cycle count: look at the changelog for consecutive patch-level bumps with
similar descriptions. If the last 2+ entries are patches addressing similar issues,
that's a repeated failure pattern.

### Step 5: Package

Create the `.skill` package. Try `package_skill.py` first; fall back to manual zip if
the script is not available.

**Option A — Script packaging:**
Locate the `build-sesh` sibling skill in the same plugin, then look for
`scripts/package_skill.py` inside it.

```bash
python <build-sesh-dir>/scripts/package_skill.py <skill-path>
```

**Option B — Manual packaging (when script is unavailable):**
Create a zip archive with `.skill` extension containing SKILL.md and all reference files,
rooted under a `{skill-name}/` directory prefix:

```
{skill-name}/
  SKILL.md
  references/
    file1.md
    file2.md
    ...
```

Do NOT include build artifacts, test results, qa-sesh/, design/, archive/, or any
non-runtime files. Only include files the skill needs at execution time.

Save to `qa-sesh/v{version}/{skill-name}.skill`.
Verify the .skill file was created successfully and list its contents.

### Step 6: Archive

Create `{skill-name}-v{version}-qa.zip` containing all files in the versioned folder
(`qa-sesh/v{version}/`).

Save the archive to `qa-sesh/v{version}/{skill-name}-v{version}-qa.zip`.
After saving, confirm the archive file exists.

### → Gate 3: Final Summary

Present a final summary:
- Version number
- All artifacts produced with paths (relative to skill root)
- The .skill package file location
- The archive location

Present the `.skill` package file using the `present_files` tool so the user can install
it directly. If `present_files` is not available, provide a `computer://` link.

**STOP. Wait for the user to confirm the release is complete.**

## Output Structure

This stage writes to:
- `SKILL.md` — version bump in `metadata` block only (never content edits)
- `CHANGELOG.md` — new entry prepended at skill root
- `qa-sesh/v{version}/` — all QA artifacts for this release

```
{skill-root}/
  SKILL.md                                              ← version bump only
  CHANGELOG.md                                          ← new entry prepended
  qa-sesh/
    v{version}/
      {skill-name}-v{version}-manual-qa.html            ← manual QA template (.html)
      {skill-name}.skill                                ← distributable package
      {skill-name}-v{version}-qa.zip                    ← version archive
```

The versioned folder is the core organizational unit. Every artifact from Steps 4–6
lives inside `qa-sesh/v{version}/`. Previous releases accumulate as sibling folders
— never overwrite a prior versioned folder.

## Edge Cases

**First-ever build:** Initialize version at 1.0.0, create CHANGELOG.md from scratch.

**Manual QA fails repeatedly:** After 3 cycles, the problem is likely upstream of
implementation. Repeated patches on the same area often indicate a design-level mismatch.
Surface this pattern to the user.

**Revision summary incomplete:** Ask for detail first. Fall back to auto-diffing SKILL.md
against the previous version only if the user can't provide one.

---

## Reference Files

At startup, read `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`. Use registry
entries by `id` to resolve all canonical artifact paths rather than hardcoding them.
Key ids for this skill:

- `skill-md` — input: SKILL.md to version-bump and package (Form B, target-skill root)
- `verification-checklist` — input for QA template generation (Form B)
- `changelog` — output: CHANGELOG.md at skill root (Form B)
- `manual-qa-template`, `version-archive`, `version-folder` — versioned outputs (Form B,
  substitution vars: `version`, `skill-name`)
- `pipeline-directory-map` — path and naming conventions (Form A)
- `environment-instructions` — Cowork vs Claude.ai packaging differences (Form A)

Plugin reference files:

- Path conventions: `${CLAUDE_PLUGIN_ROOT}/references/pipeline-directory-map.md`
- Environment differences (Cowork vs Claude.ai packaging): `${CLAUDE_PLUGIN_ROOT}/references/environment-instructions.md`
- Verification checklist the QA template is generated from: `handoff-sesh/verification-checklist.md` (at skill root)
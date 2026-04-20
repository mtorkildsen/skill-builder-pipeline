# Pipeline Directory Map

**Version:** 1.0.0
**Pipeline role:** Canonical shared path reference. All pipeline skills read from this file to determine where inputs come from and where outputs go. No skill defines its own directory structure independently.
**Do not modify** this file during a build session. Changes go through the pipeline redesign process.

---

## Path Convention Rules

1. **All paths are relative to the skill root.** Never use absolute paths in skill instructions. The skill root is the directory containing `pipeline-state.json` for a given build.
2. **Pipeline infrastructure paths are relative to the pipeline root.** The pipeline root is the directory containing this file (`pipeline-directory-map.md`).
3. **No legacy path references.** Old naming conventions (`tdd-workspace/`, `build-sesh/workspace/`, etc.) are retired. Use only the paths defined here.
4. **Plugin portability.** Relative paths ensure the pipeline works after plugin packaging. Any skill that hardcodes an absolute path will break on install.

---

## Pipeline Infrastructure (fixed, relative to pipeline root)

```
skill-pipeline/
├── skill-pipeline-design-v3.md          # Locked architecture spec — do not modify
├── references/
│   ├── skill-writing-patterns.md        # Canonical instruction-writing reference
│   └── pipeline-directory-map.md        # This file
├── templates/
│   └── verification-checklist-template.md  # Template used by Stage 2 (Prep)
└── orchestrator/
    └── SKILL.md                         # Stage 0: Orchestrator skill
```

---

## Skill Build Directory (per-skill, relative to skill root)

When the orchestrator starts a new skill build, it creates the following structure at the skill root. The skill root itself lives wherever the user keeps their skills — the pipeline does not prescribe this location.

```
{skill-root}/
├── pipeline-state.json                  # Orchestrator state — written and read by Stage 0
├── design/
│   └── design-doc.md                    # Stage 1 output (planning-sesh)
├── handoff-sesh/
│   ├── register-classification.md       # Stage 2 output #1
│   ├── test-cases.md                    # Stage 2 output #3
│   ├── verification-checklist.md        # Stage 2 output #4
│   └── references/                      # Stage 2 output #2 (only if needed)
│       └── [domain-reference].md        # One file per domain area researched
├── build-sesh/
│   └── workspace/                       # Stage 3 working directory
│       ├── test-results/                # Test run outputs
│       │   └── [run-label].md           # One file per test run
│       └── linter-reports/              # Linter output per iteration
│           └── [iteration-label].md
├── qa-sesh/
│   └── v{version}/                      # Stage 4 versioned output folder
│       ├── CHANGELOG.md
│       ├── {skill-name}-v{version}-manual-qa.html  # Manual QA template (.html, colored PASS/FAIL/N/A)
│       └── {skill-name}-v{version}-qa.zip  # Version archive for rollback
└── SKILL.md                             # Final deliverable — written and revised by Stage 3
```

---

## Stage Input/Output Summary

| Stage | Name | Reads From | Writes To |
|-------|------|-----------|----------|
| 0 | Orchestrator | `pipeline-state.json` (if resuming) | `pipeline-state.json` |
| 1 | Design (planning-sesh) | User conversation | `design/design-doc.md` |
| 2 | Prep (handoff-sesh) | `design/design-doc.md` | `handoff-sesh/` (all 4 deliverables) |
| 3 | Build (build-sesh) | `design/design-doc.md`, `handoff-sesh/` | `SKILL.md`, `build-sesh/workspace/` |
| 4 | Release (qa-sesh) | `SKILL.md`, `handoff-sesh/verification-checklist.md` | `qa-sesh/v{version}/` |

---

## `pipeline-state.json` Schema

Written by the orchestrator at the skill root. Updated after each stage completes.

```json
{
  "skill_name": "my-skill",
  "skill_root": "relative/path/to/my-skill",
  "current_stage": "build",
  "completed_stages": ["design", "prep"],
  "stage_outputs": {
    "design": {
      "design_doc": "design/design-doc.md"
    },
    "prep": {
      "register_classification": "handoff-sesh/register-classification.md",
      "references": "handoff-sesh/references/",
      "test_cases": "handoff-sesh/test-cases.md",
      "verification_checklist": "handoff-sesh/verification-checklist.md"
    },
    "build": {
      "skill_md": "SKILL.md",
      "test_results": "build-sesh/workspace/test-results/",
      "linter_reports": "build-sesh/workspace/linter-reports/"
    },
    "release": {
      "version_folder": "qa-sesh/v{version}/",
      "changelog": "qa-sesh/v{version}/CHANGELOG.md",
      "qa_template": "qa-sesh/v{version}/{skill-name}-v{version}-manual-qa.html",
      "archive": "qa-sesh/v{version}/{skill-name}-v{version}-qa.zip"
    }
  },
  "metadata": {
    "version": null
  },
  "model_recommendation": "opus",
  "entry_type": "new",
  "created": "{ISO-8601-timestamp}",
  "last_updated": "{ISO-8601-timestamp}"
}
```

**Field notes:**
- `skill_root` — relative path from wherever the pipeline is running. Set once at orchestrator init, never changed.
- `current_stage` — values: `design`, `prep`, `build`, `release`, `complete`
- `completed_stages` — append-only. Never remove a completed stage.
- `entry_type` — values: `new`, `midstream`, `tweak`
- `model_recommendation` — values: `opus`, `sonnet`. Orchestrator sets this based on complexity assessment.

---

## Naming Conventions

### Path Sanitization (Windows compatibility)

Any folder or filename derived from user input must be sanitized before use in any
path, file write, or state file entry. Apply these steps in order:

1. Strip leading and trailing whitespace and periods
2. Replace characters illegal on Windows (`\ / : * ? " < > |`) with a hyphen
3. Collapse consecutive hyphens to one
4. If the sanitized name differs from what the user typed, show them the sanitized
   version and confirm before creating any files or writing the state file

This rule applies everywhere `{skill-name}` or any user-supplied label is used as
a folder or filename component — including the skill root folder, design doc filenames,
version archives, and state file values.

---

### Stage output files — fixed names, no variables in filenames

| File | Fixed Name |
|------|-----------|
| Design doc | `design-doc.md` |
| Register classification | `register-classification.md` |
| Test cases | `test-cases.md` |
| Verification checklist | `verification-checklist.md` |
| Orchestrator state | `pipeline-state.json` |
| Changelog | `CHANGELOG.md` |

### Files with version or skill-name substitution

These are the only files where variable substitution is permitted in filenames. The variable values must be confirmed before the file is written.

| File | Pattern | Variable Source |
|------|---------|----------------|
| Manual QA template | `{skill-name}-v{version}-manual-qa.html` | `skill_name` from state file; `version` from semver bump |
| Version archive | `{skill-name}-v{version}-qa.zip` | `skill_name` from state file; `version` from semver bump |
| Version folder | `qa-sesh/v{version}/` | `version` from semver bump |
| Domain references | `handoff-sesh/references/{descriptive-name}.md` | Descriptive name chosen by handoff-sesh based on domain |
| Test run results | `build-sesh/workspace/test-results/{run-label}.md` | Run label set by build-sesh per iteration |
| Linter reports | `build-sesh/workspace/linter-reports/{iteration-label}.md` | Iteration label set by build-sesh |

---

## Retired / Forbidden Path References

The following paths appear in legacy skill versions. Do not use them. If you encounter them in an existing skill, they must be rewritten to the conventions above.

| Legacy Path | Replace With |
|------------|-------------|
| `tdd-workspace/` | `build-sesh/workspace/` |
| `pipeline-directory-map.md` (root-level) | `references/pipeline-directory-map.md` |
| Any absolute path (e.g. `/sessions/...`) | Relative path from skill root |
| `design-analysis.md` | Absorbed into `handoff-sesh/register-classification.md` |
| `prompt-templates.md` | Cut — build-sesh extracts from design doc directly |

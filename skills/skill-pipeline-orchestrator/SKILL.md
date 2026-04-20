---
name: skill-pipeline-orchestrator
metadata:
  version: "1.1.0"
description: >
  Orchestrate a full skill build from idea to packaged .skill file. Detects entry point
  (new skill, midstream resume, or small tweak), auto-invokes stage subagents with right-
  sized models (or generates copy-paste handoffs in fallback mode), tracks state, enforces
  Gate 1 and Gate 2, and handles /tweak fast path.
  Trigger on: "build a skill", "start the pipeline", "resume my skill build", "/tweak",
  "tweak a skill", "orchestrate", or any request to run multiple pipeline stages together.
---

# Skill Pipeline Orchestrator

## Step 1: Startup

Read:
- `${CLAUDE_PLUGIN_ROOT}/references/pipeline-directory-map.md`
- `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`

Then run the environment detection probe (see **Environment Detection** below) before
doing anything else.

---

## Step 2: Detect Entry Point

Ask:

> "What would you like to do?
>
> 1. **New skill** — build from scratch
> 2. **Resume** — pick up a build in progress
> 3. **Tweak** — small change to an existing skill (or use `/tweak <path>`)
>
> Type a number, describe your situation, or paste a `/tweak` command."

**STOP. Wait for the user's response.**

Route to Entry A (New), Entry B (Resume), or Entry C (Tweak).

---

## Entry A: New Skill

### A1 — Collect name and root

Ask for the skill name. Sanitize it for filesystem compatibility (per pipeline-directory-map.md
Path Sanitization rules: strip leading/trailing whitespace and periods, replace
`\ / : * ? " < > |` with hyphens, collapse consecutive hyphens). If the sanitized name
differs, confirm with the user before continuing.

Ask for the parent directory. Confirm the full skill root: `{parent}/{sanitized-name}/`.

**STOP after each question. Wait for the user's response before asking the next.**

### A2 — Initialize state

Create `{skill-root}/pipeline-state.json`:

```json
{
  "skill_name": "{skill-name}",
  "skill_root": "{skill-root}",
  "mode": "full",
  "current_stage": "design",
  "completed_stages": [],
  "stage_outputs": {},
  "transition_mode": "{auto|copy-paste}",
  "metadata": { "version": null },
  "created": "{ISO-8601}",
  "last_updated": "{ISO-8601}"
}
```

Confirm the file was written before continuing.

### A3 — Launch Stage 1 (Design)

Announce: "Starting Stage 1: Design — planning-sesh will interview you about your skill idea.
Model: Opus. When the interview is complete, planning-sesh will save the design doc and I'll
pause for your review (Gate 1)."

**Auto mode:** Invoke planning-sesh via Agent tool (see **Stage Execution** section).
**Copy-paste mode:** Present the planning-sesh handoff prompt (see **Copy-Paste Templates**).

---

## Entry B: Resume

Ask for the skill root path.

Read `{skill-root}/pipeline-state.json`. If missing, offer: (1) try another path,
(2) reconstruct the state file manually.

**STOP. Wait for path before reading.**

Report: skill name, last completed stage, current stage. Then verify expected output
files exist (per the pre/post verification table in Stage Execution). Flag any missing
files and ask how to proceed before continuing.

Route to the next stage based on `current_stage` in the state file.

---

## Entry C: /tweak Fast Path

### When to enter tweak mode

- `/tweak <path>` — enter immediately, no confirmation needed.
- Natural-language ("just fix the typo in X", "quick fix to X's SKILL.md") — confirm
  first: "Running fast path — Design and Prep skipped, patch-only release. OK?"
  **STOP. Wait for confirmation.**
- Rejected phrasings (ask full vs fast instead): "update X", "improve X", "rewrite X".

Tweaks are changes where **the instructions the skill gives do not meaningfully change**:
typo fixes, one-sentence clarifications, path-citation updates, version reference updates,
whitespace/formatting, changelog edits. If in doubt, route to the full pipeline.

### C1 — Initialize tweak state

Create or update `{skill-root}/pipeline-state.json` with `mode: tweak`,
`current_stage: build`, `transition_mode: {auto|copy-paste}`.

### C2 — Launch Build (tweak mode)

Announce: "Running Stage 3: Build in tweak mode — build-sesh will apply the change,
show you a diff, wait for your approval, then run the linter. Model: Opus."

**Auto mode:** Invoke build-sesh via Agent tool with `tweak_description: {description}`
and `tweak_mode: true` in the briefing.
**Copy-paste mode:** Present the tweak-mode build-sesh handoff (see **Copy-Paste Templates**).

After Build completes (diff approved + lint done), proceed directly to C3.

### C3 — Lightweight Release

Announce: "Running Stage 4: Release (lightweight) — patch version bump, one-line
changelog entry, repackage. No QA template, no manual QA gate."

**Auto mode:** Invoke qa-sesh via Agent tool with `release_mode: lightweight`.
**Copy-paste mode:** Present the lightweight release handoff prompt.

### C4 — Escalation

If build-sesh reports the change isn't a tweak (adds/removes a section, touches
`description` in frontmatter, adds/removes a reference citation, affects test expectations):

> "This change isn't a tweak — it affects [X].
> Options: (a) abort — no changes saved, (b) full pipeline — Design + Prep + Build + Lint + Release."

**STOP. Wait for user choice.**

If (b): reset `mode: full` in state file, restart from Entry A with the tweak intent as
context for planning-sesh. If (a): discard any pending saves.

---

## Stage Execution (Auto Mode)

Read `${CLAUDE_PLUGIN_ROOT}/skills/skill-pipeline-orchestrator/references/subagent-briefings.md`
for complete briefing templates. Fill all `{placeholders}` from `pipeline-state.json`
and the current conversation before invoking.

### Model mapping

| Stage | Model |
|-------|-------|
| planning-sesh (Design) | Opus |
| handoff-sesh (Prep) | Sonnet |
| build-sesh (Build) | Opus |
| qa-sesh (Release) | Sonnet |

### Before each Agent call

1. Announce: stage name, model, what it reads, what it produces.
2. Verify required input files exist (table below). If any are missing, stop and ask.
3. Call Agent with the briefing. Do not announce mid-way status — wait for completion.

### After each Agent call

1. Read `pipeline-state.json` — confirm the stage appears in `completed_stages`.
2. Verify expected output files exist and are non-empty (table below).
3. If either check fails → treat as stage failure (see **Failure Handling**).
4. On success → update state and proceed to the next gate or stage.

### Pre/Post-Stage File Verification

| Stage | Required inputs | Required outputs |
|-------|----------------|-----------------|
| Design | none | `design/design-doc.md` |
| Prep | `design/design-doc.md` | `handoff-sesh/register-classification.md`, `handoff-sesh/test-cases.md`, `handoff-sesh/verification-checklist.md` |
| Build | `design/design-doc.md`, `handoff-sesh/register-classification.md`, `handoff-sesh/test-cases.md`, `handoff-sesh/verification-checklist.md` | `SKILL.md` |
| Release | `SKILL.md`, `handoff-sesh/verification-checklist.md` | `CHANGELOG.md`, `qa-sesh/v{version}/{skill-name}-v{version}-manual-qa.html` |

---

## Gate 1 — Post-Design (Human Approval)

After Design completes and outputs are verified:

1. Update state: add `"design"` to `completed_stages`, set `current_stage: "prep"`,
   add `stage_outputs.design: {design_doc: "design/design-doc.md"}`, update `last_updated`.

2. Present:
> "Stage 1 complete. Review `{skill-root}/design/design-doc.md`, then choose:
> - **approve** — proceed to Prep
> - **changes: [describe]** — I'll re-run planning-sesh with your feedback
> - **abort** — stop the pipeline"

**STOP. Wait for user response.**

On approval: launch Prep.
On changes: re-invoke planning-sesh via Agent tool (or handoff prompt) with the feedback string.
On abort: set `status: aborted` in state file.

---

## Gate 2 — Post-Build (Human Approval)

After Build completes — including lint, all linter issues resolved inside the Build
subagent — and outputs are verified:

1. Update state: add `"build"` to `completed_stages`, set `current_stage: "release"`,
   add `stage_outputs.build: {skill_md: "SKILL.md"}`, update `last_updated`.

2. Present:
> "Stage 3 complete. Review `{skill-root}/SKILL.md`, then choose:
> - **approve** — proceed to Release
> - **changes: [describe]** — I'll re-run build-sesh with your feedback
> - **abort** — stop the pipeline"

**STOP. Wait for user response.**

On approval: launch Release.
On changes: re-invoke build-sesh via Agent tool (or handoff prompt) with the feedback string.
On abort: set `status: aborted` in state file.

---

## Failure Handling

If a stage returns a failure or post-stage validation fails:

1. STOP. Do not auto-advance.
2. Update state: `status: failed`, `error: {description}`.
3. Present:

> "Stage {name} failed: {short error}
> Options:
>   **retry** — re-run the same stage with the same inputs
>   **skip** — advance past this stage (only if its outputs aren't needed downstream)
>   **abort** — stop the pipeline, keep artifacts for manual recovery"

**STOP. Wait for user input. No silent retries.**

---

## QA Failure Routing

When the user reports FAIL items after manual QA:

1. Add entry to `qa_failures` in state:
   `{cycle, stage_failed: "release", items: [...], routed_to: "build", date: "{ISO-8601}"}`.

2. Re-invoke build-sesh (auto or handoff) with targeted failure note:
   "QA found these failures: {list}. Fix only these items. Re-run relevant test cases
   from `{skill-root}/handoff-sesh/test-cases.md`."

3. After fix, return to Release (auto or handoff).

**3-cycle escalation:** If `qa_failures` has 3+ entries, recommend revisiting Stage 1
(Design) before continuing. Present options: go back to Design, keep trying in Build,
or accept and release anyway. **STOP. Wait for user decision.**

---

## Environment Detection

At startup, run this probe:

```
Agent(description: "env-probe", prompt: "Return the single word: AVAILABLE")
```

- If it succeeds: set `transition_mode: auto`.
- If it fails or the tool is unavailable: set `transition_mode: copy-paste`.

Record `transition_mode` in `pipeline-state.json` at init.

The user can force copy-paste mode with `/pipeline --copy-paste` or by setting
`transition_mode: copy-paste` in `pipeline-state.json` before invoking.

---

## Copy-Paste Templates

Use these in copy-paste mode. Fill all `{placeholders}` before presenting.

**Planning-Sesh Handoff:**
```
GRILL-ME HANDOFF — {skill-name}
Skill root: {skill-root}

I'm building a new skill called {skill-name}. {description}.
Run your full design interview. Save the design doc to: {skill-root}/design/design-doc.md.
When done, let the user know to return to the orchestrator.
```

**Build-Sesh Handoff:**
```
SKILL-CREATOR HANDOFF — {skill-name}
Skill root: {skill-root}

Design and prep are complete. Read before starting:
  {skill-root}/design/design-doc.md
  {skill-root}/handoff-sesh/register-classification.md
  {skill-root}/handoff-sesh/test-cases.md
  {skill-root}/handoff-sesh/verification-checklist.md
  {skill-root}/handoff-sesh/references/ (all files, if any)
  ${CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md

Save SKILL.md to: {skill-root}/SKILL.md. When done, return to the orchestrator.
```

**Build-Sesh Handoff (Tweak Mode):**
```
SKILL-CREATOR HANDOFF — {skill-name} (tweak mode)
SKILL.md path: {path-to-skill-md}
Tweak: {tweak-description}

Apply this specific change only. Show a diff. Wait for approval. Then invoke skill-calibrator.
Do NOT re-read the design doc, run test cases, or redraft any section beyond the tweak.
After linter completes, return to the orchestrator.
```

**QA-Sesh Handoff:**
```
POST-QA-LOOP HANDOFF — {skill-name}
Skill root: {skill-root}
Revision summary: {summary}

Run the full release workflow. When done, return to the orchestrator.
```

**QA-Sesh Handoff (Lightweight — tweak mode):**
```
POST-QA-LOOP HANDOFF — {skill-name} (lightweight release)
Skill root: {skill-root}
SKILL.md path: {path-to-skill-md}
Current version: {current-version}

Lightweight release only: patch version bump, one-line changelog entry, repackage.
Skip: QA template generation, version archive zip, Gate 2 manual-QA pause.
When done, present the .skill file to the user.
```

---

## Reference Files

At startup read `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`. Use registry
ids to resolve all artifact paths rather than hardcoding them.

Key ids for this skill:
- `pipeline-state`, `design-doc`, `register-classification`, `test-cases`,
  `verification-checklist`, `skill-md`, `changelog`, `manual-qa-template`,
  `version-archive`, `version-folder` — stage artifacts (Form B, target-skill root)
- `pipeline-directory-map`, `skill-writing-patterns`, `subagent-briefings`,
  `canonical-paths` — plugin-shared references (Form A)

Plugin reference files:
- Path conventions: `${CLAUDE_PLUGIN_ROOT}/references/pipeline-directory-map.md`
- Instruction writing standards: `${CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md`
- Subagent briefing templates: `${CLAUDE_PLUGIN_ROOT}/skills/skill-pipeline-orchestrator/references/subagent-briefings.md`
- Canonical artifact paths: `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`

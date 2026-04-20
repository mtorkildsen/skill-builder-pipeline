# Subagent Briefing Templates

**Used by:** Orchestrator SKILL.md, Stage Execution section
**Purpose:** Complete Agent-tool prompt templates for each pipeline stage. Fill all
`{placeholders}` from `pipeline-state.json` and the current conversation before passing
to the Agent tool. Each subagent reads its own SKILL.md for detailed instructions —
these briefings provide context and inputs only.

Return format expected from every subagent:
- Success: `"Stage <name> complete. Artifacts: <path list>. Next: <gate|stage>."`
- Failure: `"Stage <name> failed: <reason>. State saved at <path>."`

---

## Stage 1 (Design) — Planning-Sesh Briefing

**Agent call:** `model: opus`

```
SUBAGENT BRIEFING: Stage 1 — Design (Planning-Sesh)

You are running the planning-sesh skill as a pipeline subagent.

Skill name: {skill-name}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}
Description from user: {any description the user provided}
{OPTIONAL: User feedback from Gate 1 revision: {feedback}}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/planning-sesh/SKILL.md

STEP 2: Read the canonical paths registry.
Read: {CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml

STEP 3: Run the design interview per your SKILL.md instructions.
Save the completed design doc to: {skill-root}/design/design-doc.md

STEP 4: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "design" to completed_stages
- Set current_stage to "prep"
- Add stage_outputs.design: {"design_doc": "design/design-doc.md"}
- Update last_updated to current ISO-8601 timestamp

STEP 5: Return a completion summary in this format:
"Stage design complete. Artifacts: {skill-root}/design/design-doc.md. Next: Gate 1."
```

---

## Stage 2 (Prep) — Handoff-Sesh Briefing

**Agent call:** `model: sonnet`

```
SUBAGENT BRIEFING: Stage 2 — Prep (Handoff-Sesh)

You are running the handoff-sesh skill as a pipeline subagent.

Skill name: {skill-name}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/handoff-sesh/SKILL.md

STEP 2: Read the canonical paths registry.
Read: {CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml

STEP 3: Read the design document.
Read: {skill-root}/design/design-doc.md

STEP 4: Work through the 4 deliverables per your SKILL.md instructions.
Output files to produce:
- {skill-root}/handoff-sesh/register-classification.md
- {skill-root}/handoff-sesh/references/ (only if domain research needed)
- {skill-root}/handoff-sesh/test-cases.md
- {skill-root}/handoff-sesh/verification-checklist.md

STEP 5: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "prep" to completed_stages
- Set current_stage to "build"
- Add stage_outputs.prep with paths to all deliverables produced
- Update last_updated to current ISO-8601 timestamp

STEP 6: Return a completion summary in this format:
"Stage prep complete. Artifacts: {list paths}. Next: Stage 3 Build."
```

---

## Stage 3 (Build) — Build-Sesh Briefing

**Agent call:** `model: opus`

```
SUBAGENT BRIEFING: Stage 3 — Build (Build-Sesh)

You are running the build-sesh skill as a pipeline subagent.

Skill name: {skill-name}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}
{OPTIONAL: User feedback from Gate 2 revision: {feedback}}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/build-sesh/SKILL.md

STEP 2: Read the canonical paths registry.
Read: {CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml

STEP 3: Read all build inputs.
Read: {skill-root}/design/design-doc.md
Read: {skill-root}/handoff-sesh/register-classification.md
Read: {skill-root}/handoff-sesh/test-cases.md
Read: {skill-root}/handoff-sesh/verification-checklist.md
Read: {skill-root}/handoff-sesh/references/ (all files, if any exist)
Read: {CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md

STEP 4: Build the skill per your SKILL.md instructions.
Save SKILL.md to: {skill-root}/SKILL.md (save after every revision — progressive save).
After the build converges, invoke skill-calibrator (Skill tool) and resolve all issues.

STEP 5: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "build" to completed_stages
- Set current_stage to "release"
- Add stage_outputs.build: {"skill_md": "SKILL.md"}
- Update last_updated to current ISO-8601 timestamp

STEP 6: Return a completion summary in this format:
"Stage build complete. Artifacts: {skill-root}/SKILL.md. Next: Gate 2."
```

---

## Stage 3 (Build) — Build-Sesh Briefing (Tweak Mode)

**Agent call:** `model: opus`

```
SUBAGENT BRIEFING: Stage 3 — Build (Build-Sesh, Tweak Mode)

You are running the build-sesh skill in tweak mode as a pipeline subagent.

SKILL.md path: {path-to-skill-md}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}
Tweak: {tweak-description}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/build-sesh/SKILL.md

STEP 2: Read the existing SKILL.md.
Read: {path-to-skill-md}

STEP 3: Apply the tweak.
- Make only the specific change described above.
- Show the diff to the user. Wait for approval before saving.
- If the change requires adding/removing a section, touching `description` in
  frontmatter, adding/removing a reference citation, or would change test expectations —
  STOP and escalate: report the scope to the user and ask whether to abort or use the
  full pipeline.

STEP 4: After approval, invoke skill-calibrator.
Invoke skill-calibrator via Skill tool on the edited SKILL.md. Resolve any issues.

STEP 5: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "build" to completed_stages
- Set current_stage to "release"
- Add stage_outputs.build: {"skill_md": "{path-to-skill-md}"}
- Update last_updated to current ISO-8601 timestamp

STEP 6: Return a completion summary in this format:
"Stage build (tweak) complete. Artifacts: {path-to-skill-md}. Next: lightweight release."
Or if escalating: "Stage build escalated: {reason}. Awaiting user decision."
```

---

## Stage 4 (Release) — QA-Sesh Briefing

**Agent call:** `model: sonnet`

```
SUBAGENT BRIEFING: Stage 4 — Release (QA-Sesh)

You are running the qa-sesh skill as a pipeline subagent.

Skill name: {skill-name}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}
Revision summary: {paste or summarize what changed in the build stage}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/qa-sesh/SKILL.md

STEP 2: Read the canonical paths registry.
Read: {CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml

STEP 3: Follow the qa-sesh workflow per your SKILL.md.
Inputs to read:
- {skill-root}/SKILL.md
- {skill-root}/handoff-sesh/verification-checklist.md
- {skill-root}/CHANGELOG.md (if it exists)

Output files to produce:
- {skill-root}/SKILL.md (version bump in metadata block only)
- {skill-root}/CHANGELOG.md (new entry prepended)
- {skill-root}/qa-sesh/v{version}/{skill-name}-v{version}-manual-qa.html
- {skill-root}/qa-sesh/v{version}/{skill-name}-v{version}-qa.zip
- {skill-root}/{skill-name}.skill

STEP 4: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "release" to completed_stages
- Set current_stage to "complete"
- Add stage_outputs.release with paths to all output files
- Set metadata.version to the new version string
- Update last_updated to current ISO-8601 timestamp

STEP 5: Return a completion summary in this format:
"Stage release complete. Version: {version}. Artifacts: {list paths}. Next: manual QA."
```

---

## Stage 4 (Release) — QA-Sesh Briefing (Lightweight)

**Agent call:** `model: sonnet`

```
SUBAGENT BRIEFING: Stage 4 — Release (QA-Sesh, Lightweight)

You are running the qa-sesh skill in lightweight mode as a pipeline subagent.
This is a tweak release: patch version bump only.

Skill name: {skill-name}
Skill root: {skill-root}
Plugin root: {CLAUDE_PLUGIN_ROOT}
SKILL.md path: {path-to-skill-md}
Current version: {current-version}
Tweak summary: {one-line description of the change}

STEP 1: Read your skill instructions.
Read: {CLAUDE_PLUGIN_ROOT}/skills/qa-sesh/SKILL.md

STEP 2: Perform lightweight release only.
- Bump patch version: {current-version} → {next-patch-version}
- Update metadata.version in SKILL.md frontmatter
- Prepend one-line changelog entry: "v{next-patch-version} — {tweak-summary}"
- Repackage as .skill file

SKIP (not applicable for a tweak):
- Manual QA template generation
- Version archive zip
- Gate 2 manual-QA pause

STEP 3: Update the state file.
Read {skill-root}/pipeline-state.json and write it back with:
- Add "release" to completed_stages
- Set current_stage to "complete"
- Set metadata.version to {next-patch-version}
- Update last_updated to current ISO-8601 timestamp

STEP 4: Present the .skill file to the user.

STEP 5: Return a completion summary in this format:
"Stage release (lightweight) complete. Version: {next-patch-version}. Skill file: {path}."
```

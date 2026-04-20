# Skill Pipeline Plugin

A 5-skill pipeline for building high-quality Claude skills: Design → Prep → Build → Release, with orchestration, state tracking, linting, and verification.

## Stages

| Stage | Skill | Mode | Purpose |
|-------|-------|------|---------|
| 0 | **Orchestrator** | Interactive | Detects entry point, plans sessions, tracks state, launches subagents |
| 1 | **Design** (planning-sesh) | Interactive | Design interview — produces `design/design-doc.md` |
| 2 | **Prep** (handoff-sesh) | Subagent | Generates register classification, references, test cases, verification checklist |
| 3 | **Build** (build-sesh) | Interactive | Writes SKILL.md with embedded linter, progressive save, and test iteration |
| 4 | **Release** (qa-sesh) | Subagent + QA | Versions, generates .html QA template, packages .skill file |

## Getting Started

Say "build a skill" or "start the pipeline" to trigger the orchestrator. It will walk you through the full process.

## Skills Included

- **planning-sesh** — Stage 1. Guided design interview that turns a rough idea into a buildable spec.
- **skill-pipeline-orchestrator** — Entry point. Manages state, handoffs, and subagent execution.
- **handoff-sesh** — Stage 2. Produces 4 deliverables from the design doc.
- **build-sesh** — Stage 3. Writes and iterates on SKILL.md with linting.
- **qa-sesh** — Stage 4. Versions, documents, QA templates, and packages.

## Shared References

- `references/pipeline-directory-map.md` — Canonical path conventions for all stages
- `references/skill-writing-patterns.md` — Instruction quality standards (gates, files, artifacts, voice)
- `references/exemplar-skills/` — 4 curated exemplar skills for linter comparison
- `templates/verification-checklist-template.md` — Per-step failure mode template
- `references/pipeline-flow.html` — Visual pipeline flow diagram (open in a browser)

## Requirements

- Claude Code or Cowork with subagent support
- The `best-practices-researcher` skill (used by handoff-sesh for reference file research)

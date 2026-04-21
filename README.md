# Skill Builder Pipeline

A guided 5-stage pipeline for building high-quality Claude skills. Anthropic's built-in skill creator is a great starting point, but complex skills need more scaffolding — structured design, better test cases, quality calibration, and a proper release process. This pipeline fills that gap.

Each stage is its own skill. You can run them individually or let the orchestrator manage the full flow.

---

## How to Install

1. Download `skill-pipeline.zip` from the [latest release](../../releases/latest)
2. In Cowork → Customize → Skills → `+` → upload the zip

---

## The Pipeline

| Stage | Skill | What it does |
|-------|-------|--------------|
| 0 | `skill-pipeline-orchestrator` | Entry point — detects where you are, manages state, runs stages automatically or via handoff |
| 1 | `planning-sesh` | Guided design interview — one question at a time until you have a complete, unambiguous spec |
| 2 | `handoff-sesh` | Turns the design doc into build-ready materials: register classification, reference files, test cases, verification checklist |
| 3 | `build-sesh` | Writes and iterates on SKILL.md with progressive saves and test runs |
| 4 | `skill-calibrator` | Audits the finished skill against quality standards — auto-fixes what it can, flags the rest |
| 5 | `qa-sesh` | Versions the skill, generates a QA template, and packages it for distribution |

---

## How to Start

**Run the full pipeline:**
"run the pipeline" or "start the pipeline"

**Jump to a specific stage:**
- "let's start a planning sesh"
- "let's start a handoff sesh"
- "let's start a build sesh"
- "calibrate this skill"
- "let's start a qa sesh"

---

## What's Included

- `skills/` — one folder per skill, each with a SKILL.md
- `references/` — shared reference files used across stages
- `references/exemplar-skills/` — 8 curated example skills showing different patterns
- `references/canonical-paths.yaml` — single source of truth for all artifact paths
- `scripts/` — pre-package validation scripts
- `templates/` — verification checklist template

---

## Requirements

- Claude Code or Cowork with subagent support
- The `best-practices-researcher` skill (used by handoff-sesh for reference file research)

---

## Background

Built by [Michael Torkildsen](https://github.com/mtorkildsen). Designed to sit between Anthropic's basic skill creator and full TDD-style skill writing frameworks — structured enough to produce quality results, approachable enough to use on a regular basis.

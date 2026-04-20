---
name: handoff-sesh
metadata:
  version: "3.0.0"
description: >
  Prepares a completed design document for build-sesh by generating build-ready
  support materials: register classification, reference file research, test cases
  with mock files, and a verification checklist. Use this skill whenever a user has
  finished designing a skill (via planning-sesh or any other method) and wants to prepare
  it for building. Trigger on phrases like "prep for build", "build handoff", "get
  this ready for build-sesh", "handoff to builder", "prepare build materials",
  "prep the handoff", or any variation of "I have a design doc and want to get it
  ready to build." Also trigger when a user says "we're done designing, now what?"
  or "let's get this ready for build-sesh." This skill bridges the gap between
  design and build — it ensures build-sesh has everything it needs to produce
  high-quality output on the first iteration rather than guessing at ambiguities.
---

# Handoff Sesh

<!-- Version 3.0 — Pipeline redesign: cut design-analysis.md and prompt-templates.md,
     added verification-checklist.md, added progressive save per deliverable,
     rewrote all directory references to pipeline-directory-map.md conventions -->

You are preparing a completed design document for handoff to build-sesh. Your job is
to produce four deliverables that eliminate guesswork during the build phase and set the
skill up for healthy QA iteration — not just a correct first build, but a foundation
that improves rather than degrades when issues are found and fixed later.

The reason this matters: build-sesh works best when it knows not just *what* to build,
but *how* to write each part — which instructions should be rigid procedures and which
should be flexible principles. Without this guidance, build-sesh defaults to writing
everything as procedural rules, which produces skills that are brittle under QA pressure.

---

## Before You Start

1. Ask for the skill root path if the user hasn't provided it:
   > "What's the root folder path for this skill? I'll read the design document from
   > there and save all handoff materials into it."
   All paths are relative to this root. Do not use absolute paths anywhere.

2. Locate the design document. Look first at `design/design-doc.md` inside the skill
   root. If it's not there, it might be:
   - A file the user points you to
   - Content from the current conversation (e.g., a planning-sesh session that just finished)

3. Read the entire design document before starting the analysis.

4. If the design doc has "Open Questions" or "Blockers" sections, flag these to the
   user at the start. They may want to resolve them before the handoff or explicitly
   mark them as out of scope for the first build.

---

## The Four Deliverables

Work through these in order. Each builds on the previous one. **Save each deliverable
to disk immediately after the user approves it** — do not batch saves at the end.

### Deliverable 1: Register Classification

Walk through every step, gate, rule, and edge case in the design document — once. For
each instruction, run through three questions in sequence. This single pass replaces
what would otherwise be multiple re-reads of the same document.

#### Question 1: Is the designer's intent clear?

If the instruction is ambiguous, incomplete, or contradictory — ask the user before
proceeding. The goal is to resolve *design ambiguity* here so it doesn't get passed
downstream to build-sesh.

Examples of design ambiguity:
- A step says "validate the input" but doesn't define what valid means
- Two steps describe overlapping responsibilities with no clear boundary
- A gate says "if applicable" without defining when it applies

When you find design ambiguity, ask the user a specific question with options where
possible, not an open-ended "what did you mean here?"

#### Question 2: Is there only one valid way to implement this?

If a builder could reasonably do two different things, write explicit decision logic
that removes the *implementation ambiguity*. This includes: classification criteria
(what makes something "critical" vs. "major"?), prioritization order, thresholds,
and conditional branching.

Include concrete examples — "For an IT PM, SDLC Management is critical because it's
a core role-defining skill" is far more useful than "classify skills by importance."

#### Question 3: Should this be written as a procedure or a principle?

Classify every instruction into one of two registers so build-sesh knows *how*
to write it — not just what it should contain.

**Procedural** — Use for: required gates, sequencing, specific confirmations, format
rules backed by external constraints (like ATS parser requirements), and domain
knowledge that has a deterministic right answer. These should be written as explicit
steps with clear conditions. Claude needs to follow these, not interpret them.

**Principle-based** — Use for: tone, interaction style, edge case handling, user
experience decisions, and anything where Claude's judgment should adapt to context.
These should be written as explanations of *why* something matters, with enough
context for Claude to generalize to situations the design doc didn't anticipate.

**How to classify:**
- Does this have a single correct implementation? → Procedural
- Does it require judgment that should adapt to context? → Principle-based
- Watch for rules that *look* procedural but are actually judgment calls wearing a
  rigid costume. "Limit bullets to 2 lines" sounds procedural but is really a proxy
  for "don't let bullets become unfocused paragraphs." The principle version is more
  resilient because Claude can handle the 3-line bullet that's genuinely dense vs.
  the 2-line bullet that's padded.
- Also watch for the reverse: "Make sure the resume is ATS-compatible" sounds like a
  principle, but ATS compatibility has specific, testable requirements. That needs
  procedural treatment.

#### Edge Case Routing

Design documents (especially those from planning-sesh) often include a long list of edge
cases. These are valuable — they represent thorough design thinking. But if they all
get hardcoded into the skill as rules, they create exactly the constraint accumulation
that degrades skills over QA cycles.

For each edge case in the design document, route it to one of three destinations:

- **Into the skill as a principle** — Only when the edge case reveals a design intent
  that wouldn't be obvious from the main workflow. The edge case is really teaching
  Claude *how to think* about a class of situations, not just one specific scenario.

- **Into test cases (Deliverable 3)** — Most edge cases belong here. They are
  scenarios the skill should handle, but if the principles are good, it handles them
  without dedicated rules. You prove it works through testing, not through
  instructions. If a test fails, you refine a principle — you don't add a rule for
  that specific case.

- **Dropped** — Defensive speculation that never occurs in practice, or that Claude
  handles correctly by default.

**Present to user:** Show the full analysis organized by workflow step. For each
instruction, show the resolved ambiguity (if any), the implementation logic (if
needed), and the register classification. Show the edge case routing table separately.
Ask: "Does this analysis look right? Any classifications you'd change?"

**STOP. Do not continue until the user explicitly approves the register classification.**

After approval, save to `handoff-sesh/register-classification.md` inside the skill root.
Format: markdown with H2 headers per workflow step.
After saving, confirm the file exists before moving to the next deliverable.

---

### Deliverable 2: Reference File Research

During the register classification, you'll have encountered instructions that require
domain knowledge beyond Claude's built-in capabilities. This deliverable triages those
needs and creates the reference files.

**How to assess what needs a reference file:**
- If the answer varies by industry, role, or context → reference file
- If getting it wrong would cascade into bad downstream output → reference file
- If Claude would give a reasonable but inconsistent answer across runs → reference file
- If it's general knowledge Claude handles well → skip it

**Present the triage to the user first.** List the reference files you plan to create,
what each one covers, and why it matters. Also list the knowledge areas you're
*skipping* and why. Ask: "Are these the right reference files? Would you add or remove
any?"

**STOP. Do not begin research until the user approves the reference file list.**

After the user approves the list, use the `best-practices-researcher` skill to create
each reference file. Launch research agents in parallel when possible — this is often
the longest part of the handoff.

Each reference file should be structured for quick lookup — tables, organized sections
with headers, not prose. The skill will read these on demand during execution, so they
need to be scannable, not narrative.

Save each reference file to `handoff-sesh/references/` inside the skill root.
Use a descriptive filename for each: `handoff-sesh/references/{descriptive-name}.md`.
After saving, confirm each file exists before moving to the next deliverable.

If no reference files are needed (the design doc contains only general knowledge),
skip this deliverable and note that in the handoff summary. Proceed to Deliverable 3.

---

### Deliverable 3: Test Cases with Mock Files

Before writing test cases, read `${CLAUDE_PLUGIN_ROOT}/references/exemplar-skills/` from the pipeline plugin's
shared references directory. Read `gates-skill.md`, `reference-files-skill.md`,
`user-interaction-skill.md`, and `simple-skill.md` (skip `README.md` and
`exemplar-research-report.md`). These show the structural patterns that build-sesh's
linter will check — knowing them helps you write friction-path tests that probe whether
the skill handles pattern deviations correctly.

Create realistic test scenarios that exercise the skill's main workflow, variations,
and edge cases. Each test case includes its input file specifications inline.

**How to approach this:**
- Start with the edge cases routed here from Deliverable 1. These are your edge case
  test scenarios, already identified and triaged
- Add the happy path and the most important workflow variations
- Add a **friction path**: user provides inputs at each step, but not the expected ones.
  If the skill offers options A, B, or C, the friction test has the user pick C with
  modifications. If the skill asks for a file path, the user gives a nonstandard one.
  If the skill asks a question, the user gives a partial answer that requires follow-up.
  The point is to test that the skill handles real user behavior at every step, not
  just the designed path.
- Each test case needs: a descriptive name, input description (with full mock file
  specs if files are required), any user-provided parameters, and a detailed expected
  output
- Expected outputs should be specific and verifiable — not "produces a good resume"
  but "produces a .docx with 3 roles, gap skills placed under correct employers,
  auto-generated Skills section grouped by category"
- Mock file specs should be specific enough to generate without interpretation
- Aim for 3-5 test cases that cover: happy path, friction path, and the trickiest
  edge cases

**Present to user:** Show the test cases and ask "Do these cover the right scenarios?
Would you add, remove, or modify any?"

**STOP. Do not continue until the user approves the test cases.**

After approval, save to `handoff-sesh/test-cases.md` inside the skill root.
Format: markdown with H2 per test case.
After saving, confirm the file exists before moving to the next deliverable.

---

### Deliverable 4: Verification Checklist

Generate a per-step checklist of failure modes to watch for during testing. This
checklist is used by build-sesh during build testing and by qa-sesh for QA
template generation.

Read `${CLAUDE_PLUGIN_ROOT}/templates/verification-checklist-template.md` from the pipeline plugin
before generating. Do not rely on your training knowledge for the template structure —
use the template file exactly.

For each step in the design document, populate every check from the template:

- **Gate compliance** — current gate strength level + escalation path if gate fails
- **Step skipping risk** — whether Claude might decide this step isn't needed
- **Step merging risk** — distinct steps that might get combined
- **File hallucination** — every step that produces a file: verify it exists
- **Reference drift** — steps that use reference files: verify the reference was read
- **Output format deviation** — steps with specific format requirements: verify format
- **Artifact launch compliance** — outputs intended for side panel: verify they launch

Also populate the cross-cutting checks section: happy path completion, friction path
handling, session recovery, and the file inventory table.

**Present to user:** Show the completed checklist and ask "Does this cover the right
failure modes? Anything you'd add?"

**STOP. Do not continue until the user approves the verification checklist.**

After approval, save to `handoff-sesh/verification-checklist.md` inside the skill root.
Format: markdown following the template structure exactly.
After saving, confirm the file exists before proceeding to the handoff summary.

---

## Handoff Summary

After all four deliverables are saved, compile a handoff summary that lists:
- All files created and their paths (relative to skill root)
- Confirmation that each file exists on disk
- Any open items or assumptions noted during the analysis

Present the summary to the user. This marks the end of Stage 2 (Prep).

---

## Output Structure

All deliverables go into `handoff-sesh/` inside the skill root. Create this directory
if it doesn't exist.

```
{skill-root}/
  handoff-sesh/
    register-classification.md
    test-cases.md
    verification-checklist.md
    references/                    # Only if domain research was needed
      ├── {descriptive-name}.md
      └── ...
```

---

## What Makes a Good Handoff

The litmus test: could someone who wasn't in the design conversation pick up these
materials and build the skill without asking clarifying questions? If yes, the handoff
is complete. If they'd need to guess at anything, there's a gap to fill.

Specifically:
- The register classification resolves every ambiguity, provides explicit decision
  logic where needed, classifies every instruction's register, and routes edge cases
  to the right destination
- Reference files provide deterministic answers for things that shouldn't vary
- Test cases exercise every major workflow path and key edge cases, with mock file
  specs detailed enough to generate without interpretation
- The verification checklist catalogues failure modes for every step so testers know
  what to watch for

---

## Tips

- The design document is your source of truth. Don't invent requirements that aren't
  in it. If you think something is missing, ask the user rather than filling it in
  yourself.
- When creating reference files, prefer launching multiple research agents in parallel
  rather than doing them sequentially. This is often the longest part of the handoff.
- The user has already made all the design decisions. Your job is to operationalize
  those decisions into build-ready materials, not to reopen them.
- The register classification is the most valuable output this skill produces. Without
  it, build-sesh writes everything in the same procedural voice, which produces
  skills that are rigid where they should be flexible. Take the time to classify
  carefully — it directly affects how resilient the skill will be under QA.

---

## Reference Files

At startup, read `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`. Use registry
entries by `id` to resolve all canonical artifact paths rather than hardcoding them.
Key ids for this skill:

- `design-doc` — input: design document to read (Form B, target-skill root)
- `register-classification`, `domain-references-dir`, `test-cases`,
  `verification-checklist` — outputs: paths for the four deliverables (Form B)
- `pipeline-directory-map` — path and naming conventions (Form A)
- `skill-writing-patterns` — quality patterns and gate levels (Form A)
- `verification-checklist-template` — template to read before Deliverable 4 (Form A)
- `exemplar-gates`, `exemplar-reference-files`, `exemplar-user-interaction`,
  `exemplar-simple` — exemplar skills for Deliverable 3 (Form A)

Plugin reference files:

- Path conventions: `${CLAUDE_PLUGIN_ROOT}/references/pipeline-directory-map.md`
- Instruction writing standards (gate levels, register classification, voice): `${CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md`
- Verification checklist template: `${CLAUDE_PLUGIN_ROOT}/templates/verification-checklist-template.md`
- Exemplar skills (for the reference research step): `${CLAUDE_PLUGIN_ROOT}/references/exemplar-skills/`
                                       
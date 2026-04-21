---
name: build-sesh
metadata:
  version: "2.0.0"
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users say "let's start a build sesh", "build sesh", "start a build sesh", or when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Build Sesh

<!-- Version 2.0 — Pipeline redesign: added explicit handoff-sesh reading, embedded
     linter in iteration loop, added progressive save, cut benchmark aggregation /
     blind comparator / two-round eval cycle, rewrote all directory references to
     pipeline-directory-map.md conventions -->

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description improver, which we have a whole separate script for, to optimize the triggering of the skill.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. If you haven't heard (and how could you, it's only very recently that it started), there's a trend now where the power of Claude is inspiring plumbers to open up their terminals, parents and grandparents to google "how to install npm". On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

Briefly explain terms when you're unsure of the user's familiarity. A short inline definition costs nothing and prevents confusion.

---

## Reading Handoff-Sesh Deliverables

**Before writing or revising SKILL.md, read all available handoff-sesh deliverables.**

If a `handoff-sesh/` directory exists at the skill root, read these files in order:

1. `handoff-sesh/register-classification.md` — tells you how to write each instruction
   (procedural vs. principle-based). This is the most important input. Use register
   classifications to guide writing voice: procedural instructions become explicit steps
   with clear conditions; principle instructions become explanations with reasoning.
2. `handoff-sesh/references/` — domain-specific reference files. Scan the directory and
   read each file. These contain knowledge the skill needs to access at runtime.
3. `handoff-sesh/test-cases.md` — test scenarios with mock file specs. Use these as your
   test cases instead of generating your own.
4. `handoff-sesh/verification-checklist.md` — per-step failure modes to watch for during
   testing. Reference this while running test cases to know what to verify at each step.

If `handoff-sesh/` does not exist (skill built outside the pipeline), proceed with the
standard create-from-scratch workflow below.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism - include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: currently Claude has a tendency to "undertrigger" skills -- to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit "pushy". So for instance, instead of "How to build a simple fast dashboard to display internal Anthropic data.", you might write "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

**Progressive save:** Save SKILL.md to the skill root after every revision. If the
session crashes mid-iteration, the last revision is on disk.

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited, scripts can execute without loading)

These word counts are approximate — go longer when the content requires it.

**Key patterns:**
- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:
```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```
Claude reads only the relevant reference file.

#### Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** - You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** - Include examples when they clarify intent. Format them like this (deviate from this structure if "Input" and "Output" appear as content in the examples):
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Explain to the model *why* things are important rather than relying on heavy-handed MUSTs. Use theory of mind. Write skills that generalize beyond specific examples — they should handle novel inputs, not just the test cases. Write a draft, step away mentally, then revisit and tighten it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

**If handoff-sesh test cases exist** (`handoff-sesh/test-cases.md`), use those instead
of generating your own. They were designed during the prep stage and include happy path,
friction path, and edge cases with detailed mock file specs.

Save test cases to `build-sesh/evals/evals.json` inside the skill root. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

The `assertions` field will be added later during the eval loop (see Step 2 below).

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `build-sesh/workspace/` inside the skill root directory. Organize test
results and linter reports using the directory map conventions:

- Test results: `build-sesh/workspace/test-results/{run-label}.md` — one file per run
- Linter reports: `build-sesh/workspace/linter-reports/{iteration-label}.md` — one per iteration

For test runs that produce output files (e.g., .docx, .xlsx), save those outputs alongside
the result file: `build-sesh/workspace/test-results/{run-label}/outputs/`

### Step 1: Spawn all runs in the same turn

**First iteration only — run baseline comparison.** For each test case, spawn two
subagents: one with the skill, one without. This confirms the skill outperforms vanilla
Claude. After the first iteration confirms the skill adds value, subsequent iterations
run with-skill tests only. The user can request another baseline comparison at any time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: build-sesh/workspace/test-results/{run-label}-with-skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run (first iteration only):**
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `build-sesh/workspace/test-results/{run-label}-baseline/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r` the skill directory to `build-sesh/workspace/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `build-sesh/workspace/test-results/{run-label}-old-skill/outputs/`.

Write an `eval_metadata.json` for each test case with descriptive names. If this iteration uses new or modified eval prompts, create these files for each new eval directory — don't assume they carry over from previous iterations. After saving each `eval_metadata.json`, confirm the file was written.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `build-sesh/evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `build-sesh/evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them. After saving each `timing.json`, confirm the file was written.

### Step 4: Grade and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. After saving each `grading.json`, confirm the file was written. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants) — the viewer depends on these exact field names. For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and can be reused across iterations.

2. **Launch the viewer** with both qualitative outputs and quantitative data. The
   `eval-viewer/generate_review.py` script lives in this skill's directory (the
   `build-sesh/` skill folder). Locate it relative to where this skill is
   installed:
   ```bash
   nohup python <this-skill-dir>/eval-viewer/generate_review.py \
     build-sesh/workspace/test-results/{run-label} \
     --skill-name "my-skill" \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   To find `<this-skill-dir>`: check the path this SKILL.md was loaded from and use
   its parent directory.

   **Cowork / headless environments:** Use `--static <output_path>` to write a standalone
   HTML file instead of starting a server. Feedback will be downloaded as a `feedback.json`
   file when the user clicks "Submit All Reviews". After download, copy `feedback.json`
   into the workspace directory for the next iteration to pick up.

Note: please use generate_review.py to create the viewer; there's no need to write custom HTML.

3. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here and let me know."

**If using the verification checklist** (`handoff-sesh/verification-checklist.md`):
while reviewing test results, cross-reference each step's output against the
verification checklist. Note any PASS/FAIL for gate compliance, step skipping, file
hallucination, reference drift, output format, and artifact launch.

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:
- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each configuration, with per-eval breakdowns.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

Kill the viewer server when you're done with it:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Post-Draft Linting

When the iteration loop converges — the user is satisfied, feedback is empty, or no
further meaningful progress is being made — invoke skill-calibrator as a final quality gate
before declaring Build done.

Invoke via the Skill tool:
- Pass: path to the finished SKILL.md and the target-skill root directory
- skill-calibrator runs all checks, auto-fixes safe issues, saves a report at
  `<target-skill-root>/build-sesh/workspace/linter-reports/final.md`, and returns
  a one-line summary: `skill-calibrator: N auto-fixed, M need human. Report at <path>.`

If the summary reports `M > 0` (issues needing human attention):
1. Read the linter report at `<target-skill-root>/build-sesh/workspace/linter-reports/final.md`
2. Present each issue to the user one at a time with the linter's suggestion
3. Apply approved fixes, then re-invoke skill-calibrator
4. Repeat up to 3 rounds. After 3 rounds with remaining issues, STOP and escalate —
   present the full report and ask the user whether to override or address issues before
   proceeding

When the linter returns `M = 0`, or the user explicitly accepts remaining issues,
declare Build done and hand off to qa-sesh.

---

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The big picture thing that's happening here is that we're trying to create skills that can be used a million times (maybe literally, maybe even more who knows) across many different prompts. Here you and the user are iterating on only a few examples over and over again because it helps move faster. The user knows these examples in and out and it's quick for them to assess new outputs. But if the skill you and the user are codeveloping works only for those examples, it's useless. Rather than put in fiddly overfitty changes, or oppressively constrictive MUSTs, if there's some stubborn issue, you might try branching out and using different metaphors, or recommending different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Make sure to read the transcripts, not just the final outputs — if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, you can try getting rid of the parts of the skill that are making it do that and seeing what happens.

3. **Explain the why.** Try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart*. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and what they actually wrote, and then transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach.

4. **Look for repeated work across test cases.** Read the transcripts from the test runs and notice if the subagents all independently wrote similar helper scripts or took the same multi-step approach to something. If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it. This saves every future invocation from reinventing the wheel.

5. **Triage every issue before touching the skill.** This is critical for preventing skill degradation over QA cycles. When you get feedback — whether from the user, from eval results, or from your own review — classify each issue *before* writing any revision:

   - **Knowledge gap** — Claude doesn't know a domain-specific fact, convention, or format rule. Example: "it used an em dash but ATS parsers reject those." Fix: add a specific, narrow rule *with the reasoning attached* (e.g., "Avoid em dashes and decorative symbols — ATS parsers frequently misread or strip them, which breaks keyword matching").
   - **Judgment gap** — Claude doesn't understand the *intent* behind an instruction, so it applies it mechanically or in wrong contexts. Example: "it verified role dates even when there was only one resume with no conflicts." Fix: don't add another rule. Instead, rewrite the existing instruction to explain *why* it exists and *when* it matters. Give Claude the mental model, not a longer checklist.
   - **Behavioral regression** — a previous fix created a new problem. Example: "after we added the rule about concise bullets, it started truncating important context." Fix: find the conflicting constraints and reconcile them — usually by replacing both narrow rules with one principle-level explanation. Never just add a third rule to patch the conflict.

   After classifying, apply one more check: **count the constraints.** If your revision adds a rule, look for an existing rule to consolidate or remove. The total constraint count in a skill should stay roughly stable across iterations. If it's growing every cycle, that's a leading indicator of degradation — the skill is accumulating scar tissue. When you notice this, pause and do a consolidation pass: look for clusters of narrow rules that share a common *why* and replace them with a single principle-level instruction that communicates the underlying intent.

   The instinct to "add a rule for every bug" is the single most common way skills degrade over QA cycles. Resist it. Most bugs are judgment gaps disguised as knowledge gaps.

This task is pretty important (we are trying to create billions a year in economic value here!) and your thinking time is not the blocker; take your time and really mull things over. I'd suggest writing a draft revision and then looking at it anew and making improvements. Really do your best to get into the head of the user and understand what they want and need.

---

## Description Optimization

Read `${CLAUDE_PLUGIN_ROOT}/skills/build-sesh/references/description-optimization.md` before running description optimization.
It contains the full 4-step workflow: generate eval queries, review with user, run the
optimization loop, and apply the result.

---

### Package and Present (only if `present_files` tool is available)

Check whether you have access to the `present_files` tool. If you don't, skip this step. If you do, package the skill and present the .skill file to the user:

```bash
python <this-skill-dir>/scripts/package_skill.py <path/to/skill-folder>
```
(Where `<this-skill-dir>` is the build-sesh skill directory.)

After packaging, direct the user to the resulting `.skill` file path so they can install it.

---

## Output Structure

All artifacts produced during skill creation live inside `build-sesh/` in the skill
root. Create this directory before running any test cases.

```
{skill-root}/
  SKILL.md                                    ← created/edited by build-sesh
  build-sesh/
    evals/
      evals.json                              ← test definitions, grows across sessions
    workspace/
      skill-snapshot/                         ← copy of previous SKILL.md (improvement
                                                 runs only — overwritten each session)
      test-results/                           ← test run outputs
        {run-label}.md                        ← one file per test run
      linter-reports/                         ← linter output per iteration
        {iteration-label}.md
```

Note: the permanent record of each prior release lives in `qa-sesh/v{version}/`,
not here. The `skill-snapshot/` folder is just a working copy for the current
improvement session.

---

## Environment-Specific Instructions

Read `${CLAUDE_PLUGIN_ROOT}/references/environment-instructions.md` for the section matching your current environment (Claude.ai or
Cowork). It covers adaptations for test execution, reviewing, benchmarking, packaging,
and updating existing skills in each environment.

---

## Reference Files

At startup, read `${CLAUDE_PLUGIN_ROOT}/references/canonical-paths.yaml`. Use registry
entries by `id` to resolve all canonical artifact paths rather than hardcoding them.
Key ids for this skill:

- `design-doc`, `register-classification`, `domain-references-dir`, `test-cases`,
  `verification-checklist` — inputs from prior stages (Form B, target-skill root)
- `skill-md` — output: path to write the final SKILL.md (Form B)
- `test-results-dir`, `linter-reports-dir` — workspace directories (Form B)
- `skill-writing-patterns` — linter quality patterns (Form A)
- `exemplar-gates`, `exemplar-reference-files`, `exemplar-user-interaction`,
  `exemplar-simple` — structural comparison exemplars (Form A)
- `environment-instructions` — environment-specific adaptations (Form A)
- `description-optimization` — description optimization workflow (Form A)
- `pipeline-directory-map` — path and naming conventions (Form A)

This skill's local references directory contains:
- `${CLAUDE_PLUGIN_ROOT}/skills/build-sesh/references/description-optimization.md` — the 4-step workflow for optimizing skill
  trigger descriptions (used by the Description Optimization section above)

The pipeline plugin's shared references directory contains:
- `${CLAUDE_PLUGIN_ROOT}/references/skill-writing-patterns.md` — quality patterns used by the linter
- `${CLAUDE_PLUGIN_ROOT}/references/exemplar-skills/` — curated exemplar skills for structural comparison
- `${CLAUDE_PLUGIN_ROOT}/references/environment-instructions.md` — environment-specific adaptations
- `${CLAUDE_PLUGIN_ROOT}/references/pipeline-directory-map.md` — path conventions and naming rules

---

Repeating one more time the core loop here for emphasis:

- Figure out what the skill is about
- Draft or edit the skill
- Run the linter, auto-fix, save
- Run claude-with-access-to-the-skill on test prompts
- With the user, evaluate the outputs:
  - Run `eval-viewer/generate_review.py` to help the user review them
  - Check against verification checklist if available
- Repeat until you and the user are satisfied
- Package the final skill and return it to the user.

Please add steps to your TodoList, if you have such a thing, to make sure you don't forget. If you're in Cowork, please specifically put "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" in your TodoList to make sure it happens.

Good luck!

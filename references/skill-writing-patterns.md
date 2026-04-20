# Skill Writing Patterns

**Version:** 1.0.0
**Pipeline role:** Shared reference. Loaded by handoff-sesh during register classification and by the build-sesh linter during comparison.
**Do not modify** this file during a build session. Changes go through the pipeline redesign process.

---

## 1. Step Gates

Gates are the enforcement mechanism in a skill. They prevent Claude from skipping steps, merging steps, or proceeding before a condition is met. Gate strength must match the risk of blowthrough.

### The 4 Strength Levels

**Level 1 — Soft prompt** (low-risk steps, user can reasonably override)
> "Before moving on, confirm the file path looks correct."

Use when: a missed step is recoverable, or the user is expected to verify casually.
Risk: Claude may treat this as optional. Do not use on steps that produce required outputs.

---

**Level 2 — Explicit hold** (standard gate for most steps)
> "Do not proceed to the next step until the user confirms."
> "Wait for user approval before continuing."

Use when: the step produces an output the next step depends on. This is the default gate level for the majority of skill steps.
Risk: Claude may interpret "wait" loosely in long chains. Pair with a specific trigger phrase if the step has a clear completion signal.

---

**Level 3 — Hard stop** (steps with irreversible outputs or branching logic)
> "STOP. Do not continue until the user explicitly types [confirm] or [skip]."
> "Do not write any files until the user approves the plan above."

Use when: the step writes a file, sends output to a tool, or makes a decision that affects all downstream steps. Gates before file creation should always be Level 3 minimum.
Risk: Claude may soften the language when paraphrasing. Write gates as their own paragraph, not embedded in a longer sentence.

---

**Level 4 — Nuclear** (steps where proceeding incorrectly causes session-level damage)
> "**FULL STOP. Do not take any action — including reading files, running tools, or generating content — until the user responds to the question above.**"

Use when: the skill is about to do something that cannot be undone, or when a wrong branch would require starting over. Use sparingly — overuse trains Claude to ignore them.
Risk: Even nuclear gates can be bypassed if buried in dense text. Place on its own line, bolded, above any other content in the step.

---

### Gate Escalation Path

If a gate fails during testing (Claude proceeds past it without triggering), escalate:
- Level 1 → Level 2: Add "Do not proceed until..."
- Level 2 → Level 3: Add "STOP." as a standalone sentence before the condition
- Level 3 → Level 4: Bold + full stop language + enumerate prohibited actions explicitly
- Level 4 still failing: the gate logic is in the wrong place. Move it earlier in the step, before any content Claude might generate.

---

### Gate Anti-Patterns

❌ Buried gate — gate language appears after generated content in the same step
> "Here is the analysis. Review it and let me know if you want changes before we proceed."
Fix: gate comes first, content comes after approval.

❌ Conditional gate — gate only triggers under certain conditions
> "If you want to move on, just say so."
Fix: gate is unconditional. If continuation requires a condition, state it explicitly as the trigger.

❌ Soft gate on hard output — Level 1 language before a file write
> "Let me know if the outline looks good and I'll save it."
Fix: file writes are always Level 3 minimum.

❌ Merged gate — gate for two separate steps combined into one
> "Once you approve the outline and the register classification, I'll move to writing the SKILL.md."
Fix: separate gate per step. Compound gates are easy for Claude to partially satisfy.

---

## 2. File Output Instructions

Claude will hallucinate file creation — it will describe saving a file without actually saving it — unless instructions are maximally explicit. Every step that produces a file must specify all four of the following:

### Required: Path, Filename, Format, Verification

**Path:** Relative to the skill root. Never absolute. Never vague ("in the output folder").
> `Save to handoff-sesh/register-classification.md`

**Filename:** Exact. No variables, no "something like".
> Correct: `verification-checklist.md`
> Wrong: `[skill-name]-checklist.md` (unless skill-name substitution is explicitly defined earlier)

**Format:** State the file type and any structural requirements.
> "Save as markdown. Use H2 headers for each section."
> "Save as .docx using the docx skill."

**Verification:** Instruct Claude to confirm the file exists after saving.
> "After saving, read the file back and confirm it was written correctly before proceeding."

---

### File Output Template

```
Save the [output name] to `[relative/path/filename.ext]`.
Format: [markdown / .docx / .json / etc.]
[Any structural requirements — headers, schema, etc.]
After saving, confirm the file exists before moving to the next step.
```

---

### File Output Anti-Patterns

❌ Vague path
> "Save the output somewhere accessible."
Fix: exact relative path.

❌ No verification
> "Write the register classification and we'll move on."
Fix: always verify after writing.

❌ Inline creation without save instruction
> "Here is the test cases file: [content]"
Fix: generating content in chat is not the same as saving a file. Explicit save instruction required.

❌ Dependent filename
> "Save as [skill-name]-test-cases.md"
Fix: only use variable filenames if the variable is explicitly defined and confirmed earlier in the session. Otherwise use a fixed name.

---

## 3. Reference File Usage

A reference file is only useful if Claude actually reads it. "Refer to" and "consult" do not reliably trigger a file read. Use explicit Read tool instructions.

### Correct Pattern

```
Read `references/skill-writing-patterns.md` before writing this section.
Do not rely on your training knowledge for [topic] — use only what is in the reference file.
```

### When to Use a Reference vs. Training Knowledge

Use a reference file when:
- The content is domain-specific and Claude would hallucinate details (legal, medical, technical specs)
- The content defines conventions that must be consistent across the pipeline
- The content was researched specifically for this skill and is not general knowledge

Use training knowledge when:
- The task is general writing, structure, or formatting
- The reference file would be a restatement of common knowledge
- No reference file exists for the topic

### Reference File Anti-Patterns

❌ Vague reference instruction
> "Consult the reference files in the references/ folder."
Fix: name the specific file. Claude will not reliably scan a directory.

❌ Reference instruction at end of step
> "[Step content...] Refer to skill-writing-patterns.md for guidance."
Fix: read instruction comes first, before any generation.

❌ Optional reference
> "You may want to check the reference file for examples."
Fix: if the reference matters, the read is mandatory, not optional.

---

## 4. Progressive Disclosure

SKILL.md should be scannable. If a reader needs to scroll past 500 lines to find a step, the skill is too dense. Long content belongs in `references/`.

### What Goes in SKILL.md

- Step sequence and gates
- Decision logic and branching
- Short examples (under 10 lines)
- File output instructions
- User interaction prompts

### What Goes in `references/`

- Full prompt templates (more than ~15 lines)
- Detailed domain knowledge (checklists, taxonomies, rubrics)
- Exemplar outputs Claude should match
- Any content that is consulted, not executed

### The 500-Line Rule

If SKILL.md exceeds 500 lines, audit it:
1. Find any block of content that is "consulted" rather than "executed"
2. Extract it to `references/[descriptive-name].md`
3. Replace with a Read instruction pointing to the new file

---

## 5. Artifact Launching

Artifacts (visual outputs rendered in the side panel) fail silently if the launch instruction is wrong or missing. Claude will generate the content but not present it correctly.

### Environments and Correct Launch Patterns

**Side panel artifact (React, HTML, SVG):**
```
Present this as an artifact in the side panel using the Write tool.
Do not output the content inline in chat.
```

**Downloadable file (.docx, .xlsx, .pdf, .pptx):**
```
Save the file to `[path/filename.ext]` and present it to the user
using the present_files tool so they can open it directly.
```

**Inline code or markdown (intentional):**
```
Output the following as a code block in chat [no artifact instruction needed].
```

### Common Artifact Failure Modes

❌ Silent creation — file is written but not presented
> The skill saves a .docx but never calls present_files.
Fix: every file-producing step ends with a present_files call or explicit link instruction.

❌ Inline instead of side panel — artifact content dumped in chat
> Claude generates 200 lines of HTML inline instead of launching a side panel artifact.
Fix: explicit "Do not output inline" instruction paired with Write tool instruction.

❌ Wrong tool for environment — using Write for a side panel React component
> React artifacts use the artifact system, not Write.
Fix: know the environment. Write is for files on disk. Artifact tool is for side panel rendering.

❌ No confirmation — artifact launched but skill doesn't verify user can see it
> Fix: after launching, include a one-line prompt: "Let me know if the [output] loaded correctly."

---

## 6. User Interaction Patterns

### Presenting Options

When offering choices, always:
1. Number the options
2. Give a one-line description of each
3. State the default or recommended option explicitly
4. Ask for a selection, not open-ended input

```
How would you like to handle [decision]?

1. [Option A] — [what it does]
2. [Option B] — [what it does]
3. [Option C] — [what it does]

Default: Option 1. Type a number to choose, or describe something different.
```

### Handling "I Don't Know"

Design every required decision point with an explicit fallback for when the user doesn't know the answer:

```
If the user says they don't know or aren't sure, [specific fallback behavior]:
- Use [default value] and note it as an assumption
- OR ask a simpler follow-up question: "[simpler question]"
- OR proceed with [safe default] and flag it for review
```

Never leave a decision point with no fallback. Skills that require the user to know a specific answer before proceeding will stall.

### Pass-Through Instructions

When the user should provide raw content (a file, a job description, a design doc), do not ask them to summarize or reformat it. Instruct them to paste or upload it directly:

```
Paste your [content type] directly below this message.
Do not summarize it — I need the full text.
```

### Confirmation vs. Input

Distinguish between steps where the user is confirming (yes/no) vs. providing new input. Don't mix them in the same prompt:

❌ "Does this look right, and also what tone would you like for the cover letter?"
Fix: confirm first, then ask for tone as a separate prompt.

---

## 7. Instruction Voice

Skill instructions are directives, not descriptions. Claude reads SKILL.md as instructions to itself. Every step should be written as if you are telling Claude what to do, not describing what will happen.

### Directive vs. Descriptive

❌ Descriptive (wrong register):
> "The skill will analyze the resume and identify gaps."
> "Claude should consider the user's tone preference."

✅ Directive (correct register):
> "Analyze the resume. Identify gaps in [specific areas]."
> "Ask the user: 'What tone would you like — formal, conversational, or direct?'"

### Weak Language to Avoid

These phrases introduce ambiguity about whether an action is required:
- "consider" → replace with a specific instruction
- "you might want to" → remove; if it matters, make it required
- "it may be helpful to" → remove or make explicit
- "try to" → either it's required or it isn't
- "feel free to" → never appropriate in a directive

### Step Structure Template

```
## Step N: [Step Name]

[Gate if required — before any content]

[What to do — directive voice, specific actions]

[File output instruction if applicable]

[User prompt if applicable]

[Gate for next step]
```

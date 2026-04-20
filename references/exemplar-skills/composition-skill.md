---
name: research-and-brief
description: Researches a topic and drafts a structured brief by composing two skills in sequence. Use when you need a fully sourced brief, competitive summary, or background report and want research and writing handled as separate, focused stages.
---

# Research and Brief

Compose two skills in sequence: first `web-researcher` gathers sources and extracts key facts, then `brief-writer` drafts the structured brief using those findings.

Each skill runs via the Skill tool with its own focused instructions. This skill is the orchestrator — it handles the hand-off, the gate between stages, and the final summary.

## When to compose rather than inline

Use skill composition when:
- Two skills have clearly separable responsibilities and well-defined inputs/outputs
- The second skill needs the first's output but not the orchestrator's full context
- Both skills are already well-tested standalone and you want to reuse them without duplication

Do not compose if the hand-off between stages requires nuanced judgment that only the orchestrator can make — keep that logic inline instead.

## Workflow

### Step 1: Collect scope

Ask:
1. Topic or question to research? (be specific — "AI safety in autonomous vehicles" not "AI")
2. Desired brief length? (A: Executive summary 1 page, B: Standard brief 3–5 pages, C: Full report 8+ pages)
3. Target audience? (e.g., "product leadership", "technical team", "external investors")
4. Any known sources to include or exclude?

Confirm before invoking any skill.

### Step 2: Invoke web-researcher skill

Tell the user: "Running web-researcher now — gathering sources and extracting key facts."

```
Skill({
  skill: "web-researcher",
  args: "topic: <TOPIC>; depth: <brief_length_mapped_to_depth>; exclude: <EXCLUDED_SOURCES>"
})
```

Wait for the skill to complete. Collect the structured output:
- `sources`: list of URLs with one-line descriptions
- `key_facts`: bulleted findings grouped by subtopic
- `gaps`: topics the researcher flagged as under-sourced

**Gate:** If `key_facts` is empty or the researcher reports it could not find relevant sources:
- Tell the user what was found (or not found).
- Ask whether to broaden the search, try alternate keywords, or stop.
- Do not invoke brief-writer with empty source material.

### Step 3: Invoke brief-writer skill

Tell the user: "Research complete. Running brief-writer now — drafting the brief."

Pass the structured research output:

```
Skill({
  skill: "brief-writer",
  args: "topic: <TOPIC>; audience: <AUDIENCE>; length: <LENGTH>; sources: <SOURCES_FROM_STEP_2>; key_facts: <KEY_FACTS_FROM_STEP_2>; gaps: <GAPS_FROM_STEP_2>"
})
```

The brief-writer uses `gaps` to add a "Limitations" section noting where the research was thin, so the reader understands confidence levels.

Wait for the skill to complete.

### Step 4: Summarize

After both skills complete, provide a closing summary:

```
## Brief Complete

**Topic:** <TOPIC>
**Sources:** <n> sources consulted
**Gaps flagged:** <gap count> (see Limitations section in brief)
**Output:** <inline or file path>

The brief is ready. Let me know if you want to expand any section or re-run
the research with different keywords.
```

If the user requested a file output: write the brief to `brief-<slug>-<YYYY-MM-DD>.md` and present the file.

## Composition guidelines

- **Log the hand-off**: always tell the user which skill is running and why ("Running web-researcher now...") so they know where they are in the multi-skill workflow.
- **Pass structured output, not prose**: use named fields or JSON between skills. The receiving skill cannot reliably parse unstructured text from the previous skill.
- **Gate between stages**: check for errors or empty results after every Skill call. Launching the second skill with bad input from the first just propagates the error.
- **Summarize after both complete**: the user interacted with two separate skills and may have lost track. Give them a clear end-state summary so they know the full workflow is done.
- **Respect user cancellation**: if the user says "stop" or "cancel" after Stage 1, do not auto-launch Stage 2. Ask first.
- **Don't re-invoke a completed stage**: if the user asks for a revision after the brief is done, invoke brief-writer directly with the revised instructions — do not re-run web-researcher unless the research itself was the problem.

## When to use this skill

- Preparing a competitive landscape brief before a product decision
- Researching a technical topic before writing an architecture proposal
- Producing a background report for a stakeholder meeting
- Any workflow where research and writing are cleanly separable and benefit from focused, independent instructions

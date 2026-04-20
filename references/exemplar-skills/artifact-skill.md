---
name: weekly-status-report
description: Generates a formatted weekly status report as a downloadable .docx file. Use when a user says "create my status report", "write up this week's status", "generate a weekly update", or hands over a list of accomplishments/blockers and wants a polished document to share with stakeholders.
---

# Weekly Status Report

Turn a list of weekly accomplishments and blockers into a polished, downloadable `.docx`
that can be shared with stakeholders.

## Inputs

Ask the user for these up front if not provided:

- **Reporting week** (e.g., "Week of Apr 15")
- **Accomplishments** — 3-6 bullet points of what shipped or progressed
- **Blockers** — any items at risk or needing escalation
- **Next week's focus** — top 2-3 priorities for the coming week

If the user provides a messy brain-dump instead, organize it into the four sections above
and show the draft back to them for confirmation before generating the file.

## Workflow

### 1. Draft and confirm

Restate the inputs in structured form. Show the user:

```
Week of [date]

Accomplishments
- [item 1]
- [item 2]

Blockers
- [item 1 — status, ask]

Next week
- [priority 1]
- [priority 2]
```

Ask: "Does this capture it? Anything to add, remove, or reword before I generate the
`.docx`?"

**STOP.** Wait for the user's confirmation. Do not generate the file until they approve.

### 2. Generate the .docx

Use the `docx` skill to build the file. The document structure:

- **Title:** `Weekly Status — {User Name}, Week of {Date}`
- **Section 1: Accomplishments** — bulleted list
- **Section 2: Blockers** — bulleted list, each with a one-line status and ask
- **Section 3: Next Week's Focus** — numbered list

Formatting rules:
- Header: bold, 16pt
- Section titles: bold, 12pt
- Body: 11pt, single-spaced
- Page margins: 1 inch all sides

### 3. Save and present the file

**File location:** save to the user's working directory.

**File naming:** `weekly-status-{yyyy-mm-dd}.docx` (use the Monday of the reporting week
as the date).

**Launch instruction:**

Save the file using the `docx` skill, then call `present_files` with the saved path
so the user can download or open it directly.

```
Save the file to `weekly-status-{yyyy-mm-dd}.docx` and present it to the user
using the present_files tool so they can open it directly.
```

Do not output the .docx content inline in chat — it will not render correctly.

### 4. Confirm the file rendered

After presenting, close with:

> "Your status report is ready — let me know if the file loaded correctly or if you
> want me to adjust the formatting."

If the user says the file didn't load, the most common causes are: (a) the
present_files call was skipped, (b) the file path was wrong, or (c) the docx skill
returned an error. Check each before regenerating.

## When to use a side-panel artifact instead

If the user wants an **editable preview** inside the chat session rather than a
downloadable file, offer a side-panel HTML artifact as an alternative. Use the
artifact tool (not Write) and explicitly instruct:

```
Present this as an artifact in the side panel using the artifact tool.
Do not output the HTML inline in chat.
```

Side-panel artifacts are best for review-and-iterate flows. `.docx` output is best
for sharing with stakeholders outside the chat.

## Common failure modes

- **File saved but not presented** — always pair the Write/docx-skill step with a
  `present_files` call. The user cannot access the file otherwise.
- **Inline dump instead of artifact** — Claude generates 200 lines of markdown or HTML
  in the chat instead of producing a downloadable file. Fix: repeat the "do not output
  inline" instruction.
- **Wrong file extension** — `.doc` (old format) is not interchangeable with `.docx`.
  Always use `.docx`.
- **Generic filename** — `status-report.docx` is ambiguous when a user has many weeks
  of reports. Always include the date in the filename.

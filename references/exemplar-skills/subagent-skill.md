---
name: codebase-health-report
description: Generates a codebase health report by running security and dependency audits as parallel sub-agents. Use when you want a comprehensive health check, prepare for a release audit, or produce a team-wide code quality summary.
---

# Codebase Health Report

Orchestrate two specialized sub-agents — a security auditor and a dependency auditor — each running in its own context window via the Agent tool. Synthesize their outputs into a single executive report.

Running each audit as a sub-agent prevents large codebases from overflowing the orchestrator's context and lets each agent focus without distraction.

## Workflow

### Step 1: Collect scope

Ask:
1. Root directory to audit? (default: current working directory)
2. Which sections? (A: All, B: Security only, C: Dependencies only)
3. Output format? (A: Inline summary, B: Write file to disk)

Confirm before launching any sub-agents.

### Step 2: Launch security sub-agent

```
Agent({
  description: "Security scan — detect hardcoded secrets, unsafe patterns, injection risks",
  subagent_type: "general-purpose",
  model: "opus",
  prompt: "You are a security auditor. Scan the repository at <ROOT_DIR>.

Check for:
1. Hardcoded credentials or secrets in source files
2. Unsafe shell commands (exec, eval, subprocess with user-controlled input)
3. SQL or command injection patterns
4. Unvalidated external input at API or file-read boundaries

Return a structured report with three sections:
- CRITICAL: must fix before release
- HIGH: should fix this sprint
- INFORMATIONAL: notes for future improvement

If no issues in a category, write 'None found.' Do not skip the section."
})
```

Wait for the result. If the sub-agent errors, surface the error and stop — do not proceed with a partial report.

### Step 3: Launch dependency sub-agent

```
Agent({
  description: "Dependency audit — outdated, deprecated, or vulnerable packages",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "You are a dependency auditor. Examine the package manifest at <ROOT_DIR>.

For each dependency:
1. Is a newer minor or patch version available?
2. Are there known CVEs in the lock file or audit output?
3. Has the package had no releases in 12+ months with no deprecation notice?

Return a structured report with three sections:
- Outdated (semver bump available)
- Vulnerable (known CVE or audit flag)
- Stale (no updates in 12 months, no deprecation notice)

If no issues in a category, write 'None found.' Do not skip the section."
})
```

Wait for the result before proceeding.

### Step 4: Synthesize

Combine the two sub-agent outputs:

```
# Codebase Health Report
Generated: <timestamp>
Root: <ROOT_DIR>

## Executive Summary
[2–3 sentences on overall health based on both reports]

## Security Findings
[Security sub-agent output, formatted]

## Dependency Findings
[Dependency sub-agent output, formatted]

## Recommended Actions
[Top 3–5 actions ranked by severity, drawn from both reports]
```

### Step 5: Present

- Inline summary: output the report directly.
- Write to file: save as `codebase-health-<YYYY-MM-DD>.md` at the root dir and present the file.

## Sub-agent guidelines

- **Be explicit about scope**: tell each sub-agent exactly which directory or files to examine — sub-agents share no context with the orchestrator.
- **Specify return format**: sub-agents cannot infer what structure you need; describe it fully in the prompt.
- **Choose model per task**: deep analysis (security) → Opus; structured retrieval (dependencies) → Sonnet.
- **Handle empty results**: if a sub-agent returns no findings, reflect "None found" in the report rather than omitting the section.
- **Gate after each launch**: check for errors before using the result in synthesis. A missing section is worse than a clear error message.
- **Do not retry silently**: if a sub-agent fails, tell the user what failed and ask whether to retry or skip that section.

## When to use this skill

- Before cutting a release branch
- Quarterly security reviews
- Onboarding a new codebase
- Preparing a tech-debt summary for stakeholders

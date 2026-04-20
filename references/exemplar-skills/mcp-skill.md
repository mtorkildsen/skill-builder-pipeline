---
name: github-pr-digest
description: Fetches open pull requests and their review status from GitHub, then produces a prioritized review queue. Use when you want to triage pending PRs, identify stale reviews, or prepare for a sprint review meeting.
---

# GitHub PR Digest

Fetch the open PR list from GitHub via the GitHub MCP server, classify each PR by review urgency, and output a ranked queue.

**Prerequisite:** The GitHub MCP server must be connected. Confirm by checking available tools before starting — if `mcp__github__list_pull_requests` is not listed, this skill cannot retrieve live data.

## Workflow

### Step 1: Confirm parameters

Ask:
1. Repository? (format: `owner/repo`, e.g. `acme/api-server`)
2. Filter by author or label? (default: all open PRs)
3. How many PRs to include? (default: 20, max: 50)

Confirm before calling any MCP tools.

### Step 2: Verify MCP connectivity

Before fetching data, check that the GitHub MCP tools are available in the current session. If not:
- Tell the user: "GitHub MCP is not connected. I cannot fetch live PR data."
- Offer to analyze a PR list the user pastes manually.
- Do not attempt to substitute `gh` CLI without first confirming the user has it installed.

### Step 3: Fetch open PRs

```
mcp__github__list_pull_requests({
  owner: <owner>,
  repo: <repo>,
  state: "open",
  per_page: <count>
})
```

Handle errors explicitly:
- **401 Unauthorized** → tell the user their GitHub token is missing or expired.
- **404 Not Found** → confirm the repo name with the user.
- **Any other error** → surface the raw error message and stop. Do not guess at the cause.

### Step 4: Fetch review status per PR

For each PR, call:

```
mcp__github__get_pull_request_reviews({
  owner: <owner>,
  repo: <repo>,
  pull_number: <pr.number>
})
```

Collect: review state (`APPROVED` / `CHANGES_REQUESTED` / `COMMENTED` / `PENDING`), reviewer names, and last-activity timestamp.

Note: if you are fetching more than 20 PRs, space out the calls — do not fire all review fetches simultaneously.

### Step 5: Rank and format

Classify each PR into one category (use the first that applies):

1. **Needs action** — has `CHANGES_REQUESTED` and the author has not pushed a new commit since
2. **Ready to merge** — all assigned reviews are `APPROVED`, no open comment threads
3. **Awaiting review** — no reviewers assigned or no reviews submitted yet
4. **Stale** — no activity in 7+ days regardless of review state

Output:

```
## PR Review Queue — <owner>/<repo>
Generated: <timestamp>

### Needs Action (<n> PRs)
| # | Title | Author | Last Activity | Blocker |
|---|-------|--------|---------------|---------|

### Ready to Merge (<n> PRs)
| # | Title | Author | Approvers |
|---|-------|--------|-----------|

### Awaiting Review (<n> PRs)
| # | Title | Author | Days Open |
|---|-------|--------|-----------|

### Stale (<n> PRs)
| # | Title | Author | Last Activity |
|---|-------|--------|---------------|
```

### Step 6: Present

- Default: output the table inline.
- If the user asked for a file: write to `pr-digest-<YYYY-MM-DD>.md` and present the file.

## MCP tool guidelines

- **Check connectivity first**: MCP servers can disconnect between sessions. Always verify the tool is available before the workflow depends on it.
- **Handle every error case**: auth failures, rate limits, and 404s each need a different user message. Do not display a generic error and stop.
- **Never fabricate data**: if a field is missing from the MCP response (e.g., no reviewers assigned), write "none assigned" — do not infer or fill in.
- **Sequential calls when dependent**: fetch the PR list before fetching reviews per PR. Do not attempt parallel MCP calls unless you confirm the server supports concurrent requests.
- **Distinguish MCP from Bash**: use MCP tools for API calls; use Bash only for local file or git operations. Do not substitute one for the other.
- **Respect pagination**: if the server returns a `next_page` cursor and the user requested more than the page size, fetch the next page — do not silently truncate.

## When to use this skill

- Pre-sprint review meetings to triage the PR queue
- Weekly PR health checks
- When preparing a "what's blocked" summary for the team
- When assigning reviewers systematically across a large backlog

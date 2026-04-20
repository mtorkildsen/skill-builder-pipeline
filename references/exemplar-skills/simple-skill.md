---
name: code-review
description: Reviews code for bugs, performance issues, and best practices. Use when you want to analyze code quality, check for regressions, suggest improvements, or get architectural feedback on changes.
---

# Code Review

Review code systematically to identify bugs, performance problems, and improvement opportunities.

## Review methodology

When reviewing code, follow this structured approach:

1. **Analyze the code structure**: Check organization, naming clarity, and function size
2. **Identify potential bugs**: Look for edge cases, null pointer risks, and off-by-one errors
3. **Check performance**: Spot unnecessary loops, inefficient queries, and memory issues
4. **Verify best practices**: Confirm adherence to patterns, error handling, and testing
5. **Suggest improvements**: Provide specific refactoring recommendations with examples

## Guidelines for your analysis

- **Be specific**: Don't say "make this clearer" — show exactly what to change
- **Prioritize issues**: Separate critical bugs from nice-to-have improvements
- **Show examples**: When suggesting a change, include before/after code samples
- **Explain the why**: Connect each issue to a concrete problem (performance, maintainability, correctness)
- **Test your recommendations**: Verify suggested changes compile and behave correctly

## Review focus areas

### Correctness
Check for logic errors, boundary conditions, and error handling:
- Does the code handle empty inputs?
- Are all error paths covered?
- Do loops have proper termination conditions?

### Performance
Identify inefficient patterns:
- O(n²) algorithms where O(n) is feasible
- Redundant database queries in loops
- Unnecessary memory allocations

### Maintainability
Assess clarity and consistency:
- Function names accurately describe behavior
- Complex logic is documented
- Naming is consistent throughout the file

### Testing
Verify coverage of critical paths:
- Edge cases are covered
- Error conditions are tested
- Integration points are validated

## Output format

Organize your review as:

```
## Summary
[One-paragraph overview of code health and key findings]

## Critical Issues (must fix)
- [Issue 1 with specific location and fix]
- [Issue 2 with specific location and fix]

## Minor Issues (should fix)
- [Issue 1 with explanation]
- [Issue 2 with explanation]

## Suggestions (nice to have)
- [Suggestion 1 with benefit]
- [Suggestion 2 with benefit]

## Code samples
[Before/after examples for the top 2-3 recommendations]
```

## When to use this skill

Invoke this skill when you:
- Want a fresh perspective on recent changes
- Need to verify code quality before merging
- Are preparing for a PR review
- Want to identify technical debt
- Need to check a peer's contribution

The skill works best when you provide the code directly or reference the files to review.

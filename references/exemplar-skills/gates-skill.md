---
name: deploy-to-production
description: Safely deploys the application to production after running tests and building. Use only when you are ready to deploy—invoke with /deploy-to-production to start the deployment workflow.
disable-model-invocation: true
context: fork
agent: Plan
allowed-tools: Bash(npm test) Bash(npm run build) Bash(git status) Bash(npm run deploy)
---

# Deploy to Production

Deploy your application to production with safety checks and verification steps.

**WARNING:** This skill modifies your production environment. It can only be invoked manually with `/deploy-to-production`. Claude cannot trigger it automatically to prevent accidental deployments.

## Deployment workflow

Follow this sequence exactly. Do not skip steps:

### Step 1: Verify readiness
```bash
git status
```

Check:
- [ ] Working directory is clean
- [ ] All changes are committed
- [ ] No uncommitted files remain

If uncommitted files exist, STOP. Commit changes first and re-invoke this skill.

### Step 2: Run test suite
```bash
npm test
```

Requirements:
- [ ] All tests MUST pass
- [ ] No test warnings or failures
- [ ] Coverage targets MUST be met

If tests fail, STOP. Fix failures, commit, and re-invoke. Do not proceed with failing tests.

### Step 3: Build application
```bash
npm run build
```

Verify:
- [ ] Build completes without errors
- [ ] No compiler warnings in output
- [ ] Build artifacts are generated
- [ ] Bundle size is within acceptable range

If build fails, STOP. Fix issues and retry.

### Step 4: Execute deployment
```bash
npm run deploy
```

Monitor:
- [ ] Deployment begins successfully
- [ ] All services transition smoothly
- [ ] No errors in deployment logs

### Step 5: Verify production
```bash
curl https://your-production-domain.com/health
```

Confirm:
- [ ] Health endpoint returns 200 OK
- [ ] Application responds correctly
- [ ] Critical functionality works

If verification fails, trigger automatic rollback immediately.

## Safety constraints

**MANDATORY rules (non-negotiable):**

1. ALWAYS run tests first—never skip this step
2. NEVER deploy with uncommitted changes
3. NEVER proceed if any test fails
4. NEVER ignore build errors or warnings
5. ALWAYS verify production health after deployment

Breaking these rules creates production incidents.

## Rollback procedure

If production verification fails:

```bash
# Immediately revert to previous version
npm run rollback-production
```

Then:
1. Investigate the failure
2. Fix the root cause
3. Commit the fix
4. Re-invoke `/deploy-to-production`

## Communication protocol

After successful deployment:

Report deployment completion with:
- Deployment timestamp
- Git commit SHA deployed
- All verification checks passed
- Time to production (from start to finish)

Example report:
```
Deployment successful

Commit: abc1234567890def
Time: 2026-04-09 14:32:00 UTC
Duration: 4 minutes 23 seconds

All checks passed:
✓ Tests: 147 passed
✓ Build: Production bundle generated (2.3MB)
✓ Production: Health check 200 OK
✓ Critical path: All endpoints responding
```

## When to deploy

Use this skill when:
- All features are complete and tested
- Code review is finished
- All team sign-offs are obtained
- No known critical bugs remain
- Deployment window is open (business hours recommended)

## When NOT to deploy

Do not invoke this skill if:
- Tests are failing
- Code review comments remain unaddressed
- Recent changes have not been tested in staging
- It's outside the deployment window
- Team members request a hold
- Production is already experiencing issues

## Monitoring

After deployment, monitor:
- Error logs: Check for new errors
- Performance: Verify response times
- Database: Check query performance
- User reports: Watch support channels

If issues appear within 5 minutes, rollback immediately.

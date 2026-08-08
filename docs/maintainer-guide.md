# Maintainer guide

This guide is an operating checklist, not a requirement to respond instantly. Set sustainable expectations and prefer a smaller accurate dataset over rapid growth.

## Initial GitHub setup

After the first push:

1. Use `main` as the default branch.
2. Create the labels listed below; Issue Forms cannot create missing labels.
3. Enable Issues and private vulnerability reporting.
4. Add a branch ruleset for `main` requiring a pull request and the `validate` check.
5. Require one approval and resolution of review conversations.
6. Block force pushes and deletion of `main`.
7. Leave Actions with read-only default permissions unless a future workflow has a documented need for more.
8. Enable Dependabot security updates.

Do not require branches to be current until merge conflicts or stale checks become a real problem; it creates unnecessary contributor work.

## Suggested labels

- `submission` — proposed new opportunity
- `correction` — factual correction
- `data-update` — dates, eligibility, or benefits changed
- `broken-link` — URL needs manual confirmation
- `lifecycle` — paused, discontinued, archived, or unknown
- `needs-triage` — not yet reviewed
- `needs-verification` — evidence is missing, old, or inconclusive
- `duplicate` — already represented
- `invalid` — outside scope or insufficient information
- `good-first-issue` — suitable for a new contributor

## Issue triage

1. Check whether the submission is in scope.
2. Search by program name, organization, and normalized official URL.
3. Open the supplied source; distinguish application closure from discontinuation.
4. Ask focused follow-up questions when required facts are missing.
5. Apply labels and either close with a reason or mark it ready for a data pull request.

Closing a submission is an editorial decision, not a judgment about the contributor. Be brief and cite the policy.

## Pull request review

Review the diff and automated checks, then verify:

- The record has a stable, sensible ID and filename.
- The official source supports the name, organization, eligibility, dates, and benefits.
- Dates are announced rather than inferred.
- Geography describes applicant eligibility.
- Material fees and equity terms are visible.
- The description is neutral and is not copied marketing text.
- `last_verified` matches a genuine source review.
- No existing record represents the same program.

Request changes when necessary. Use squash merge so a contribution becomes one understandable commit. Link the pull request to its issue with `Closes #123` when appropriate.

## Link and freshness reports

The weekly maintenance workflow is advisory. A failed request may be bot blocking or a temporary outage. Confirm failures manually before editing a record. Never update `last_verified` because an automated request succeeded.

When a recurring record is near its usual opening month but has no announced cycle, look for a current official announcement. If none exists, leave its past dates intact and make uncertainty visible in `notes` if useful.

## Corrections and reversions

Correct ordinary mistakes with another pull request. If a merged change is dangerous or seriously misleading, revert its merge commit promptly and investigate afterward. Do not rewrite public history.

## Adding maintainers later

Start by granting triage access, which permits issue and pull-request organization without merge authority. Promote contributors to write/maintain access only after a consistent history of accurate reviews.

Category maintainers can be documented in a future `MAINTAINERS.md` and assigned through more specific `CODEOWNERS` patterns if the dataset is divided into category folders. Do not reorganize files solely to create roles before scale requires it.


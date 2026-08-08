# Maintenance policy

## Trust model

Automation catches malformed or suspicious data; maintainers establish truth. No automated link result, scraped page, or date calculation should silently change a factual record.

## Verification freshness

- 0–180 days: recently verified
- 181–365 days: verification aging
- More than 365 days: needs verification
- Recurring programs approaching a typical opening month without a current cycle: priority review

Rechecking a source may update `last_verified` even when no other field changes. The pull request should say what was checked.

## Expiration and archiving

A passed deadline does not make a recurring program discontinued. Preserve completed cycles and add the next announced cycle when available.

Mark an entry `discontinued` only when an official source or strong evidence supports that conclusion. Use `unknown` when pages disappear but discontinuation is not confirmed. Records are retained rather than deleted unless they are duplicates, fraudulent, dangerous, or contain material that should never have been committed.

## Link checking

The scheduled checker probes official, application, and verification URLs. One failure is not evidence that a program ended. Bot blocking, rate limits, and temporary outages are common.

- Redirects are accepted and reported for review.
- `401`, `403`, and `429` are warnings, not broken-link failures.
- Confirm repeated failures manually before changing lifecycle state.
- The checker never edits opportunity files.

## Duplicate policy

Exact IDs, normalized official URLs, and highly similar organization/name pairs are flagged. Similarity warnings require human judgment because programs may have multiple tracks or regional editions. Merge true duplicates under the older stable ID and preserve useful aliases or notes.

## Maintainer rhythm

- Review new issues and pull requests weekly when practical.
- Review automated link reports weekly.
- Review stale records monthly, prioritizing programs near their usual application period.
- Revisit controlled taxonomies periodically; avoid adding values for one-off wording differences.


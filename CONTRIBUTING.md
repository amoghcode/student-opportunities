# Contributing

Thank you for helping students find trustworthy opportunities. Accuracy is more important than collection size.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Choose a contribution path

### No Git experience required

Open an issue using the closest form:

- **Submit an opportunity** for a new record
- **Report outdated information** for dates or eligibility that changed
- **Report a broken link** when an official page no longer works
- **Report a discontinued opportunity** when a program appears to have ended
- **Suggest a correction** for anything else

Provide an official source whenever possible. An issue is a proposal, not a published record. A maintainer or volunteer will verify it and prepare a pull request.

### Edit the dataset directly

1. Search `opportunities/` and open issues for duplicates.
2. Copy [`opportunities/_template.yml`](opportunities/_template.yml).
3. Rename it to a stable lowercase slug such as `example-research-fellowship.yml`.
4. Fill in the fields using [`docs/data-model.md`](docs/data-model.md).
5. Run `python scripts/validate_data.py` if working locally.
6. Open a pull request and complete its checklist.

One pull request should normally add or update one opportunity. Small groups of closely related mechanical updates are acceptable.

## Evidence standard

Prefer sources in this order:

1. Official application or program page
2. Official organization announcement or documentation
3. Official social account, only when no durable page exists
4. Reputable secondary source, clearly identified as secondary

Do not use search-result snippets, AI-generated text, affiliate pages, or another directory as the only evidence. Do not copy long descriptions from official websites; summarize facts neutrally.

`last_verified` means a person checked the cited source on that date. Do not update it merely to silence a stale-data warning.

## Writing and data rules

- Use ISO dates: `YYYY-MM-DD`.
- Do not predict a future deadline by adding one year to an old deadline.
- Put uncertain details in `notes` and explain the uncertainty.
- Use only values from `data/taxonomies.yml` for controlled fields.
- Use the canonical official URL without tracking or referral parameters.
- State fees, equity requirements, and important restrictions plainly.
- Distinguish applicant eligibility geography from the location where the
  program takes place.
- Use `required: null` for an application fee that could not be confirmed;
  absence of fee information is not proof that applying is free.
- When recording one numeric benefit amount, specify whether it is a stipend,
  prize, grant, or reimbursement and whether it is total, monthly, or another
  frequency.
- Keep descriptions factual, concise, and free of marketing language.
- Never add personal phone numbers, private email addresses, or sensitive applicant data.

## Review process

Automated checks validate structure, controlled values, dates, duplicates, and tests. Passing checks do not prove an opportunity is legitimate. A maintainer also reviews sources and editorial quality.

A reviewer may request clarification or changes. Once checks pass and the evidence is adequate, a maintainer squash-merges the pull request. The dataset is then ready for downstream tools to consume.

## Licensing

By submitting a contribution, you agree that code contributions may be distributed under MIT and dataset/documentation contributions under CC BY 4.0.

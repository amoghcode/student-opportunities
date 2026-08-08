# Opportunity data model

The canonical dataset is the collection of YAML files in `opportunities/`. There is no manually stored `open` or `closed` status: consumers derive those labels from schedule data and the current date.

## Identity and summary

- `id` — Permanent lowercase identifier. Never reuse or change it merely because a program is renamed.
- `name`, `organization` — Official names, without promotional slogans.
- `categories` — One or more controlled values from `data/taxonomies.yml`.
- `official_url` — Durable official program page. Remove tracking parameters.
- `application_url` — Optional direct application URL.
- `description` — Original neutral summary, not copied marketing text.

## Audience and location

- `geographies` — Eligibility geography, not merely event location. `global` uses an empty `values` list; `country`, `region`, `city`, and `institution` name their values.
- `delivery` — How participation occurs.
- `student_levels` — Controlled values. Use `any-student` only when the source genuinely accepts all students.
- `fields` — Human-readable study/industry fields. Keep terminology broad and consistent.
- `eligibility_summary` — Important qualifications that do not fit controlled fields.
- `tags` — Lowercase slugs. Prefer existing tags before inventing another synonym.

## Benefits

`benefits.summary` describes funding, prizes, mentorship, travel, or other support. Use `amount` and three-letter ISO `currency` only for one unambiguous amount. Otherwise explain ranges in the summary. `equity_required` may be `null` when it is not known or not relevant.

## Schedule

`schedule.type` is one of:

- `fixed` — A one-off or explicitly dated application period
- `recurring` — Repeats, usually annually or in cohorts
- `rolling` — Applications are accepted without a fixed closing date
- `unknown` — The source does not establish a reliable pattern

Each known cycle has a human-readable `label`, plus nullable `opens_on` and `deadline`. Record announced dates only. Never project next year's dates from an earlier cycle.

`typical_open_months` and `typical_close_months` describe an observed recurring pattern. They support wording such as “usually opens in January”; they are not deadlines.

## Lifecycle and verification

- `active` — The program exists, even if applications are currently closed.
- `paused` — The organization explicitly paused it or no cohort is currently planned.
- `discontinued` — Reliable evidence says the program ended.
- `archived` — Retained primarily for historical value.
- `unknown` — Existence cannot currently be confirmed.

Use `lifecycle_note` and `discontinued_on` where relevant. Do not delete discontinued records: historical pages and links may remain useful.

`last_verified` is the most recent date a human reviewed the record against its sources. Every item in `verification_sources` records its own access date and source kind.

## Derived status recommendation

Future consumers should apply this order:

1. Discontinued or archived lifecycle
2. Rolling schedule
3. Between opening and deadline: open now
4. Open with deadline within 14 days: closing soon
5. Opening within 45 days: opening soon
6. No announced cycle but a typical month: usually opens in that month
7. Otherwise: dates unconfirmed

Verification freshness is a separate warning. A calculated “open now” entry can also be marked “needs verification.”


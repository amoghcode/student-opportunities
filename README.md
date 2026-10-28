# Student Opportunities

An open, community-maintained dataset of useful opportunities for students.

[Explore the live directory](https://amoghcode.github.io/student-opportunities/) ·
[Release v0.1.0](https://github.com/amoghcode/student-opportunities/releases/tag/v0.1.0) ·
[Suggest an opportunity](https://github.com/amoghcode/student-opportunities/issues/new/choose)

This repository is intentionally **data-first**. The YAML files are the canonical collection and power a simple searchable website, with room to support other tools later without changing the source data.

## What belongs here

- Grants, accelerators, incubators, and student-founder programs
- Hackathons, competitions, and open-source programs
- Fellowships, research programs, internships, and scholarships
- Conference/travel grants and other selective student programs

An entry must have an official source, clear student relevance, and enough information for someone to decide whether to investigate it. Promotional copy, referral links, unverifiable claims, and ordinary paid courses do not belong.

## How the dataset works

- Each opportunity is one YAML file in [`opportunities/`](opportunities/).
- [`schema/opportunity.schema.json`](schema/opportunity.schema.json) defines the machine-readable rules.
- [`data/taxonomies.yml`](data/taxonomies.yml) contains approved categories and controlled values.
- Dates and lifecycle facts are stored; temporary labels such as "Open now" are calculated later.
- Every accepted entry includes a verification date and at least one source.
- Changes are proposed through issues or pull requests and reviewed before merging.

Read [`docs/data-model.md`](docs/data-model.md) for field definitions, [`docs/maintenance-policy.md`](docs/maintenance-policy.md) for expiration and verification policy, and [`docs/maintainer-guide.md`](docs/maintainer-guide.md) for day-to-day GitHub operations.

## Search the directory

The [live directory](https://amoghcode.github.io/student-opportunities/) searches
the same YAML records maintained
in `opportunities/`; the generated JSON file is rebuilt and is not edited by
hand. Search by keyword, then filter by opportunity type, study level, subject,
eligibility geography, delivery format, or application timing. Application
status is derived from recorded dates. If an opening date is unknown, the site
does not claim that applications are open.

To preview the website on your computer from the repository folder:

```bash
python -m pip install -e .
python scripts/validate_data.py
python scripts/build_site_data.py
python -m http.server 8000 --directory site
```

Then open `http://localhost:8000` in your browser. Keep the terminal window open
while viewing the page; press `Ctrl+C` there when you are done.

The [website workflow](.github/workflows/deploy-site.yml) rebuilds the data and
deploys the site to GitHub Pages when relevant changes are merged into `main`.
Pull requests affecting the site or dataset build a preview artifact without
publishing. For your own fork, enable publishing in **Settings → Pages** by
choosing **GitHub Actions** as the source.

## Contributing

You do not need to know Git.

- Use **Submit an opportunity** in the issue chooser to suggest a new entry.
- Use one of the report forms to flag a correction, broken link, or discontinued program.
- If you are comfortable editing YAML, follow [`CONTRIBUTING.md`](CONTRIBUTING.md) and open a pull request.

## Local validation

Requires Python 3.11 or later.

```bash
python -m pip install -e ".[dev]"
python scripts/validate_data.py
python -m unittest discover -s tests
node --test tests/site.test.cjs
```

The website behavior tests require Node.js 22 or later and use its built-in test
runner; there are no npm dependencies.

Link checks are deliberately separate because they use the network:

```bash
python scripts/check_links.py
```

## Project status

As of October 28, 2026:

- **Released:** [v0.1.0](https://github.com/amoghcode/student-opportunities/releases/tag/v0.1.0)
  was published on October 22, 2026. The release is a versioned snapshot;
  `main` and the live website continue to receive updates.
- **Live:** the searchable directory contains 35 curated opportunities across
  scholarships, research, internships, open source, competitions, and
  student-founder support. The website theme was updated after the initial
  release.
- **Validated and deployed:** the latest dataset validation and website
  deployment passed on October 27, 2026. See
  [GitHub Actions](https://github.com/amoghcode/student-opportunities/actions)
  for current results.
- **Maintained through pull requests:** `main` is protected. The schema,
  automated tests, contribution forms, and weekly maintenance workflow are in
  place; YAML files remain the canonical records.

### Known limitations and maintenance

The latest scheduled maintenance run, on October 26, 2026, failed. Automated
link checks can encounter certificate errors, server refusals, or access
restrictions even when a page loads in a browser. Manual verification and
automated reachability are tracked separately; a failed check alone does not
mean that a programme has ended. See the
[October 22 link-audit follow-up](docs/link-audit-2026-10-22.md) for the earlier
findings and manual review, and the workflow logs for subsequent results.

Application-cycle updates and link reviews remain ongoing. Verification dates
are recorded per entry; inclusion in the directory does not mean applications
are currently open. Confirm eligibility, funding, and deadlines on the official
programme pages before applying.

## Licenses

Source code is available under the [MIT License](LICENSE). Dataset contents are available under [CC BY 4.0](DATA_LICENSE.md). Contributors agree to license their accepted contributions on those terms.

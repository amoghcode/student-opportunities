# Student Opportunities

An open, community-maintained dataset of useful opportunities for students.

This repository is intentionally **data-first**. It does not contain a website yet. The current goal is to establish a reliable collection that can later power a website, API, newsletter, or other tools without changing the source data.

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
```

Link checks are deliberately separate because they use the network:

```bash
python scripts/check_links.py
```

## Project status

Foundation stage. The schema and contribution process are ready for an initial curated set. A public website should be added only after the repository contains enough reviewed records to test the information architecture properly.

## Licenses

Source code is available under the [MIT License](LICENSE). Dataset contents are available under [CC BY 4.0](DATA_LICENSE.md). Contributors agree to license their accepted contributions on those terms.

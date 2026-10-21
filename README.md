# Student Opportunities

An open, community-maintained dataset of useful opportunities for students.

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

The simple website in [`site/`](site/) searches the same YAML records maintained
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

The website workflow rebuilds the data and deploys the site to GitHub Pages
after changes are merged into `main`. To enable publishing, open the repository's
**Settings → Pages** page and choose **GitHub Actions** as the source. The site
can then be reached at `https://amoghcode.github.io/student-opportunities/`.

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

The repository is a community-maintained dataset with a searchable website
ready to deploy through GitHub Pages. The YAML files remain the canonical
records; the website helps students find them and sends them to official
program pages to confirm details. The first versioned release is a separate
maintainer step after the final review.

## Licenses

Source code is available under the [MIT License](LICENSE). Dataset contents are available under [CC BY 4.0](DATA_LICENSE.md). Contributors agree to license their accepted contributions on those terms.

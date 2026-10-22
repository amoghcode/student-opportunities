# Link audit follow-up: October 22, 2026

The [PR maintenance run](https://github.com/amoghcode/student-opportunities/actions/runs/39720417086)
checked 74 URLs and reported 10 failures. The freshness audit found zero stale
records and six priority cycle reviews. Dataset validation and the website build
passed; 19 Python tests and six JavaScript behavior tests passed.

## Automated failures at the time of the run

| Program | URLs | GitHub Linux runner result |
| --- | --- | --- |
| EPFL Excellence in Engineering | `https://eee.epfl.ch/`, `/apply/`, `/faq/`, `/selection-criteria/` | Connection closed without an HTTP response |
| NIDHI-PRAYAS | `https://nidhi.dst.gov.in/`, `/prayas2-0/` | Certificate expired |
| ISTA Scientific Internship | `https://phd.ista.ac.at/funding-and-awards/`, `https://phd.pages.ista.ac.at/scientific-internships/` | HTTP 503 Service Unavailable |
| NASA Space Apps | `https://www.spaceappschallenge.org/`, `/legal/` | Certificate chain could not be verified |

The local Windows audit also completed all 74 URLs, with six failures: the four
EPFL URLs closed their connections, while the two ISTA URLs failed certificate
verification. NIDHI and Space Apps passed locally. These differences mean a
successful local request is insufficient to close the GitHub maintenance alert.
An additional EPFL GET request also closed without a response.

## Source checks

Official-source search results still describe the programs:

- [EPFL's October 12 announcement](https://actu.epfl.ch/news/apply-to-the-e3-epfl-excellence-in-engineering-p-6/)
  describes the 2027 program and November 1 application deadline.
- [ISTA careers](https://www.ista.ac.at/en/jobs/careers-in-science/)
  links its year-round scientific internships separately from the paused seasonal
  ISTernship program.
- [NIDHI's PRAYAS 2.0 page](https://nidhi.dst.gov.in/prayas2-0/)
  describes the current prototype-support program.
- [NASA's October 15 announcement](https://science.nasa.gov/universe/nasa-welcomes-all-ages-experience-levels-for-space-apps-challenge/)
  describes the November 14–15 Space Apps event.

These checks corroborate program existence; they do not reverify every field or
prove that each recorded URL is reachable from all clients. No lifecycle,
deadline, or record-level `last_verified` fields were changed during this audit.

## Maintainer manual review: October 22

The maintainer reported that the following supplied URLs load successfully in
their browser. This is evidence of manual reachability, separate from the
automated results above.

| Supplied URL | Review outcome |
| --- | --- |
| `https://www.epfl.ch/education/international/en/coming-to-epfl/research-internships/` | Loads, but describes ERIP, not the recorded E3 program. It does not close the four E3 URL failures. |
| `https://ista.ac.at/en/education/internship-and-scholarship/` | Loads and links the recorded year-round scientific internship. Added as a supporting source. |
| `https://phd.pages.ista.ac.at/scientific-internships/` | Maintainer confirmed reachability; content was independently retrieved during review. Tracking parameters omitted. |
| `https://www.spaceappschallenge.org/` | Maintainer confirmed homepage reachability; automated retrieval still timed out during review. The separate `/legal/` URL was not included in this manual check. |
| `https://nidhi-prayas.org/` | Maintainer confirmed reachability; content independently retrieved. This PMU site is now the listing's official link, with its innovator page added as a supporting source. |

[EPFL's eligibility page](https://www.epfl.ch/education/international/en/coming-to-epfl/research-internships/eligibility-and-application/)
restricts ERIP to partner institutions in North America and Singapore and
explicitly lists E3 as another program with distinct eligibility. Keep the
existing E3 record and URLs; adding ERIP would require a separate opportunity
record and eligibility review.

The [ISTA landing page](https://ista.ac.at/en/education/internship-and-scholarship/)
links the year-round scientific internship. The
[NIDHI PMU site](https://nidhi-prayas.org/) identifies its DST program and SINE,
IIT Bombay management. Neither supplied landing page proves that the older
ISTA funding URL or the two DST-hosted NIDHI URLs now pass automated checks.
Those source URLs remain recorded and monitored.

Only source access dates and the NIDHI official link were updated. Record-level
verification dates remain unchanged because this was a link review, not a full
reverification of eligibility, funding, and application cycles.

## Follow-up

The checker now reports interrupted connections and continues auditing other
URLs instead of crashing. Certificate verification remains enabled, and genuine
HTTP and TLS failures continue to fail the maintenance workflow. Changes to the
checker or maintenance workflow run the audit on pull requests as well as on
the weekly schedule.

Recheck the failing URLs after the server/certificate problems are corrected.
Replace a URL only when an official source establishes its replacement. The
website PR was initially kept in draft while these alerts were unresolved; it
has since been merged with the external maintenance issues tracked separately.

Review the six approaching application cycles separately: CERN openlab, EPFL
Excellence in Engineering, EPFL Life Sciences, Erasmus Mundus, ETH Zurich, and
Technovation Girls. A freshness priority flag alone does not justify inferring
an opening date.

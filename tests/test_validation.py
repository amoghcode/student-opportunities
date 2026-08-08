from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_data import ROOT, Record, custom_errors, load_yaml, normalize_name, normalize_url


class NormalizationTests(unittest.TestCase):
    def test_url_removes_tracking_and_www(self):
        self.assertEqual(
            normalize_url("https://www.example.org/program/?utm_source=newsletter"),
            "https://example.org/program",
        )

    def test_name_normalization(self):
        self.assertEqual(normalize_name("ACME's AI-Fellowship!"), "acme s ai fellowship")


class TemplateTests(unittest.TestCase):
    def test_template_matches_schema_and_taxonomies(self):
        schema = json.loads((ROOT / "schema/opportunity.schema.json").read_text(encoding="utf-8"))
        template_path = ROOT / "opportunities/_template.yml"
        template = load_yaml(template_path)
        schema_errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(template))
        taxonomies = load_yaml(ROOT / "data/taxonomies.yml")
        self.assertEqual(schema_errors, [])
        self.assertEqual(custom_errors(Record(template_path, template), taxonomies), [])


if __name__ == "__main__":
    unittest.main()

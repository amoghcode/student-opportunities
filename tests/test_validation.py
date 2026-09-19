from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_data import ROOT, Record, custom_errors, load_yaml, normalize_name, normalize_url, validate


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


class CustomValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_path = ROOT / "opportunities/_template.yml"
        cls.template = load_yaml(cls.template_path)
        cls.taxonomies = load_yaml(ROOT / "data/taxonomies.yml")

    def errors_for(self, changes=None):
        data = deepcopy(self.template)
        if changes:
            changes(data)
        return custom_errors(Record(self.template_path, data), self.taxonomies)

    def test_controlled_value_error_suggests_canonical_value(self):
        errors = self.errors_for(lambda data: data.update(categories=["student-founder-program"]))
        self.assertTrue(any("did you mean 'student-founder'" in error for error in errors))

    def test_eligibility_basis_and_program_location_are_independent(self):
        def change(data):
            data["eligibility_geographies"] = [{"scope": "country", "basis": "nationality", "values": ["India"]}]
            data["locations"] = [{"scope": "country", "values": ["France"]}]

        self.assertEqual(self.errors_for(change), [])

    def test_legacy_geographies_field_remains_compatible(self):
        def change(data):
            data["geographies"] = data.pop("eligibility_geographies")
            for geography in data["geographies"]:
                geography.pop("basis", None)

        data = deepcopy(self.template)
        change(data)
        schema = json.loads((ROOT / "schema/opportunity.schema.json").read_text(encoding="utf-8"))
        schema_errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data))
        self.assertEqual(schema_errors, [])
        self.assertEqual(custom_errors(Record(self.template_path, data), self.taxonomies), [])

    def test_eligibility_and_legacy_geographies_cannot_both_be_used(self):
        def change(data):
            data["geographies"] = deepcopy(data["eligibility_geographies"])

        errors = self.errors_for(change)
        self.assertIn(
            "use eligibility_geographies; do not include the deprecated geographies field as well",
            errors,
        )

    def test_location_scope_uses_controlled_values(self):
        def change(data):
            data["locations"] = [{"scope": "nation", "values": ["France"]}]

        errors = self.errors_for(change)
        self.assertTrue(any("locations[0].scope has unsupported value" in error for error in errors))

    def test_application_fee_requires_amount_and_currency_together(self):
        def change(data):
            data["application_fee"] = {
                "required": True,
                "amount": 50,
                "currency": None,
                "notes": None,
            }

        errors = self.errors_for(change)
        self.assertIn("application_fee amount and currency must either both be set or both be null", errors)

    def test_free_application_has_no_amount_or_currency(self):
        def change(data):
            data["application_fee"] = {
                "required": False,
                "amount": 0,
                "currency": "USD",
                "notes": "Free",
            }

        errors = self.errors_for(change)
        self.assertIn("application_fee amount and currency must be null when required is false", errors)

    def test_funding_metadata_must_be_complete(self):
        def change(data):
            data["benefits"].update(
                amount=1000,
                currency="USD",
                amount_type="stipend",
                amount_frequency=None,
                amount_qualifier="exact",
            )

        errors = self.errors_for(change)
        self.assertIn("benefits.amount_frequency is required when amount metadata is provided", errors)

    def test_future_verification_dates_are_rejected(self):
        def change(data):
            data["last_verified"] = "2999-01-01"
            data["verification_sources"][0]["accessed_on"] = "2999-01-01"

        errors = self.errors_for(change)
        self.assertIn("last_verified cannot be in the future", errors)
        self.assertIn("verification_sources[0].accessed_on cannot be in the future", errors)

    def test_deadline_time_requires_timezone(self):
        def change(data):
            data["schedule"]["timezone"] = None
            data["schedule"]["cycles"][0]["deadline_time"] = "17:00"

        errors = self.errors_for(change)
        self.assertIn("schedule.cycles[0] deadline_time requires schedule.timezone", errors)


class RepositoryValidationTests(unittest.TestCase):
    def test_filename_must_match_record_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schema").mkdir()
            (root / "data").mkdir()
            (root / "opportunities").mkdir()
            shutil.copy(ROOT / "schema/opportunity.schema.json", root / "schema/opportunity.schema.json")
            shutil.copy(ROOT / "data/taxonomies.yml", root / "data/taxonomies.yml")
            record = load_yaml(ROOT / "opportunities/_template.yml")
            (root / "opportunities/wrong-name.yml").write_text(
                yaml.safe_dump(record, sort_keys=False), encoding="utf-8"
            )

            errors, warnings = validate(root)

        self.assertEqual(warnings, [])
        self.assertTrue(any("filename must match id 'example-opportunity'" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

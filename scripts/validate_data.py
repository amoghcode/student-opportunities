#!/usr/bin/env python3
"""Validate opportunity YAML files and report likely duplicates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TRACKING_KEYS = {"fbclid", "gclid", "ref", "referrer", "source"}


@dataclass
class Record:
    path: Path
    data: dict


def normalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    port = f":{parts.port}" if parts.port else ""
    query = urlencode([
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS
    ])
    path = re.sub(r"/+", "/", parts.path).rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), host + port, path, query, ""))


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError("top level must be a mapping")
    return value


def unsupported_value(field: str, value: object, allowed: list[str]) -> str:
    suggestion = get_close_matches(value, allowed, n=1, cutoff=0.55) if isinstance(value, str) else []
    suffix = f"; did you mean {suggestion[0]!r}?" if suggestion else ""
    return f"{field} has unsupported value: {value!r}{suffix}"


def geography_errors(items: list[dict], field: str, taxonomies: dict, *, eligibility: bool) -> list[str]:
    errors: list[str] = []
    allowed_scopes = taxonomies["geography_scopes"]
    allowed_bases = taxonomies["eligibility_bases"]
    for index, geography in enumerate(items):
        scope = geography.get("scope")
        values = geography.get("values", [])
        if scope not in allowed_scopes:
            errors.append(unsupported_value(f"{field}[{index}].scope", scope, allowed_scopes))
        if eligibility:
            basis = geography.get("basis")
            if basis is not None and basis not in allowed_bases:
                errors.append(unsupported_value(f"{field}[{index}].basis", basis, allowed_bases))
        if scope == "global" and values:
            errors.append(f"{field}[{index}] global scope must have an empty values list")
        if scope not in {"global", "unspecified"} and not values:
            errors.append(f"{field}[{index}] {scope!r} scope requires at least one value")
    return errors


def custom_errors(record: Record, taxonomies: dict) -> list[str]:
    data = record.data
    errors: list[str] = []
    controlled = {
        "categories": "categories",
        "student_levels": "student_levels",
    }
    for field, taxonomy in controlled.items():
        for value in sorted(set(data.get(field, [])) - set(taxonomies[taxonomy])):
            errors.append(unsupported_value(field, value, taxonomies[taxonomy]))

    if data.get("delivery") not in taxonomies["delivery_modes"]:
        errors.append(unsupported_value("delivery", data.get("delivery"), taxonomies["delivery_modes"]))
    if data.get("lifecycle") not in taxonomies["lifecycle_values"]:
        errors.append(unsupported_value("lifecycle", data.get("lifecycle"), taxonomies["lifecycle_values"]))

    application_method = data.get("application_method")
    if application_method is not None and application_method not in taxonomies["application_methods"]:
        errors.append(unsupported_value("application_method", application_method, taxonomies["application_methods"]))

    application_fee = data.get("application_fee")
    if application_fee:
        fee_required = application_fee.get("required")
        fee_amount = application_fee.get("amount")
        fee_currency = application_fee.get("currency")
        if (fee_amount is None) != (fee_currency is None):
            errors.append("application_fee amount and currency must either both be set or both be null")
        if fee_required is False and (fee_amount is not None or fee_currency is not None):
            errors.append("application_fee amount and currency must be null when required is false")
        if fee_required is None and fee_amount is not None:
            errors.append("application_fee amount must be null when whether a fee is required is unknown")

    schedule = data.get("schedule", {})
    if schedule.get("type") not in taxonomies["schedule_types"]:
        errors.append(unsupported_value("schedule.type", schedule.get("type"), taxonomies["schedule_types"]))
    if schedule.get("type") == "fixed" and not schedule.get("cycles"):
        errors.append("a fixed schedule requires at least one cycle")
    if schedule.get("type") == "rolling" and any(c.get("deadline") for c in schedule.get("cycles", [])):
        errors.append("a rolling schedule should not contain a deadline; use fixed or recurring")

    if data.get("eligibility_geographies") is not None and data.get("geographies") is not None:
        errors.append("use eligibility_geographies; do not include the deprecated geographies field as well")
    eligibility_geographies = data.get("eligibility_geographies", data.get("geographies", []))
    errors.extend(
        geography_errors(eligibility_geographies, "eligibility_geographies", taxonomies, eligibility=True)
    )
    errors.extend(geography_errors(data.get("locations", []), "locations", taxonomies, eligibility=False))

    benefits = data.get("benefits", {})
    amount = benefits.get("amount")
    currency = benefits.get("currency")
    amount_fields = {
        "amount_type": "benefit_amount_types",
        "amount_frequency": "benefit_amount_frequencies",
        "amount_qualifier": "benefit_amount_qualifiers",
    }
    if (amount is None) != (currency is None):
        errors.append("benefits amount and currency must either both be set or both be null")
    metadata_present = any(benefits.get(field) is not None for field in amount_fields)
    if metadata_present and amount is None:
        errors.append("benefits amount metadata requires a numeric amount and currency")
    if metadata_present:
        for field, taxonomy in amount_fields.items():
            value = benefits.get(field)
            if value is None:
                errors.append(f"benefits.{field} is required when amount metadata is provided")
            elif value not in taxonomies[taxonomy]:
                errors.append(unsupported_value(f"benefits.{field}", value, taxonomies[taxonomy]))

    for index, cycle in enumerate(schedule.get("cycles", [])):
        opens = cycle.get("opens_on")
        deadline = cycle.get("deadline")
        if opens and deadline and date.fromisoformat(opens) > date.fromisoformat(deadline):
            errors.append(f"schedule.cycles[{index}] opens_on is after deadline")
        if cycle.get("deadline_time") and not schedule.get("timezone"):
            errors.append(f"schedule.cycles[{index}] deadline_time requires schedule.timezone")

    last_verified = data.get("last_verified")
    sources = data.get("verification_sources", [])
    if last_verified and sources:
        latest_source = max(source["accessed_on"] for source in sources if source.get("accessed_on"))
        if last_verified > latest_source:
            errors.append("last_verified is later than every verification source accessed_on date")
    today = date.today().isoformat()
    if last_verified and last_verified > today:
        errors.append("last_verified cannot be in the future")
    for index, source in enumerate(sources):
        if source.get("accessed_on") and source["accessed_on"] > today:
            errors.append(f"verification_sources[{index}].accessed_on cannot be in the future")

    if data.get("lifecycle") == "discontinued" and not data.get("lifecycle_note"):
        errors.append("discontinued records require lifecycle_note")
    if data.get("lifecycle") != "discontinued" and data.get("discontinued_on"):
        errors.append("discontinued_on is only valid when lifecycle is discontinued")
    return errors


def duplicate_messages(records: list[Record]) -> list[str]:
    messages: list[str] = []
    for i, left in enumerate(records):
        for right in records[i + 1:]:
            left_id, right_id = left.data["id"], right.data["id"]
            if left_id == right_id:
                messages.append(f"ERROR duplicate id {left_id!r}: {left.path.name}, {right.path.name}")
            if normalize_url(left.data["official_url"]) == normalize_url(right.data["official_url"]):
                messages.append(f"ERROR duplicate official URL: {left.path.name}, {right.path.name}")
            left_name = normalize_name(f"{left.data['organization']} {left.data['name']}")
            right_name = normalize_name(f"{right.data['organization']} {right.data['name']}")
            similarity = SequenceMatcher(None, left_name, right_name).ratio()
            if similarity >= 0.90 and left_id != right_id:
                messages.append(
                    f"WARNING possible duplicate ({similarity:.0%} similar): "
                    f"{left.path.name}, {right.path.name}"
                )
    return messages


def validate(root: Path = ROOT) -> tuple[list[str], list[str]]:
    schema = json.loads((root / "schema/opportunity.schema.json").read_text(encoding="utf-8"))
    taxonomies = load_yaml(root / "data/taxonomies.yml")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    warnings: list[str] = []
    records: list[Record] = []

    paths = sorted(p for p in (root / "opportunities").glob("*.yml") if not p.name.startswith("_"))
    for path in paths:
        try:
            record = Record(path, load_yaml(path))
        except (OSError, yaml.YAMLError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        records.append(record)
        if path.stem != record.data.get("id"):
            errors.append(
                f"{path.relative_to(root)}: filename must match id {record.data.get('id')!r}"
            )
        for error in sorted(validator.iter_errors(record.data), key=lambda e: list(e.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{path.relative_to(root)}:{location}: {error.message}")
        for error in custom_errors(record, taxonomies):
            errors.append(f"{path.relative_to(root)}: {error}")

    for message in duplicate_messages(records):
        if message.startswith("ERROR "):
            errors.append(message.removeprefix("ERROR "))
        else:
            warnings.append(message)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-warnings", action="store_true", help="fail on possible-duplicate warnings")
    args = parser.parse_args()
    errors, warnings = validate()
    for warning in warnings:
        print(warning)
    for error in errors:
        print(f"ERROR {error}")
    count = len([p for p in (ROOT / "opportunities").glob("*.yml") if not p.name.startswith("_")])
    if errors or (args.strict_warnings and warnings):
        print(f"Validation failed: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"Validated {count} opportunity file(s): {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

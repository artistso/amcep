import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "claims.schema.json"
LEDGER_PATH = ROOT / "data" / "claims.json"


def test_claim_ledger_matches_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(ledger), key=lambda error: list(error.path))
    assert not errors, "\n".join(
        f"{list(error.path)}: {error.message}" for error in errors
    )


def test_claim_ids_are_unique() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    claim_ids = [claim["claim_id"] for claim in ledger["claims"]]
    assert len(claim_ids) == len(set(claim_ids))


def test_verified_claims_require_formal_proof_artifact() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    for claim in ledger["claims"]:
        if claim["status"] != "formally-verified":
            continue
        kinds = {item["kind"] for item in claim["evidence"]}
        assert "formal-proof" in kinds, claim["claim_id"]


def test_empirical_claims_require_empirical_artifact() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    for claim in ledger["claims"]:
        if claim["status"] != "empirically-supported":
            continue
        kinds = {item["kind"] for item in claim["evidence"]}
        assert "empirical-study" in kinds, claim["claim_id"]

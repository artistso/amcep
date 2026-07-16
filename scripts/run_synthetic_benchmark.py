#!/usr/bin/env python3
"""Run the deterministic AMCEP synthetic benchmark and emit audit artifacts."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any

from src.synthetic_benchmark import (
    MODEL_NAMES,
    ScenarioResult,
    default_scenarios,
    evaluate_sweep,
)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _scenario_id(index: int, result: ScenarioResult) -> str:
    config = result.config
    return (
        f"{index:02d}-{config.regime}"
        f"-noise-{config.noise_std:g}"
        f"-missing-{config.missing_rate:g}"
        f"-adversarial-{config.adversarial_rate:g}"
    )


def _write_predictions(
    path: Path,
    results: tuple[ScenarioResult, ...],
) -> None:
    fieldnames = [
        "scenario_id",
        "case_id",
        "regime",
        "target",
        "true_rho",
        "true_operator_power",
        "true_x",
        "depth",
        "true_normalization",
        "observed_rho",
        "observed_operator_power",
        "observed_x",
        "observed_normalization",
        "adversarially_corrupted",
        "missing_field",
        *[f"prediction_{model}" for model in MODEL_NAMES],
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, result in enumerate(results):
            scenario_id = _scenario_id(index, result)
            for position, case in enumerate(result.cases):
                row: dict[str, object] = {
                    "scenario_id": scenario_id,
                    "case_id": case.case_id,
                    "regime": case.regime,
                    "target": case.target,
                    "true_rho": case.true_rho,
                    "true_operator_power": case.true_operator_power,
                    "true_x": case.true_x,
                    "depth": case.depth,
                    "true_normalization": case.true_normalization,
                    "observed_rho": case.observed_rho,
                    "observed_operator_power": case.observed_operator_power,
                    "observed_x": case.observed_x,
                    "observed_normalization": case.observed_normalization,
                    "adversarially_corrupted": case.adversarially_corrupted,
                    "missing_field": case.missing_field,
                }
                for model in MODEL_NAMES:
                    row[f"prediction_{model}"] = result.predictions[model][
                        position
                    ]
                writer.writerow(row)


def _write_checksums(output_dir: Path) -> None:
    lines: list[str] = []
    for path in sorted(output_dir.iterdir()):
        if not path.is_file() or path.name == "checksums.txt":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (output_dir / "checksums.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def run(output_dir: Path, sample_size: int, seed: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios = default_scenarios(sample_size=sample_size, seed=seed)
    results = evaluate_sweep(scenarios)

    parameters = [
        {
            "scenario_id": _scenario_id(index, result),
            **asdict(result.config),
        }
        for index, result in enumerate(results)
    ]
    metrics = [
        {
            "scenario_id": _scenario_id(index, result),
            "regime": result.config.regime,
            "noise_std": result.config.noise_std,
            "missing_rate": result.config.missing_rate,
            "adversarial_rate": result.config.adversarial_rate,
            **asdict(metric),
        }
        for index, result in enumerate(results)
        for metric in result.metrics
    ]

    _write_json(output_dir / "parameters.json", parameters)
    _write_json(output_dir / "metrics.json", metrics)
    _write_predictions(output_dir / "predictions.csv", results)

    manifest = {
        "schema_version": "1.0.0",
        "experiment_id": "amcep-synthetic-cross-regime-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "base_seed": seed,
        "sample_size_per_scenario": sample_size,
        "scenario_count": len(results),
        "model_names": list(MODEL_NAMES),
        "claims_under_test": [
            "AMCEP-MON-002",
            "AMCEP-CAN-001",
            "AMCEP-CAN-002",
            "AMCEP-CAN-003",
            "AMCEP-CAN-004",
        ],
        "interpretation_boundary": (
            "Synthetic results test implementation and structural behavior "
            "under declared data-generating regimes. They do not establish "
            "real-world validity or moral truth."
        ),
    }
    _write_json(output_dir / "manifest.json", manifest)

    environment = "\n".join(
        (
            f"python={sys.version.replace(chr(10), ' ')}",
            f"platform={platform.platform()}",
            f"executable={sys.executable}",
            f"git_commit={manifest['git_commit']}",
        )
    )
    (output_dir / "environment.txt").write_text(
        environment + "\n",
        encoding="utf-8",
    )
    _write_checksums(output_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/synthetic/latest"),
    )
    parser.add_argument("--sample-size", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20260716)
    args = parser.parse_args()
    run(args.output_dir, args.sample_size, args.seed)


if __name__ == "__main__":
    main()

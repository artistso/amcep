#!/usr/bin/env python3
"""Run the locked AMCEP constrained-allocation benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.allocation_benchmark import (  # noqa: E402
    MODELS,
    AllocationConfig,
    run_grid,
    serializable_aggregates,
    serializable_scenarios,
    summarize_grid,
)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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


def run(
    output_dir: Path,
    *,
    seed_start: int,
    seed_count: int,
    attack_rates: tuple[float, ...],
    bootstrap_resamples: int,
) -> None:
    if seed_count < 2:
        raise ValueError("seed_count must be at least two")
    output_dir.mkdir(parents=True, exist_ok=True)

    config = AllocationConfig()
    seeds = tuple(range(seed_start, seed_start + seed_count))
    scenarios = run_grid(seeds, attack_rates, config)
    aggregates = summarize_grid(
        scenarios,
        bootstrap_seed=20260716,
        resamples=bootstrap_resamples,
    )

    _write_json(
        output_dir / "config.json",
        {
            "allocation_config": asdict(config),
            "seed_start": seed_start,
            "seed_count": seed_count,
            "attack_rates": list(attack_rates),
            "bootstrap_resamples": bootstrap_resamples,
        },
    )
    _write_json(
        output_dir / "scenarios.json",
        serializable_scenarios(scenarios),
    )
    _write_json(
        output_dir / "aggregates.json",
        serializable_aggregates(aggregates),
    )

    manifest = {
        "schema_version": "1.0.0",
        "experiment_id": "amcep-constrained-allocation-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "models": list(MODELS),
        "seed_start": seed_start,
        "seed_count": seed_count,
        "attack_rates": list(attack_rates),
        "scenario_count": len(scenarios),
        "bootstrap_resamples": bootstrap_resamples,
        "decision_problem": {
            "objective": "maximize true net value",
            "constraints": [
                "integer cost budget",
                "integer persistent-risk budget",
            ],
            "oracle": "exact two-constraint 0/1 dynamic program",
        },
        "interpretation_boundary": (
            "Synthetic allocation outcomes test declared decision behavior, "
            "constraint failures, and manipulation sensitivity. They do not "
            "establish external validity, fairness, morality, or physical law."
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


def _parse_attack_rates(raw: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one attack rate is required")
    if any(not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("attack rates must be in [0, 1]")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/allocation/latest"),
    )
    parser.add_argument("--seed-start", type=int, default=20260716)
    parser.add_argument("--seed-count", type=int, default=30)
    parser.add_argument(
        "--attack-rates",
        default="0,0.1,0.25,0.5",
    )
    parser.add_argument("--bootstrap-resamples", type=int, default=1000)
    args = parser.parse_args()
    run(
        args.output_dir,
        seed_start=args.seed_start,
        seed_count=args.seed_count,
        attack_rates=_parse_attack_rates(args.attack_rates),
        bootstrap_resamples=args.bootstrap_resamples,
    )


if __name__ == "__main__":
    main()

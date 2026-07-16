#!/usr/bin/env python3
"""Run AMCEP robustness attacks and emit checksummed audit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.robustness_attacks import (  # noqa: E402
    GROUPS,
    MODELS,
    serializable_matrix,
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


def run(output_dir: Path, sample_size: int, seed: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = serializable_matrix(sample_size=sample_size, seed=seed)
    _write_json(output_dir / "metrics.json", matrix)

    manifest = {
        "schema_version": "1.0.0",
        "experiment_id": "amcep-robustness-attacks-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "base_seed": seed,
        "sample_size_per_group": sample_size,
        "groups": list(GROUPS),
        "models": list(MODELS),
        "attacks": [
            "coherent task-value unit rescaling",
            "contradiction-severity intervention",
            "persistence boundary shift around |x| = 1",
            "small positive normalization stress",
            "high-severity distribution shift",
            "independent Decimal arithmetic agreement",
        ],
        "interpretation_boundary": (
            "These attacks test structural and numerical behavior only. "
            "They do not establish external validity, fairness, morality, "
            "or physical law."
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
        default=Path("results/robustness/latest"),
    )
    parser.add_argument("--sample-size", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20260716)
    args = parser.parse_args()
    run(args.output_dir, args.sample_size, args.seed)


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from llm_env_drift_checker.audit import DriftFinding, DriftLevel, compare_env_maps


LEVEL_RANK = {
    DriftLevel.warning: 1,
    DriftLevel.error: 2,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare two LLM env files for rollout drift.")
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--fail-on", choices=[DriftLevel.warning, DriftLevel.error], default=DriftLevel.warning)
    args = parser.parse_args(argv)

    findings = compare_env_maps(_read_env_file(args.source), _read_env_file(args.target))
    for finding in findings:
        print(f"{finding.level.upper():7} {finding.code} {finding.message}")

    threshold = LEVEL_RANK[args.fail_on]
    if any(LEVEL_RANK[finding.level] >= threshold for finding in findings):
        return 1
    return 0


def _read_env_file(path: str) -> dict[str, str]:
    env_map: dict[str, str] = {}
    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_map[key.strip()] = value.strip()
    return env_map


if __name__ == "__main__":
    raise SystemExit(main())

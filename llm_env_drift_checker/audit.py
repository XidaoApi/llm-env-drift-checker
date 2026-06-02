from __future__ import annotations

from dataclasses import dataclass


class DriftLevel:
    error = "error"
    warning = "warning"


@dataclass(frozen=True)
class DriftFinding:
    level: str
    code: str
    message: str


ALIASES = {
    "base_url": ("OPENAI_BASE_URL", "BASE_URL", "LLM_BASE_URL"),
    "model": ("OPENAI_MODEL", "MODEL", "LLM_MODEL"),
    "timeout": ("OPENAI_TIMEOUT", "TIMEOUT_SECONDS", "LLM_TIMEOUT"),
    "retries": ("OPENAI_MAX_RETRIES", "MAX_RETRIES", "LLM_MAX_RETRIES"),
    "temperature": ("OPENAI_TEMPERATURE", "TEMPERATURE", "LLM_TEMPERATURE"),
}


def compare_env_maps(source: dict[str, str], target: dict[str, str]) -> list[DriftFinding]:
    findings: list[DriftFinding] = []

    for canonical_name, keys in ALIASES.items():
        source_value = _first_present(source, keys)
        target_value = _first_present(target, keys)

        if source_value is None and target_value is None:
            continue
        if source_value is None:
            findings.append(
                DriftFinding(
                    DriftLevel.error,
                    "missing-in-source",
                    f"{canonical_name} is missing in source but present in target.",
                )
            )
            continue
        if target_value is None:
            findings.append(
                DriftFinding(
                    DriftLevel.error,
                    "missing-in-target",
                    f"{canonical_name} is present in source but missing in target.",
                )
            )
            continue
        if source_value == target_value:
            continue

        code = f"{canonical_name.replace('_', '-')}-mismatch"
        level = DriftLevel.error if canonical_name == "base_url" else DriftLevel.warning
        findings.append(
            DriftFinding(
                level,
                code,
                f"staging uses {source_value} but production uses {target_value}.",
            )
        )

    findings.extend(_extra_key_findings(source, target, side="source"))
    findings.extend(_extra_key_findings(target, source, side="target"))
    return findings


def _extra_key_findings(primary: dict[str, str], secondary: dict[str, str], side: str) -> list[DriftFinding]:
    canonical_keys = {key for keys in ALIASES.values() for key in keys}
    findings: list[DriftFinding] = []
    for key in sorted(primary):
        if key in canonical_keys or key in secondary:
            continue
        findings.append(
            DriftFinding(
                DriftLevel.warning,
                f"extra-key-in-{side}",
                f"{key} is only present in {side}.",
            )
        )
    return findings


def _first_present(values: dict[str, str], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = values.get(key)
        if value is not None:
            return value.strip()
    return None

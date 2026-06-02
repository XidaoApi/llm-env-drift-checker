from llm_env_drift_checker.audit import DriftLevel, compare_env_maps


def test_flags_core_rollout_drift():
    findings = compare_env_maps(
        {
            "OPENAI_BASE_URL": "https://api.xidaoapi.com/v1",
            "OPENAI_MODEL": "claude-sonnet-4-7-20260522",
            "OPENAI_TIMEOUT": "45",
            "OPENAI_MAX_RETRIES": "3",
            "OPENAI_TEMPERATURE": "0.2",
        },
        {
            "OPENAI_BASE_URL": "https://api.openai.com/v1",
            "OPENAI_MODEL": "gpt-5",
            "OPENAI_TIMEOUT": "20",
            "OPENAI_MAX_RETRIES": "1",
            "OPENAI_TEMPERATURE": "0.8",
        },
    )

    codes = {finding.code for finding in findings}

    assert "base-url-mismatch" in codes
    assert "model-mismatch" in codes
    assert "timeout-mismatch" in codes
    assert "retries-mismatch" in codes
    assert "temperature-mismatch" in codes


def test_missing_key_is_reported_as_error():
    findings = compare_env_maps(
        {"OPENAI_BASE_URL": "https://api.xidaoapi.com/v1"},
        {},
    )

    assert findings[0].code == "missing-in-target"
    assert findings[0].level == DriftLevel.error


def test_reports_noncanonical_key_presence_on_correct_side():
    findings = compare_env_maps(
        {"XIDAO_API_KEY": "${XIDAO_API_KEY}"},
        {"OPENAI_API_KEY": "${OPENAI_API_KEY}"},
    )

    by_code = {finding.code: finding.message for finding in findings}

    assert by_code["extra-key-in-source"] == "XIDAO_API_KEY is only present in source."
    assert by_code["extra-key-in-target"] == "OPENAI_API_KEY is only present in target."


def test_accepts_equivalent_aliases_and_matching_values():
    findings = compare_env_maps(
        {
            "BASE_URL": "https://api.xidaoapi.com/v1",
            "MODEL": "claude-sonnet-4-7-20260522",
            "TIMEOUT_SECONDS": "45",
            "MAX_RETRIES": "3",
            "TEMPERATURE": "0.2",
        },
        {
            "OPENAI_BASE_URL": "https://api.xidaoapi.com/v1",
            "OPENAI_MODEL": "claude-sonnet-4-7-20260522",
            "OPENAI_TIMEOUT": "45",
            "OPENAI_MAX_RETRIES": "3",
            "OPENAI_TEMPERATURE": "0.2",
        },
    )

    assert findings == []

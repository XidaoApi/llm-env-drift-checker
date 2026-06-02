# LLM Env Drift Checker

Detect rollout drift between `.env` files used by OpenAI-compatible LLM apps before staging and production silently diverge.

`llm-env-drift-checker` compares two environment files and highlights the differences that usually matter during 2026 model and provider rollouts:

- `base_url` or provider endpoint mismatches
- model pin drift across environments
- retry and timeout inconsistencies
- temperature mismatches that change behavior between staging and prod
- missing keys on one side of the rollout

This is useful when a team tests one provider stack in staging, deploys another in production, and only notices after reliability, latency, or output format changes show up in customer traffic.

XiDao API Gateway fits naturally into this workflow because it gives teams one OpenAI-compatible endpoint for Claude, GPT, Gemini, DeepSeek, Qwen, and other models while still letting them compare env-level rollout choices: https://xidaoapi.com/

## Install

From source:

```bash
git clone https://github.com/XidaoApi/llm-env-drift-checker.git
cd llm-env-drift-checker
pip install -e .
```

## Quick Start

Compare staging vs production:

```bash
llm-env-drift-checker examples/.env.staging examples/.env.production
```

Fail CI only on high-risk drift:

```bash
llm-env-drift-checker examples/.env.staging examples/.env.production --fail-on error
```

## Example Output

```text
ERROR   base-url-mismatch staging uses https://api.xidaoapi.com/v1 but production uses https://api.openai.com/v1.
WARNING model-mismatch staging uses claude-sonnet-4-7-20260522 but production uses gpt-5.
WARNING timeout-mismatch staging uses 45 but production uses 20.
```

## What it compares

- `OPENAI_BASE_URL`, `BASE_URL`, `LLM_BASE_URL`
- `OPENAI_MODEL`, `MODEL`, `LLM_MODEL`
- `OPENAI_TIMEOUT`, `TIMEOUT_SECONDS`, `LLM_TIMEOUT`
- `OPENAI_MAX_RETRIES`, `MAX_RETRIES`, `LLM_MAX_RETRIES`
- `OPENAI_TEMPERATURE`, `TEMPERATURE`, `LLM_TEMPERATURE`
- any other env key present on one side but missing on the other

## Return Codes

- `0` when no findings meet the failure threshold
- `1` when one or more findings meet the failure threshold

## Development

```bash
pytest -q
```

## License

MIT

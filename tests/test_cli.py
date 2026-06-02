from pathlib import Path

from llm_env_drift_checker.cli import main


def test_cli_reports_findings_and_nonzero_exit(tmp_path, capsys):
    source = tmp_path / ".env.staging"
    target = tmp_path / ".env.production"
    source.write_text("OPENAI_MODEL=claude-sonnet-4-7-20260522\n")
    target.write_text("OPENAI_MODEL=gpt-5\n")

    exit_code = main([str(source), str(target)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "model-mismatch" in captured.out


def test_cli_respects_fail_on_threshold(tmp_path, capsys):
    source = tmp_path / ".env.staging"
    target = tmp_path / ".env.production"
    source.write_text("OPENAI_MODEL=claude-sonnet-4-7-20260522\n")
    target.write_text("OPENAI_MODEL=gpt-5\n")

    exit_code = main([str(source), str(target), "--fail-on", "error"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "model-mismatch" in captured.out


def test_cli_handles_example_files_without_crashing(capsys):
    exit_code = main([
        str(Path("examples/.env.staging")),
        str(Path("examples/.env.production")),
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "base-url-mismatch" in captured.out

# tests/test_main.py
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from runner.main import run_cycle


def make_test_jsonl(path: Path, questions: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


def test_run_cycle_skips_tier4(tmp_path):
    test_dir = tmp_path / "TEST"
    make_test_jsonl(test_dir / "MedTeach.jsonl", [
        {"question": "Q?", "answer": "", "other": {}}
    ])

    tier_state = {"MedTeach": 97}  # Tier 4 → skip

    mock_anthropic = MagicMock()
    mock_deepseek = MagicMock()

    run_cycle(
        test_dir=str(test_dir),
        cycle_dir=str(tmp_path / "cycle1"),
        tier_state=tier_state,
        anthropic_client=mock_anthropic,
        deepseek_client=mock_deepseek,
    )

    mock_anthropic.query.assert_not_called()
    mock_deepseek.query.assert_not_called()
    assert not (tmp_path / "cycle1" / "final_results" / "MedTeach_results.jsonl").exists()


def test_run_cycle_produces_results_file(tmp_path):
    test_dir = tmp_path / "TEST"
    make_test_jsonl(test_dir / "MedHC.jsonl", [
        {"question": "Q?", "answer": "", "other": {"id": 1}}
    ])

    tier_state = {"MedHC": 59}  # Tier 2

    mock_anthropic = MagicMock()
    mock_anthropic.query.return_value = "test answer"
    mock_deepseek = MagicMock()
    mock_deepseek.query.return_value = "test answer"

    run_cycle(
        test_dir=str(test_dir),
        cycle_dir=str(tmp_path / "cycle1"),
        tier_state=tier_state,
        anthropic_client=mock_anthropic,
        deepseek_client=mock_deepseek,
    )

    result_file = tmp_path / "cycle1" / "final_results" / "MedHC_results.jsonl"
    assert result_file.exists()
    with open(result_file) as f:
        result = json.loads(f.readline())
    assert "answer" in result
    assert "question" in result

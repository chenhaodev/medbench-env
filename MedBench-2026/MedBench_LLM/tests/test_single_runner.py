# tests/test_single_runner.py
from unittest.mock import MagicMock
import pytest
from runner.single_runner import run_tier3

SAMPLE_QUESTIONS = [
    {"question": "Q1?", "answer": "", "other": {"id": 1}},
]


def test_tier3_calls_claude_once_per_question():
    client = MagicMock()
    client.query.return_value = "some answer"

    answers = run_tier3(
        questions=SAMPLE_QUESTIONS,
        client=client,
        model="claude-sonnet-4-5-20251001",
    )

    assert len(answers) == 1
    assert answers[0] == "some answer"
    client.query.assert_called_once_with("Q1?", model="claude-sonnet-4-5-20251001")


def test_tier3_handles_error_gracefully():
    client = MagicMock()
    client.query.return_value = "ERROR: timeout"

    answers = run_tier3(
        questions=SAMPLE_QUESTIONS,
        client=client,
        model="claude-sonnet-4-5-20251001",
    )

    assert answers[0].startswith("ERROR:")

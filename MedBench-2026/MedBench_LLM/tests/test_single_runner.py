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
    assert client.query.call_count == 1
    # Prompt includes the question and a format suffix
    call_prompt = client.query.call_args[0][0]
    assert "Q1?" in call_prompt


def test_tier3_handles_error_gracefully():
    client = MagicMock()
    client.query.return_value = "ERROR: timeout"

    answers = run_tier3(
        questions=SAMPLE_QUESTIONS,
        client=client,
        model="claude-sonnet-4-5-20251001",
    )

    assert answers[0].startswith("ERROR:")


def test_tier3_injects_qwen_context():
    """When qwen_answers provided, Claude prompt includes Qwen reference."""
    client = MagicMock()
    client.query.return_value = "答案"

    run_tier3(
        questions=[{"question": "Q1?", "answer": "", "other": {"id": 1}}],
        client=client,
        model="claude-opus-4-6",
        qwen_answers=["参考答案"],
        format_type="freeform",
    )

    call_prompt = client.query.call_args[0][0]
    assert "Qwen" in call_prompt
    assert "参考答案" in call_prompt


def test_tier3_no_qwen_still_works():
    """Without qwen_answers, Tier 3 behaves as before (no context block)."""
    client = MagicMock()
    client.query.return_value = "答案"

    answers = run_tier3(
        questions=[{"question": "Q1?", "answer": "", "other": {"id": 1}}],
        client=client,
        model="claude-opus-4-6",
    )

    assert answers[0] == "答案"
    call_prompt = client.query.call_args[0][0]
    assert "其他模型" not in call_prompt


def test_tier3_qwen_error_excluded_from_context():
    """Qwen ERROR answer not injected into prompt."""
    client = MagicMock()
    client.query.return_value = "答案"

    run_tier3(
        questions=[{"question": "Q1?", "answer": "", "other": {"id": 1}}],
        client=client,
        model="claude-opus-4-6",
        qwen_answers=["ERROR: 403"],
        format_type="freeform",
    )

    call_prompt = client.query.call_args[0][0]
    assert "其他模型" not in call_prompt

# tests/test_multi_model_runner.py
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from runner.multi_model_runner import run_tier1, run_tier2

SAMPLE_QUESTIONS = [
    {"question": "Q1?", "answer": "", "other": {"id": 1}},
    {"question": "Q2?", "answer": "", "other": {"id": 2}},
]


def make_mock_client(answer: str):
    client = MagicMock()
    client.query.return_value = answer
    return client


def test_tier1_ds_unanimous_uses_ds_answer(tmp_path):
    ds_client = make_mock_client("B")    # always returns B
    opus_client = make_mock_client("A")  # would return A but DS is unanimous

    answers = run_tier1(
        questions=SAMPLE_QUESTIONS,
        task_name="DDx-advanced",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-reasoner",
        opus_client=opus_client,
        opus_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
    )
    # DS unanimous (B,B,B) differs from what Claude would say → use DS
    assert all(a == "b" for a in answers)
    # Opus should NOT be called (DS unanimous)
    opus_client.query.assert_not_called()


def test_tier1_ds_not_unanimous_calls_opus(tmp_path):
    ds_client = MagicMock()
    # Alternating A/B per question across 3 runs → not unanimous
    ds_client.query.side_effect = ["A", "B", "A", "A", "B", "A"]
    opus_client = make_mock_client("C")

    answers = run_tier1(
        questions=SAMPLE_QUESTIONS,
        task_name="DDx-advanced",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-reasoner",
        opus_client=opus_client,
        opus_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
    )
    assert opus_client.query.call_count == 2  # called for each question


def test_tier2_ds_override_when_both_agree(tmp_path):
    sonnet_client = make_mock_client("A")
    ds_client = make_mock_client("B")  # both DS return B

    answers = run_tier2(
        questions=SAMPLE_QUESTIONS,
        task_name="MedHC",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-chat",
        sonnet_client=sonnet_client,
        sonnet_model="claude-sonnet-4-6",
        raw_votes_dir=tmp_path,
    )
    assert all(a == "b" for a in answers)


def test_raw_votes_saved(tmp_path):
    ds_client = make_mock_client("A")
    opus_client = make_mock_client("A")

    run_tier1(
        questions=SAMPLE_QUESTIONS,
        task_name="DDx-advanced",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-reasoner",
        opus_client=opus_client,
        opus_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
    )
    vote_dir = tmp_path / "DDx-advanced"
    assert vote_dir.exists()
    vote_files = list(vote_dir.glob("*.jsonl"))
    assert len(vote_files) >= 3  # at least 3 DS runs saved


def test_tier1_all_unanimous_skips_claude(tmp_path):
    """DS×3 + Qwen all return 'B' → Claude never called (skip optimization)."""
    ds_client = make_mock_client("B")
    opus_client = make_mock_client("A")

    answers = run_tier1(
        questions=SAMPLE_QUESTIONS,
        task_name="MedLitQA",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-reasoner",
        opus_client=opus_client,
        opus_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
        qwen_answers=["B", "B"],  # Qwen also says B
    )
    assert all(a == "b" for a in answers)
    opus_client.query.assert_not_called()


def test_tier1_qwen_breaks_unanimity_calls_claude(tmp_path):
    """DS×3 say 'B', Qwen says 'A' → not unanimous → Claude called."""
    ds_client = make_mock_client("B")
    opus_client = make_mock_client("C")

    answers = run_tier1(
        questions=SAMPLE_QUESTIONS,
        task_name="MedLitQA",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-reasoner",
        opus_client=opus_client,
        opus_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
        qwen_answers=["A", "A"],  # Qwen disagrees
    )
    # Claude is called (not unanimous); Claude's answer wins (context-informed synthesizer)
    opus_client.query.assert_called()
    # Opus receives context-injected prompt containing Qwen's answer
    call_args = opus_client.query.call_args_list
    assert any("Qwen" in str(args) for args in call_args)


def test_tier2_claude_prompt_includes_qwen_context(tmp_path):
    """When qwen_answers provided, Claude receives context-injected prompt."""
    ds_client = make_mock_client("B")
    sonnet_client = make_mock_client("A")

    run_tier2(
        questions=SAMPLE_QUESTIONS,
        task_name="MedMC",
        format_type="mcq",
        ds_client=ds_client,
        ds_model="deepseek-chat",
        sonnet_client=sonnet_client,
        sonnet_model="claude-opus-4-6",
        raw_votes_dir=tmp_path,
        qwen_answers=["C", "C"],
    )
    # Claude should have been called with a prompt containing "Qwen"
    call_args = sonnet_client.query.call_args_list
    assert any("Qwen" in str(args) for args in call_args)

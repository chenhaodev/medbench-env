# tests/test_aggregator.py
import pytest
from runner.aggregator import normalize_answer, majority_vote, claude_anchored_vote_tier1, claude_anchored_vote_tier2, is_error_answer

# normalize_answer
def test_normalize_mcq_strips_punctuation():
    assert normalize_answer("A.", "mcq") == "a"
    assert normalize_answer(" B ", "mcq") == "b"
    assert normalize_answer("C", "mcq") == "c"

def test_normalize_multi_select_sorts():
    assert normalize_answer("C, A, B", "multi_select") == "a,b,c"
    assert normalize_answer("A,C,B", "multi_select") == "a,b,c"
    assert normalize_answer("B, A", "multi_select") == "a,b"

def test_normalize_freeform_strips_whitespace():
    assert normalize_answer("  hello  ", "freeform") == "hello"

# majority_vote
def test_majority_vote_clear_winner():
    assert majority_vote(["A", "A", "B"], "mcq") == "a"

def test_majority_vote_tie_returns_first():
    result = majority_vote(["A", "B"], "mcq")
    assert result in ["a", "b"]

def test_majority_vote_multi_select():
    assert majority_vote(["A,B", "A,B", "A,C"], "multi_select") == "a,b"

# claude_anchored_vote_tier1: DS unanimous + differs → use DS; else Claude
def test_tier1_ds_unanimous_and_differs_uses_ds():
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "B", "B"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "b"

def test_tier1_ds_not_unanimous_uses_claude():
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "C", "B"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "a"

def test_tier1_ds_unanimous_but_agrees_uses_claude():
    result = claude_anchored_vote_tier1(
        ds_answers=["A", "A", "A"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "a"

# claude_anchored_vote_tier2: both DS agree + differs → use DS; else Claude
def test_tier2_both_ds_agree_and_differ_uses_ds():
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "B"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "b"

def test_tier2_ds_disagree_uses_claude():
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "C"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "a"

def test_tier2_freeform_always_uses_claude():
    result = claude_anchored_vote_tier2(
        ds_answers=["some long text", "some long text"],
        claude_answer="different text",
        format_type="freeform"
    )
    assert result == "different text"

def test_tier2_json_struct_always_uses_claude():
    result = claude_anchored_vote_tier2(
        ds_answers=['{"value": 1}', '{"value": 1}'],
        claude_answer='{"value": 2}',
        format_type="json_struct"
    )
    assert result == '{"value": 2}'

def test_majority_vote_empty_returns_empty():
    assert majority_vote([], "mcq") == ""


# is_error_answer
def test_is_error_answer_detects_error_prefix():
    assert is_error_answer("ERROR: timeout") is True
    assert is_error_answer("ERROR: Rate limit exceeded") is True
    assert is_error_answer("  ERROR: something") is True

def test_is_error_answer_ignores_normal_answers():
    assert is_error_answer("A") is False
    assert is_error_answer("B") is False
    assert is_error_answer("some freeform text") is False


# claude_anchored_vote_tier1: error filtering
def test_tier1_all_ds_errors_uses_claude():
    result = claude_anchored_vote_tier1(
        ds_answers=["ERROR: timeout", "ERROR: timeout", "ERROR: timeout"],
        claude_answer="A",
        format_type="mcq"
    )
    # When all DS answers are errors, Claude's answer is returned as-is (stripped)
    assert result == "A"

def test_tier1_some_ds_errors_uses_claude():
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "ERROR: timeout", "B"],
        claude_answer="A",
        format_type="mcq"
    )
    assert result == "a"  # not all DS were valid, Claude wins


# claude_anchored_vote_tier2: error filtering
def test_tier2_any_ds_error_uses_claude():
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "ERROR: timeout"],
        claude_answer="A",
        format_type="mcq"
    )
    # When any DS answer is an error, Claude's answer is returned as-is (stripped)
    assert result == "A"

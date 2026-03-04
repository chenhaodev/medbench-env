import pytest
from runner.prompt_builder import build_prompt


def test_no_context_returns_question_with_suffix():
    prompt = build_prompt("What is A?", "mcq", {})
    assert "What is A?" in prompt
    assert "请只输出选项字母" in prompt
    assert "其他模型" not in prompt


def test_with_context_includes_model_answers():
    prompt = build_prompt("What is A?", "mcq", {"Qwen": "B", "DeepSeek": "C"})
    assert "其他模型的参考回答" in prompt
    assert "Qwen" in prompt
    assert "DeepSeek" in prompt
    assert "请只输出选项字母" in prompt


def test_error_answers_excluded_from_context():
    prompt = build_prompt("Q?", "mcq", {"Qwen": "ERROR: timeout", "DS": "A"})
    assert "ERROR" not in prompt
    assert "DS" in prompt


def test_all_error_answers_gives_plain_prompt():
    prompt = build_prompt("Q?", "freeform", {"Qwen": "ERROR: 403"})
    assert "其他模型" not in prompt
    assert "请用中文详细回答" in prompt


def test_freeform_suffix():
    prompt = build_prompt("Q?", "freeform", {})
    assert "请用中文详细回答" in prompt


def test_multi_select_suffix():
    prompt = build_prompt("Q?", "multi_select", {})
    assert "请输出所有正确选项" in prompt


def test_json_struct_suffix():
    prompt = build_prompt("Q?", "json_struct", {})
    assert "请只输出JSON" in prompt


def test_empty_answer_excluded_from_context():
    prompt = build_prompt("Q?", "mcq", {"Qwen": "", "DS": "A"})
    assert "Qwen" not in prompt
    assert "DS" in prompt

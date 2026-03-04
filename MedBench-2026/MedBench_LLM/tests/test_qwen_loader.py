import json
from pathlib import Path
import pytest
from runner.qwen_loader import load_qwen_answers


def make_qwen_jsonl(path: Path, answers: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for i, ans in enumerate(answers):
            f.write(json.dumps({"question": f"Q{i}", "answer": ans, "other": {"id": i}}, ensure_ascii=False) + "\n")


def test_load_returns_answer_strings(tmp_path):
    make_qwen_jsonl(tmp_path / "MedMC.jsonl", ["A", "B", "C"])
    result = load_qwen_answers(str(tmp_path), "MedMC")
    assert result == ["A", "B", "C"]


def test_load_returns_none_for_missing_task(tmp_path):
    result = load_qwen_answers(str(tmp_path), "NonExistentTask")
    assert result is None


def test_load_handles_missing_answer_field(tmp_path):
    path = tmp_path / "MedHC.jsonl"
    path.write_text('{"question":"Q0","other":{}}\n{"question":"Q1","answer":"text","other":{}}\n', encoding="utf-8")
    result = load_qwen_answers(str(tmp_path), "MedHC")
    assert result == ["", "text"]


def test_load_skips_blank_lines(tmp_path):
    path = tmp_path / "MedMC.jsonl"
    path.write_text('{"question":"Q0","answer":"A","other":{}}\n\n{"question":"Q1","answer":"B","other":{}}\n', encoding="utf-8")
    result = load_qwen_answers(str(tmp_path), "MedMC")
    assert result == ["A", "B"]

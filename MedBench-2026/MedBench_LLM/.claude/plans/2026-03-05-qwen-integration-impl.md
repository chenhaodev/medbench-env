# Qwen Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate cycle0 Qwen answers as a free context signal and extra voter across all tiers, and copy Qwen answers directly for Tier 4 tasks (zero API calls).

**Architecture:** Two new modules (`qwen_loader.py`, `prompt_builder.py`) keep I/O and prompt construction pure and testable. Existing `aggregator.py`, `multi_model_runner.py`, `single_runner.py`, and `main.py` are updated to thread Qwen answers through. Claude always receives a context-injected prompt; for MCQ/multi_select Tier 1, Claude call is skipped entirely when DS×3 + Qwen unanimously agree.

**Tech Stack:** Python 3.11, pytest, existing runner package (`runner/`), Qwen JSONL at `../SUBMIT/results-qwen-wxw-20251215/MedBench_LLM/`

---

## Task 1: qwen_loader.py — Load Qwen answers per task

**Files:**
- Create: `runner/qwen_loader.py`
- Test: `tests/test_qwen_loader.py`

**Step 1: Write the failing test**

```python
# tests/test_qwen_loader.py
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


def test_load_handles_empty_answer_field(tmp_path):
    make_qwen_jsonl(tmp_path / "MedHC.jsonl", ["some text", ""])
    result = load_qwen_answers(str(tmp_path), "MedHC")
    assert result == ["some text", ""]


def test_load_skips_blank_lines(tmp_path):
    path = tmp_path / "MedMC.jsonl"
    path.write_text('{"question":"Q0","answer":"A","other":{}}\n\n{"question":"Q1","answer":"B","other":{}}\n', encoding="utf-8")
    result = load_qwen_answers(str(tmp_path), "MedMC")
    assert result == ["A", "B"]
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_qwen_loader.py -v
```
Expected: `ImportError: cannot import name 'load_qwen_answers'`

**Step 3: Write implementation**

```python
# runner/qwen_loader.py
import json
from pathlib import Path
from typing import List, Optional


def load_qwen_answers(qwen_dir: str, task_name: str) -> Optional[List[str]]:
    """Load Qwen's pre-computed answers for a task.

    Returns a list of answer strings indexed by question position,
    or None if the task file does not exist.
    """
    path = Path(qwen_dir) / f"{task_name}.jsonl"
    if not path.exists():
        return None

    answers = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                answers.append(d.get("answer", ""))
    return answers
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_qwen_loader.py -v
```
Expected: 4 passed

**Step 5: Commit**

```bash
git add runner/qwen_loader.py tests/test_qwen_loader.py
git commit -m "feat: add qwen_loader to load cycle0 Qwen answers"
```

---

## Task 2: prompt_builder.py — Build context-injected Claude prompts

**Files:**
- Create: `runner/prompt_builder.py`
- Test: `tests/test_prompt_builder.py`

**Step 1: Write the failing tests**

```python
# tests/test_prompt_builder.py
import pytest
from runner.prompt_builder import build_prompt


def test_no_context_returns_question_with_suffix():
    prompt = build_prompt("What is A?", "mcq", {})
    assert "What is A?" in prompt
    assert "请只输出选项字母" in prompt
    # No context section
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
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_prompt_builder.py -v
```
Expected: `ImportError: cannot import name 'build_prompt'`

**Step 3: Write implementation**

```python
# runner/prompt_builder.py
from typing import Dict

from .aggregator import is_error_answer

FORMAT_SUFFIXES: Dict[str, str] = {
    "mcq":          "请只输出选项字母，例如：A",
    "freeform":     "请用中文详细回答",
    "multi_select": "请输出所有正确选项，例如：A, B, C",
    "json_struct":  "请只输出JSON格式答案",
}


def build_prompt(question: str, format_type: str, other_answers: Dict[str, str]) -> str:
    """Build a Claude prompt with optional context from other models.

    Args:
        question: The original question text.
        format_type: One of 'mcq', 'freeform', 'multi_select', 'json_struct'.
        other_answers: Dict mapping model label → answer string. Errors and
                       empty strings are silently excluded from the context block.

    Returns:
        A prompt string with format suffix appended. If valid context exists,
        a Chinese-language reference block is injected before the suffix.
    """
    suffix = FORMAT_SUFFIXES.get(format_type, FORMAT_SUFFIXES["freeform"])

    valid_context = {
        label: ans
        for label, ans in other_answers.items()
        if ans and not is_error_answer(ans)
    }

    if not valid_context:
        return f"{question}\n\n{suffix}"

    context_lines = "\n".join(
        f"- {label}：{answer}" for label, answer in valid_context.items()
    )
    return (
        f"{question}\n\n"
        f"---\n"
        f"其他模型的参考回答：\n{context_lines}\n\n"
        f"请综合以上参考，给出你的最佳答案。\n{suffix}"
    )
```

**Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_prompt_builder.py -v
```
Expected: 8 passed

**Step 5: Run all tests to ensure no regressions**

```bash
python -m pytest tests/ -q
```
Expected: 51 passed (43 existing + 8 new)

**Step 6: Commit**

```bash
git add runner/prompt_builder.py tests/test_prompt_builder.py
git commit -m "feat: add prompt_builder with Qwen context injection and format suffixes"
```

---

## Task 3: Update aggregator.py — Add qwen_answer to vote functions

**Files:**
- Modify: `runner/aggregator.py`
- Modify: `tests/test_aggregator.py`

**Step 1: Write the failing tests** (add to end of `tests/test_aggregator.py`)

```python
# Add to tests/test_aggregator.py

# --- Tier 1 with Qwen ---

def test_tier1_ds_and_qwen_all_agree_overrides_claude():
    """DS×3 + Qwen all agree on B, Claude says A → DS/Qwen wins."""
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="B",
    )
    assert result == "b"


def test_tier1_qwen_disagrees_with_ds_claude_wins():
    """DS×3 unanimous on B, Qwen says A → not all challengers agree → Claude wins."""
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="A",  # Qwen sides with Claude
    )
    assert result == "a"  # Claude wins


def test_tier1_no_qwen_behaves_as_before():
    """Without qwen_answer, existing DS-only logic unchanged."""
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "B", "B"],
        claude_answer="A",
        format_type="mcq",
    )
    assert result == "b"  # DS unanimous, differs from Claude → DS wins


def test_tier1_qwen_error_excluded():
    """Qwen ERROR treated as absent; DS unanimous still overrides Claude."""
    result = claude_anchored_vote_tier1(
        ds_answers=["B", "B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="ERROR: timeout",
    )
    assert result == "b"  # DS unanimous, Qwen excluded → DS wins


# --- Tier 2 with Qwen ---

def test_tier2_ds_and_qwen_agree_overrides_claude():
    """Both DS + Qwen agree on B, Claude says A → stricter override triggered."""
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="B",
    )
    assert result == "b"


def test_tier2_ds_agree_but_qwen_sides_with_claude():
    """Both DS agree on B, but Qwen says A (same as Claude) → Claude wins."""
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="A",
    )
    assert result == "a"  # Qwen vetos DS override


def test_tier2_no_qwen_fallback_to_ds_only():
    """No Qwen → original DS-only logic: both DS agree and differ → override."""
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "B"],
        claude_answer="A",
        format_type="mcq",
    )
    assert result == "b"


def test_tier2_qwen_error_falls_back_to_ds_only():
    """Qwen error → treat as absent, fall back to DS-only override logic."""
    result = claude_anchored_vote_tier2(
        ds_answers=["B", "B"],
        claude_answer="A",
        format_type="mcq",
        qwen_answer="ERROR: 403",
    )
    assert result == "b"  # Qwen excluded → DS-only override
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_aggregator.py -v -k "qwen"
```
Expected: `TypeError: claude_anchored_vote_tier1() got an unexpected keyword argument 'qwen_answer'`

**Step 3: Update `runner/aggregator.py`**

Replace `claude_anchored_vote_tier1` and `claude_anchored_vote_tier2` with:

```python
def claude_anchored_vote_tier1(
    ds_answers: List[str],
    claude_answer: str,
    format_type: str,
    qwen_answer: str = "",
) -> str:
    """Tier 1: All challengers (DS×3 + Qwen) must be unanimous to override Claude."""
    if format_type == "freeform":
        return claude_answer.strip()

    # Build full challenger list; include Qwen only if valid
    challengers = list(ds_answers)
    if qwen_answer and not is_error_answer(qwen_answer):
        challengers.append(qwen_answer)

    valid = [a for a in challengers if not is_error_answer(a)]
    if not valid:
        return claude_answer.strip()

    norm_valid = [normalize_answer(a, format_type) for a in valid]
    norm_claude = normalize_answer(claude_answer, format_type)

    all_valid = len(valid) == len(challengers)
    unanimous = len(set(norm_valid)) == 1
    differs = unanimous and (norm_valid[0] != norm_claude)

    if all_valid and differs:
        return norm_valid[0]
    return norm_claude


def claude_anchored_vote_tier2(
    ds_answers: List[str],
    claude_answer: str,
    format_type: str,
    qwen_answer: str = "",
) -> str:
    """Tier 2: DS+Qwen unanimous override only; without Qwen, DS-only override."""
    if format_type in ("freeform", "json_struct"):
        return claude_answer.strip()

    if any(is_error_answer(a) for a in ds_answers):
        return claude_answer.strip()

    norm_ds = [normalize_answer(a, format_type) for a in ds_answers]
    norm_claude = normalize_answer(claude_answer, format_type)
    both_ds_agree = len(set(norm_ds)) == 1

    qwen_valid = qwen_answer and not is_error_answer(qwen_answer)

    if qwen_valid:
        norm_qwen = normalize_answer(qwen_answer, format_type)
        # Require DS + Qwen all agree AND differ from Claude
        if both_ds_agree and (norm_ds[0] == norm_qwen) and (norm_ds[0] != norm_claude):
            return norm_ds[0]
    else:
        # No Qwen → original DS-only override
        if both_ds_agree and (norm_ds[0] != norm_claude):
            return norm_ds[0]

    return norm_claude
```

**Step 4: Run all aggregator tests**

```bash
python -m pytest tests/test_aggregator.py -v
```
Expected: all pass (existing 16 + 8 new = 24)

**Step 5: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: 59 passed

**Step 6: Commit**

```bash
git add runner/aggregator.py tests/test_aggregator.py
git commit -m "feat: add qwen_answer param to tier1/tier2 aggregator vote functions"
```

---

## Task 4: Update multi_model_runner.py — Wire Qwen into Tier 1 & Tier 2

**Files:**
- Modify: `runner/multi_model_runner.py`
- Modify: `tests/test_multi_model_runner.py`

**Step 1: Write the failing tests** (add to `tests/test_multi_model_runner.py`)

```python
# Add to tests/test_multi_model_runner.py
# (keep existing imports, add these)
from runner.multi_model_runner import run_tier1, run_tier2


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
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_multi_model_runner.py -v -k "qwen"
```
Expected: `TypeError: run_tier1() got an unexpected keyword argument 'qwen_answers'`

**Step 3: Update `runner/multi_model_runner.py`**

Add imports at top:
```python
from typing import Optional
from .aggregator import is_error_answer, normalize_answer
from .prompt_builder import build_prompt
```

Add helper function before `run_tier1`:
```python
def _run_model_on_questions_with_qwen_context(
    questions: List[Dict],
    client,
    model: str,
    qwen_answers: Optional[List[str]],
    format_type: str,
) -> List[str]:
    """Run model on questions, injecting Qwen answers as context in each prompt."""
    answers = []
    for q_idx, item in enumerate(questions):
        qwen_ans = (
            qwen_answers[q_idx]
            if qwen_answers and q_idx < len(qwen_answers)
            else ""
        ) or ""
        other = {"Qwen": qwen_ans} if qwen_ans and not is_error_answer(qwen_ans) else {}
        prompt = build_prompt(item["question"], format_type, other)
        answers.append(client.query(prompt, model=model))
    return answers
```

Update `run_tier1` signature and body:
```python
def run_tier1(
    questions: List[Dict[str, Any]],
    task_name: str,
    format_type: str,
    ds_client: DeepSeekClient,
    ds_model: str,
    opus_client: AnthropicClient,
    opus_model: str,
    raw_votes_dir: Path,
    qwen_answers: Optional[List[str]] = None,
) -> List[str]:
    """Run 3x DeepSeek-R1. If DS×3+Qwen unanimous → use DS/Qwen (skip Opus).
    Otherwise call Opus with full context as synthesizer."""
    ds_runs: List[List[str]] = [[], [], []]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_model_on_questions, questions, ds_client, ds_model): i
            for i in range(3)
        }
        for future in as_completed(futures):
            ds_runs[futures[future]] = future.result()

    for i, run_answers in enumerate(ds_runs):
        _save_raw_votes(raw_votes_dir, task_name, f"deepseek-r1-run{i+1}", run_answers)

    final_answers = []
    opus_answers: List[str] = []

    for q_idx in range(len(questions)):
        ds_q_answers = [ds_runs[i][q_idx] for i in range(3)]
        qwen_ans = (
            qwen_answers[q_idx] if qwen_answers and q_idx < len(qwen_answers) else ""
        ) or ""

        # Skip-Claude optimization: all challengers unanimous on MCQ/multi_select
        if format_type not in ("freeform", "json_struct"):
            challengers = ds_q_answers + ([qwen_ans] if qwen_ans and not is_error_answer(qwen_ans) else [])
            valid = [a for a in challengers if not is_error_answer(a)]
            if valid and len(valid) == len(challengers):
                norm = [normalize_answer(a, format_type) for a in valid]
                if len(set(norm)) == 1:
                    final_answers.append(norm[0])
                    opus_answers.append(None)
                    continue

        # Call Opus with full context as synthesizer
        other = {
            "DeepSeek-R1（第1次）": ds_runs[0][q_idx],
            "DeepSeek-R1（第2次）": ds_runs[1][q_idx],
            "DeepSeek-R1（第3次）": ds_runs[2][q_idx],
            "Qwen": qwen_ans,
        }
        prompt = build_prompt(questions[q_idx]["question"], format_type, other)
        opus_answer = opus_client.query(prompt, model=opus_model)
        opus_answers.append(opus_answer)
        result = claude_anchored_vote_tier1(
            ds_answers=ds_q_answers,
            claude_answer=opus_answer,
            format_type=format_type,
            qwen_answer=qwen_ans,
        )
        final_answers.append(result)

    _save_raw_votes(raw_votes_dir, task_name, "opus-tiebreak", opus_answers)
    return final_answers
```

Update `run_tier2` signature and body:
```python
def run_tier2(
    questions: List[Dict[str, Any]],
    task_name: str,
    format_type: str,
    ds_client: DeepSeekClient,
    ds_model: str,
    sonnet_client: AnthropicClient,
    sonnet_model: str,
    raw_votes_dir: Path,
    qwen_answers: Optional[List[str]] = None,
) -> List[str]:
    """Claude anchor (with Qwen context) + 2x DS-V3. DS+Qwen unanimous override only."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_sonnet = executor.submit(
            _run_model_on_questions_with_qwen_context,
            questions, sonnet_client, sonnet_model, qwen_answers, format_type,
        )
        f_ds1 = executor.submit(_run_model_on_questions, questions, ds_client, ds_model)
        f_ds2 = executor.submit(_run_model_on_questions, questions, ds_client, ds_model)
        sonnet_answers = f_sonnet.result()
        ds1_answers = f_ds1.result()
        ds2_answers = f_ds2.result()

    _save_raw_votes(raw_votes_dir, task_name, "sonnet-anchor", sonnet_answers)
    _save_raw_votes(raw_votes_dir, task_name, "deepseek-v3-run1", ds1_answers)
    _save_raw_votes(raw_votes_dir, task_name, "deepseek-v3-run2", ds2_answers)

    final_answers = []
    for q_idx in range(len(questions)):
        qwen_ans = (
            qwen_answers[q_idx] if qwen_answers and q_idx < len(qwen_answers) else ""
        ) or ""
        result = claude_anchored_vote_tier2(
            ds_answers=[ds1_answers[q_idx], ds2_answers[q_idx]],
            claude_answer=sonnet_answers[q_idx],
            format_type=format_type,
            qwen_answer=qwen_ans,
        )
        final_answers.append(result)

    return final_answers
```

**Step 4: Run multi_model_runner tests**

```bash
python -m pytest tests/test_multi_model_runner.py -v
```
Expected: all pass

**Step 5: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: all pass

**Step 6: Commit**

```bash
git add runner/multi_model_runner.py tests/test_multi_model_runner.py
git commit -m "feat: wire Qwen context into Tier 1/2 runners"
```

---

## Task 5: Update single_runner.py — Inject Qwen context for Tier 3

**Files:**
- Modify: `runner/single_runner.py`
- Modify: `tests/test_single_runner.py`

**Step 1: Write the failing tests** (add to `tests/test_single_runner.py`)

```python
# Add to tests/test_single_runner.py
from runner.single_runner import run_tier3


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
    """Without qwen_answers, Tier 3 behaves as before."""
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
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_single_runner.py -v -k "qwen"
```
Expected: `TypeError: run_tier3() got an unexpected keyword argument 'qwen_answers'`

**Step 3: Update `runner/single_runner.py`**

```python
# runner/single_runner.py
from typing import Dict, List, Any, Optional

from .prompt_builder import build_prompt


def run_tier3(
    questions: List[Dict[str, Any]],
    client,
    model: str,
    qwen_answers: Optional[List[str]] = None,
    format_type: str = "freeform",
) -> List[str]:
    """Single-pass Claude for Tier 3 tasks, with optional Qwen context injection."""
    answers = []
    for q_idx, item in enumerate(questions):
        qwen_ans = (
            qwen_answers[q_idx] if qwen_answers and q_idx < len(qwen_answers) else ""
        ) or ""
        other = {"Qwen": qwen_ans} if qwen_ans else {}
        prompt = build_prompt(item["question"], format_type, other)
        answers.append(client.query(prompt, model=model))
    return answers
```

**Step 4: Run all single_runner tests**

Note: existing `test_tier3_calls_claude_once_per_question` checks `client.query.assert_called_once_with("Q1?", model=...)`. This will now fail because the prompt includes a format suffix. Update that test:

```python
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
```

```bash
python -m pytest tests/test_single_runner.py -v
```
Expected: all pass

**Step 5: Run full suite**

```bash
python -m pytest tests/ -q
```
Expected: all pass

**Step 6: Commit**

```bash
git add runner/single_runner.py tests/test_single_runner.py
git commit -m "feat: inject Qwen context into Tier 3 single-pass prompts"
```

---

## Task 6: Update main.py — Tier 4 copy + wire qwen_dir through run_cycle

**Files:**
- Modify: `runner/main.py`
- Modify: `runner/tier_config.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing tests** (add to `tests/test_main.py`)

```python
# Add to tests/test_main.py
from runner.main import run_cycle, copy_qwen_tier4


def make_qwen_jsonl(path, questions):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")


def test_tier4_copies_qwen_answers(tmp_path):
    """Tier 4 task: Qwen answers copied to final_results, no API calls."""
    test_dir = tmp_path / "TEST"
    qwen_dir = tmp_path / "qwen"
    make_test_jsonl(test_dir / "MedTeach.jsonl", [
        {"question": "Q?", "answer": "", "other": {"id": 1}}
    ])
    make_qwen_jsonl(qwen_dir / "MedTeach.jsonl", [
        {"question": "Q?", "answer": "Qwen answer here", "other": {"id": 1}}
    ])

    tier_state = {"MedTeach": 97}
    mock_anthropic = MagicMock()
    mock_deepseek = MagicMock()

    run_cycle(
        test_dir=str(test_dir),
        cycle_dir=str(tmp_path / "cycle1"),
        tier_state=tier_state,
        anthropic_client=mock_anthropic,
        deepseek_client=mock_deepseek,
        qwen_dir=str(qwen_dir),
    )

    result_path = tmp_path / "cycle1" / "final_results" / "MedTeach_results.jsonl"
    assert result_path.exists()
    with open(result_path) as f:
        record = json.loads(f.readline())
    assert record["answer"] == "Qwen answer here"
    mock_anthropic.query.assert_not_called()
    mock_deepseek.query.assert_not_called()


def test_tier4_skips_gracefully_if_qwen_missing(tmp_path):
    """Tier 4 task with no Qwen file → skip silently, no results file."""
    test_dir = tmp_path / "TEST"
    qwen_dir = tmp_path / "qwen"  # empty dir
    qwen_dir.mkdir()
    make_test_jsonl(test_dir / "MedTeach.jsonl", [
        {"question": "Q?", "answer": "", "other": {"id": 1}}
    ])

    tier_state = {"MedTeach": 97}
    mock_anthropic = MagicMock()
    mock_deepseek = MagicMock()

    run_cycle(
        test_dir=str(test_dir),
        cycle_dir=str(tmp_path / "cycle1"),
        tier_state=tier_state,
        anthropic_client=mock_anthropic,
        deepseek_client=mock_deepseek,
        qwen_dir=str(qwen_dir),
    )

    result_path = tmp_path / "cycle1" / "final_results" / "MedTeach_results.jsonl"
    assert not result_path.exists()
```

**Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_main.py -v -k "tier4_copies or tier4_skips"
```
Expected: `TypeError: run_cycle() got an unexpected keyword argument 'qwen_dir'`

**Step 3: Add `QWEN_DIR` to `runner/tier_config.py`**

Add at bottom of file:
```python
QWEN_DIR = "../SUBMIT/results-qwen-wxw-20251215/MedBench_LLM"
```

**Step 4: Update `runner/main.py`**

Add imports:
```python
from .qwen_loader import load_qwen_answers
from .tier_config import QWEN_DIR
```

Update `run_cycle` signature and add Tier 4 copy logic:

```python
def run_cycle(
    test_dir: str,
    cycle_dir: str,
    tier_state: Dict[str, float],
    anthropic_client: AnthropicClient,
    deepseek_client: DeepSeekClient,
    qwen_dir: str = QWEN_DIR,
):
    test_path = Path(test_dir)
    cycle_path = Path(cycle_dir)
    raw_votes_dir = cycle_path / "raw_votes"
    results_dir = cycle_path / "final_results"

    for jsonl_file in sorted(test_path.glob("*.jsonl")):
        task_name = jsonl_file.stem
        tier = get_tier(task_name, tier_state)
        format_type = get_format_type(task_name)

        output_path = results_dir / f"{task_name}_results.jsonl"
        if output_path.exists():
            print(f"[SKIP] {task_name} (already done)")
            continue

        if tier == 4:
            qwen_answers = load_qwen_answers(qwen_dir, task_name)
            if qwen_answers is None:
                print(f"[SKIP] {task_name} (Tier 4, no Qwen file)")
                continue
            questions = load_questions(str(jsonl_file))
            save_results(output_path, questions, qwen_answers)
            print(f"[Tier 4] {task_name} (copied {len(qwen_answers)} Qwen answers)")
            continue

        print(f"[Tier {tier}] {task_name} (format={format_type})")
        questions = load_questions(str(jsonl_file))
        qwen_answers = load_qwen_answers(qwen_dir, task_name)
        models = get_models(tier)

        if tier == 1:
            answers = run_tier1(
                questions=questions,
                task_name=task_name,
                format_type=format_type,
                ds_client=deepseek_client,
                ds_model=models["deepseek"]["model_id"],
                opus_client=anthropic_client,
                opus_model=models["claude_tiebreak"]["model_id"],
                raw_votes_dir=raw_votes_dir,
                qwen_answers=qwen_answers,
            )
        elif tier == 2:
            answers = run_tier2(
                questions=questions,
                task_name=task_name,
                format_type=format_type,
                ds_client=deepseek_client,
                ds_model=models["deepseek"]["model_id"],
                sonnet_client=anthropic_client,
                sonnet_model=models["claude_anchor"]["model_id"],
                raw_votes_dir=raw_votes_dir,
                qwen_answers=qwen_answers,
            )
        else:  # tier == 3
            answers = run_tier3(
                questions=questions,
                client=anthropic_client,
                model=models["claude"]["model_id"],
                qwen_answers=qwen_answers,
                format_type=format_type,
            )

        save_results(output_path, questions, answers)
        print(f"  Saved {len(answers)} answers -> {output_path}")
```

Also update `main()` to pass `--qwen-dir` CLI arg:
```python
parser.add_argument("--qwen-dir", default=QWEN_DIR, help="Path to Qwen cycle0 results dir")
# ...
run_cycle(..., qwen_dir=args.qwen_dir)
```

**Step 5: Update existing test that checked Tier 4 was skipped**

In `tests/test_main.py`, update `test_run_cycle_skips_tier4` to reflect new behavior (Tier 4 copies Qwen when available, or skips if not):

```python
def test_run_cycle_skips_tier4_when_no_qwen(tmp_path):
    """Tier 4 task with no Qwen dir → skip silently."""
    test_dir = tmp_path / "TEST"
    make_test_jsonl(test_dir / "MedTeach.jsonl", [
        {"question": "Q?", "answer": "", "other": {}}
    ])
    tier_state = {"MedTeach": 97}
    mock_anthropic = MagicMock()
    mock_deepseek = MagicMock()

    run_cycle(
        test_dir=str(test_dir),
        cycle_dir=str(tmp_path / "cycle1"),
        tier_state=tier_state,
        anthropic_client=mock_anthropic,
        deepseek_client=mock_deepseek,
        qwen_dir=str(tmp_path / "no_such_dir"),
    )

    mock_anthropic.query.assert_not_called()
    mock_deepseek.query.assert_not_called()
    assert not (tmp_path / "cycle1" / "final_results" / "MedTeach_results.jsonl").exists()
```

**Step 6: Run all tests**

```bash
python -m pytest tests/ -v
```
Expected: all pass

**Step 7: Commit**

```bash
git add runner/main.py runner/tier_config.py tests/test_main.py
git commit -m "feat: Tier 4 copies Qwen answers; wire qwen_dir through run_cycle"
```

---

## Task 7: Smoke test end-to-end

**Step 1: Run a Tier 3 task with real Qwen context**

```bash
rm -rf cycle1/
set -a && source .env && set +a
python -m runner.main --task MedSynonym --cycle 1
```

Expected output:
```
[Tier 3] MedSynonym (format=freeform)
  Saved 30 answers -> cycle1/final_results/MedSynonym_results.jsonl
```

**Step 2: Verify Qwen context injected**

```bash
python3 -c "
import json
with open('cycle1/final_results/MedSynonym_results.jsonl') as f:
    d = json.loads(f.readline())
errors = sum(1 for line in open('cycle1/final_results/MedSynonym_results.jsonl') if 'ERROR' in line)
print(f'Errors: {errors}/30')
print('Sample answer:', d['answer'][:100])
"
```
Expected: 0 errors, meaningful Chinese answer.

**Step 3: Verify Tier 4 copy works**

```bash
python -m runner.main --task MedTeach --cycle 1
```
Expected: `[Tier 4] MedTeach (copied 30 Qwen answers)` — no API calls made.

**Step 4: Check Tier 4 output**

```bash
python3 -c "
import json
with open('cycle1/final_results/MedTeach_results.jsonl') as f:
    d = json.loads(f.readline())
print('MedTeach Qwen answer:', d['answer'][:80])
"
```
Expected: Qwen answer content from `../SUBMIT/results-qwen-wxw-20251215/MedBench_LLM/MedTeach.jsonl`.

**Step 5: Final full test suite**

```bash
python -m pytest tests/ -q
```
Expected: all pass with no regressions.

**Step 6: Commit**

```bash
git add cycle1/  # only if you want to keep smoke test outputs
git commit -m "feat: Qwen integration complete — context injection, Tier 4 copy, vote update"
```

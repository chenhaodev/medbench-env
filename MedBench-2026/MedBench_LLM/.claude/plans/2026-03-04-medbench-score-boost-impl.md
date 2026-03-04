# MedBench Score Boost — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 4-tier multi-model ensemble runner that replaces single-pass submit_answers.py for targeted score improvement on MedBench.

**Architecture:** Tasks are routed by their cycle0 score (read from tier_state.json) to one of 4 tiers. Tier 1 & 2 run multi-model ensembles with Claude-anchored voting. Tier 3 uses a single Claude Sonnet 4.5 call. Tier 4 is skipped. Raw votes are saved for future Dawid-Skene calibration.

**Tech Stack:** Python 3.10+, `anthropic` SDK (Claude models), `openai` SDK (DeepSeek via compatible API), `concurrent.futures` for parallelism, `tqdm` for progress.

**Environment variables required:**
- `ANTHROPIC_API_KEY` — for Claude Opus 4.6, Sonnet 4.6, Sonnet 4.5
- `DEEPSEEK_API_KEY` — for DeepSeek-R1 and DeepSeek-V3

---

## Task 1: Scaffold + tier_state.json + test setup

**Files:**
- Create: `runner/__init__.py`
- Create: `tier_state.json`
- Create: `tests/__init__.py`
- Create: `tests/test_tier_config.py`

**Step 1: Create runner package**

```bash
mkdir -p runner tests
touch runner/__init__.py tests/__init__.py
```

**Step 2: Create tier_state.json**

```json
{
  "DDx-advanced": 33,
  "MedOutcome": 39,
  "MedReportQC": 39,
  "MedDiffer": 48,
  "MedLitQA": 50,
  "MedExplain": 55,
  "MedChartQC": 57,
  "MedInsureCalc": 59,
  "MedHC": 59,
  "MedSafety": 60,
  "MedPrimary": 62,
  "MedEthics": 63,
  "CMB-Clin-extended": 63,
  "MedPopular": 64,
  "MedSummary": 65,
  "MedCare": 66,
  "MedSpeQA": 68,
  "MedPHM": 69,
  "MedTerm": 69,
  "MedAnalysis": 61,
  "MedRehab": 63,
  "MedMC": 66,
  "SMDoc": 65,
  "MedPsychCare": 66,
  "MedRxCheck_MSQ": 58,
  "MedRxCheck_SCQ": 58,
  "MedRxCheck_SQ": 58,
  "MedDiag": 73,
  "MedSynonym": 75,
  "MedRecordGen": 76,
  "MedRxPlan": 78,
  "MedPsychQA": 72,
  "MedExam": 80,
  "MedHG": 81,
  "MedTreat": 81,
  "MedPathQC": 82,
  "MedInsureCheck": 84,
  "MedTeach": 97
}
```

**Step 3: Install anthropic SDK**

```bash
pip install anthropic
```

Verify: `python -c "import anthropic; print('ok')"`

**Step 4: Commit scaffold**

```bash
git add runner/ tests/ tier_state.json
git commit -m "feat: scaffold runner package and tier_state.json"
```

---

## Task 2: runner/tier_config.py

**Files:**
- Create: `runner/tier_config.py`
- Test: `tests/test_tier_config.py`

**Step 1: Write failing tests**

```python
# tests/test_tier_config.py
import json
import pytest
from runner.tier_config import get_tier, get_format_type, get_models, TIER_THRESHOLDS

def test_tier1_task():
    assert get_tier("DDx-advanced", {"DDx-advanced": 33}) == 1

def test_tier2_task():
    assert get_tier("MedHC", {"MedHC": 59}) == 2

def test_tier3_task():
    assert get_tier("MedDiag", {"MedDiag": 73}) == 3

def test_tier4_task():
    assert get_tier("MedTeach", {"MedTeach": 97}) == 4

def test_unknown_task_defaults_tier2():
    assert get_tier("UnknownTask", {}) == 2

def test_format_multi_select():
    assert get_format_type("DDx-advanced") == "multi_select"

def test_format_freeform():
    assert get_format_type("MedHC") == "freeform"

def test_format_mcq():
    assert get_format_type("MedExam") == "mcq"

def test_tier1_models():
    models = get_models(1)
    assert "deepseek" in models
    assert "claude_tiebreak" in models
    assert models["deepseek"]["runs"] == 3

def test_tier2_models():
    models = get_models(2)
    assert "deepseek" in models
    assert "claude_anchor" in models
    assert models["deepseek"]["runs"] == 2
```

**Step 2: Run tests — expect FAIL**

```bash
cd /Users/chenhao/MyMedBench/medbench-env/MedBench-2026/MedBench_LLM
python -m pytest tests/test_tier_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'runner.tier_config'`

**Step 3: Implement tier_config.py**

```python
# runner/tier_config.py
from typing import Dict, Any

TIER_THRESHOLDS = {1: 55, 2: 70, 3: 80}

# Format types: mcq=single letter, multi_select=comma-separated letters,
# freeform=Chinese text, json_struct=JSON output
TASK_FORMATS: Dict[str, str] = {
    "DDx-advanced": "multi_select",
    "MedOutcome": "freeform",
    "MedReportQC": "freeform",
    "MedDiffer": "freeform",
    "MedLitQA": "mcq",
    "MedExplain": "freeform",
    "MedChartQC": "freeform",
    "MedInsureCalc": "json_struct",
    "MedHC": "freeform",
    "MedSafety": "mcq",
    "MedPrimary": "freeform",
    "MedEthics": "mcq",
    "CMB-Clin-extended": "freeform",
    "MedPopular": "freeform",
    "MedSummary": "freeform",
    "MedCare": "freeform",
    "MedSpeQA": "freeform",
    "MedPHM": "freeform",
    "MedTerm": "freeform",
    "MedAnalysis": "freeform",
    "MedRehab": "freeform",
    "MedMC": "mcq",
    "SMDoc": "freeform",
    "MedPsychCare": "freeform",
    "MedRxCheck_MSQ": "multi_select",
    "MedRxCheck_SCQ": "mcq",
    "MedRxCheck_SQ": "freeform",
    "MedDiag": "freeform",
    "MedSynonym": "freeform",
    "MedRecordGen": "freeform",
    "MedRxPlan": "freeform",
    "MedPsychQA": "freeform",
    "MedExam": "mcq",
    "MedHG": "freeform",
    "MedTreat": "freeform",
    "MedPathQC": "freeform",
    "MedInsureCheck": "freeform",
    "MedTeach": "freeform",
}

MODELS = {
    1: {
        "deepseek": {"model_id": "deepseek-reasoner", "runs": 3},
        "claude_tiebreak": {"model_id": "claude-opus-4-6"},
    },
    2: {
        "deepseek": {"model_id": "deepseek-chat", "runs": 2},
        "claude_anchor": {"model_id": "claude-sonnet-4-6"},
    },
    3: {
        "claude": {"model_id": "claude-sonnet-4-5-20251001"},
    },
}


def get_tier(task_name: str, tier_state: Dict[str, float]) -> int:
    score = tier_state.get(task_name)
    if score is None:
        return 2  # default to Tier 2 for unknown tasks
    if score < TIER_THRESHOLDS[1]:
        return 1
    if score < TIER_THRESHOLDS[2]:
        return 2
    if score < TIER_THRESHOLDS[3]:
        return 3
    return 4


def get_format_type(task_name: str) -> str:
    return TASK_FORMATS.get(task_name, "freeform")


def get_models(tier: int) -> Dict[str, Any]:
    return MODELS.get(tier, MODELS[2])
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_tier_config.py -v
```

Expected: all 10 tests PASS.

**Step 5: Commit**

```bash
git add runner/tier_config.py tests/test_tier_config.py
git commit -m "feat: add tier_config with task routing and format types"
```

---

## Task 3: runner/clients.py — API wrappers

**Files:**
- Create: `runner/clients.py`
- Test: `tests/test_clients.py`

**Step 1: Write failing tests**

```python
# tests/test_clients.py
from unittest.mock import patch, MagicMock
import pytest
from runner.clients import AnthropicClient, DeepSeekClient

def test_anthropic_client_returns_string():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="test answer")]
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.return_value = mock_response
        client = AnthropicClient(api_key="test")
        result = client.query("What is 1+1?", model="claude-sonnet-4-6")
        assert result == "test answer"

def test_anthropic_client_error_returns_error_string():
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.side_effect = Exception("API error")
        client = AnthropicClient(api_key="test")
        result = client.query("question", model="claude-sonnet-4-6")
        assert result.startswith("ERROR:")

def test_deepseek_client_returns_string():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="deepseek answer"))]
    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.return_value = mock_response
        client = DeepSeekClient(api_key="test")
        result = client.query("What is 1+1?", model="deepseek-chat")
        assert result == "deepseek answer"

def test_deepseek_client_error_returns_error_string():
    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.side_effect = Exception("timeout")
        client = DeepSeekClient(api_key="test")
        result = client.query("question", model="deepseek-chat")
        assert result.startswith("ERROR:")
```

**Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_clients.py -v
```

Expected: `ModuleNotFoundError: No module named 'runner.clients'`

**Step 3: Implement clients.py**

```python
# runner/clients.py
import anthropic
import openai


class AnthropicClient:
    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def query(self, question: str, model: str, max_tokens: int = 2048) -> str:
        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": question}],
            )
            return response.content[0].text
        except Exception as e:
            return f"ERROR: {e}"


class DeepSeekClient:
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    def __init__(self, api_key: str):
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=self.DEEPSEEK_BASE_URL,
        )

    def query(self, question: str, model: str, max_tokens: int = 2048) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": question}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {e}"
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_clients.py -v
```

Expected: all 4 tests PASS.

**Step 5: Commit**

```bash
git add runner/clients.py tests/test_clients.py
git commit -m "feat: add Anthropic and DeepSeek client wrappers"
```

---

## Task 4: runner/aggregator.py — voting logic

**Files:**
- Create: `runner/aggregator.py`
- Test: `tests/test_aggregator.py`

**Step 1: Write failing tests**

```python
# tests/test_aggregator.py
import pytest
from runner.aggregator import normalize_answer, majority_vote, claude_anchored_vote_tier1, claude_anchored_vote_tier2

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
    # tie: returns first occurrence
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
    # freeform: never override Claude (can't compare text meaningfully)
    result = claude_anchored_vote_tier2(
        ds_answers=["some long text", "some long text"],
        claude_answer="different text",
        format_type="freeform"
    )
    assert result == "different text"
```

**Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_aggregator.py -v
```

**Step 3: Implement aggregator.py**

```python
# runner/aggregator.py
import re
from collections import Counter
from typing import List


def normalize_answer(answer: str, format_type: str) -> str:
    if format_type == "mcq":
        return re.sub(r"[^a-zA-Z]", "", answer).lower()[:1]
    if format_type == "multi_select":
        letters = re.findall(r"[a-zA-Z]", answer)
        return ",".join(sorted(set(l.lower() for l in letters)))
    # freeform / json_struct: just strip whitespace
    return answer.strip()


def majority_vote(answers: List[str], format_type: str) -> str:
    normalized = [normalize_answer(a, format_type) for a in answers]
    counts = Counter(normalized)
    return counts.most_common(1)[0][0]


def claude_anchored_vote_tier1(
    ds_answers: List[str], claude_answer: str, format_type: str
) -> str:
    """Tier 1: DS unanimous override only. Claude wins otherwise."""
    if format_type == "freeform":
        return claude_answer.strip()

    norm_ds = [normalize_answer(a, format_type) for a in ds_answers]
    norm_claude = normalize_answer(claude_answer, format_type)

    ds_unanimous = len(set(norm_ds)) == 1
    ds_differs_from_claude = ds_unanimous and (norm_ds[0] != norm_claude)

    if ds_differs_from_claude:
        return norm_ds[0]
    return norm_claude


def claude_anchored_vote_tier2(
    ds_answers: List[str], claude_answer: str, format_type: str
) -> str:
    """Tier 2: both DS must agree AND differ from Claude to override."""
    if format_type in ("freeform", "json_struct"):
        return claude_answer.strip()

    norm_ds = [normalize_answer(a, format_type) for a in ds_answers]
    norm_claude = normalize_answer(claude_answer, format_type)

    both_agree = len(set(norm_ds)) == 1
    differs = both_agree and (norm_ds[0] != norm_claude)

    if differs:
        return norm_ds[0]
    return norm_claude
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_aggregator.py -v
```

Expected: all 11 tests PASS.

**Step 5: Commit**

```bash
git add runner/aggregator.py tests/test_aggregator.py
git commit -m "feat: add aggregator with Claude-anchored voting for Tier 1 and 2"
```

---

## Task 5: runner/multi_model_runner.py — Tier 1 & 2

**Files:**
- Create: `runner/multi_model_runner.py`
- Test: `tests/test_multi_model_runner.py`

**Step 1: Write failing tests**

```python
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


def make_mock_anthropic(answer: str):
    client = MagicMock()
    client.query.return_value = answer
    return client


def make_mock_deepseek(answer: str):
    client = MagicMock()
    client.query.return_value = answer
    return client


def test_tier1_ds_unanimous_uses_ds_answer(tmp_path):
    ds_client = make_mock_deepseek("B")   # always returns B
    opus_client = make_mock_anthropic("A")  # would return A but DS unanimous

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
    # DS unanimous (B,B,B) differs from Claude (A) → use DS
    assert all(a == "b" for a in answers)
    # Opus should NOT be called (DS unanimous)
    opus_client.query.assert_not_called()


def test_tier1_ds_not_unanimous_calls_opus(tmp_path):
    ds_client = MagicMock()
    ds_client.query.side_effect = ["A", "B", "A", "A", "B", "A"]  # alternating, not unanimous
    opus_client = make_mock_anthropic("C")

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


def test_tier2_ds_override_when_unanimous(tmp_path):
    sonnet_client = make_mock_anthropic("A")
    ds_client = make_mock_deepseek("B")  # both DS return B

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
    ds_client = make_mock_deepseek("A")
    opus_client = make_mock_anthropic("A")

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
    # Check raw vote files exist
    vote_dir = tmp_path / "DDx-advanced"
    assert vote_dir.exists()
    vote_files = list(vote_dir.glob("*.jsonl"))
    assert len(vote_files) >= 3  # at least 3 DS runs
```

**Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_multi_model_runner.py -v
```

**Step 3: Implement multi_model_runner.py**

```python
# runner/multi_model_runner.py
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any

from .aggregator import claude_anchored_vote_tier1, claude_anchored_vote_tier2, normalize_answer
from .clients import AnthropicClient, DeepSeekClient


def _save_raw_votes(raw_votes_dir: Path, task_name: str, run_name: str, answers: List[str]):
    task_dir = raw_votes_dir / task_name
    task_dir.mkdir(parents=True, exist_ok=True)
    out_file = task_dir / f"{run_name}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for answer in answers:
            f.write(json.dumps({"answer": answer}, ensure_ascii=False) + "\n")


def _run_model_on_questions(
    questions: List[Dict], client, model: str
) -> List[str]:
    answers = []
    for item in questions:
        answer = client.query(item["question"], model=model)
        answers.append(answer)
    return answers


def run_tier1(
    questions: List[Dict[str, Any]],
    task_name: str,
    format_type: str,
    ds_client: DeepSeekClient,
    ds_model: str,
    opus_client: AnthropicClient,
    opus_model: str,
    raw_votes_dir: Path,
) -> List[str]:
    """Run 3x DeepSeek-R1. If unanimous and differs, use DS. Else call Opus."""
    # Run 3 DS passes in parallel
    ds_runs: List[List[str]] = [[], [], []]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_model_on_questions, questions, ds_client, ds_model): i
            for i in range(3)
        }
        for future in as_completed(futures):
            run_idx = futures[future]
            ds_runs[run_idx] = future.result()

    for i, run_answers in enumerate(ds_runs):
        _save_raw_votes(raw_votes_dir, task_name, f"deepseek-r1-run{i+1}", run_answers)

    final_answers = []
    opus_answers: List[str] = []

    for q_idx in range(len(questions)):
        ds_q_answers = [ds_runs[i][q_idx] for i in range(3)]
        norm_ds = [normalize_answer(a, format_type) for a in ds_q_answers]
        ds_unanimous = len(set(norm_ds)) == 1

        if ds_unanimous and format_type not in ("freeform", "json_struct"):
            # DS unanimous: use DS, skip Opus
            final_answers.append(norm_ds[0])
            opus_answers.append("")  # not called
        else:
            # Need Opus as tiebreaker
            opus_answer = opus_client.query(questions[q_idx]["question"], model=opus_model)
            opus_answers.append(opus_answer)
            result = claude_anchored_vote_tier1(
                ds_answers=ds_q_answers,
                claude_answer=opus_answer,
                format_type=format_type,
            )
            final_answers.append(result)

    _save_raw_votes(raw_votes_dir, task_name, "opus-tiebreak", opus_answers)
    return final_answers


def run_tier2(
    questions: List[Dict[str, Any]],
    task_name: str,
    format_type: str,
    ds_client: DeepSeekClient,
    ds_model: str,
    sonnet_client: AnthropicClient,
    sonnet_model: str,
    raw_votes_dir: Path,
) -> List[str]:
    """Run Claude Sonnet (anchor) + 2x DS-V3. DS unanimous override only."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_sonnet = executor.submit(_run_model_on_questions, questions, sonnet_client, sonnet_model)
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
        result = claude_anchored_vote_tier2(
            ds_answers=[ds1_answers[q_idx], ds2_answers[q_idx]],
            claude_answer=sonnet_answers[q_idx],
            format_type=format_type,
        )
        final_answers.append(result)

    return final_answers
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_multi_model_runner.py -v
```

**Step 5: Commit**

```bash
git add runner/multi_model_runner.py tests/test_multi_model_runner.py
git commit -m "feat: add multi-model runner for Tier 1 and 2 with parallel execution"
```

---

## Task 6: runner/single_runner.py — Tier 3

**Files:**
- Create: `runner/single_runner.py`
- Test: `tests/test_single_runner.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_single_runner.py -v
```

**Step 3: Implement single_runner.py**

```python
# runner/single_runner.py
from typing import List, Dict, Any
from .clients import AnthropicClient


def run_tier3(
    questions: List[Dict[str, Any]],
    client: AnthropicClient,
    model: str,
) -> List[str]:
    """Single-pass Claude Sonnet 4.5 for Tier 3 tasks."""
    answers = []
    for item in questions:
        answer = client.query(item["question"], model=model)
        answers.append(answer)
    return answers
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_single_runner.py -v
```

**Step 5: Commit**

```bash
git add runner/single_runner.py tests/test_single_runner.py
git commit -m "feat: add single_runner for Tier 3"
```

---

## Task 7: runner/main.py — orchestrator

**Files:**
- Create: `runner/main.py`
- Test: `tests/test_main.py`

**Step 1: Write failing tests**

```python
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

    # No API calls should be made for Tier 4
    mock_anthropic.query.assert_not_called()
    mock_deepseek.query.assert_not_called()
    # No output file
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
```

**Step 2: Run tests — expect FAIL**

```bash
python -m pytest tests/test_main.py -v
```

**Step 3: Implement main.py**

```python
# runner/main.py
import json
import os
import argparse
from pathlib import Path
from typing import Dict

from .clients import AnthropicClient, DeepSeekClient
from .tier_config import get_tier, get_format_type, get_models
from .multi_model_runner import run_tier1, run_tier2
from .single_runner import run_tier3

TIER_MODELS = {
    1: {"ds_model": "deepseek-reasoner", "claude_model": "claude-opus-4-6"},
    2: {"ds_model": "deepseek-chat",     "claude_model": "claude-sonnet-4-6"},
    3: {"claude_model": "claude-sonnet-4-5-20251001"},
}


def load_questions(filepath: str):
    questions = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


def save_results(output_path: Path, questions: list, answers: list):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for item, answer in zip(questions, answers):
            result = {"question": item["question"], "answer": answer, "other": item.get("other", {})}
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def run_cycle(
    test_dir: str,
    cycle_dir: str,
    tier_state: Dict[str, float],
    anthropic_client: AnthropicClient,
    deepseek_client: DeepSeekClient,
):
    test_path = Path(test_dir)
    cycle_path = Path(cycle_dir)
    raw_votes_dir = cycle_path / "raw_votes"
    results_dir = cycle_path / "final_results"

    for jsonl_file in sorted(test_path.glob("*.jsonl")):
        task_name = jsonl_file.stem
        tier = get_tier(task_name, tier_state)
        format_type = get_format_type(task_name)

        if tier == 4:
            print(f"[SKIP] {task_name} (Tier 4, score={tier_state.get(task_name, '?')})")
            continue

        print(f"[Tier {tier}] {task_name} (format={format_type})")
        questions = load_questions(str(jsonl_file))

        if tier == 1:
            answers = run_tier1(
                questions=questions,
                task_name=task_name,
                format_type=format_type,
                ds_client=deepseek_client,
                ds_model=TIER_MODELS[1]["ds_model"],
                opus_client=anthropic_client,
                opus_model=TIER_MODELS[1]["claude_model"],
                raw_votes_dir=raw_votes_dir,
            )
        elif tier == 2:
            answers = run_tier2(
                questions=questions,
                task_name=task_name,
                format_type=format_type,
                ds_client=deepseek_client,
                ds_model=TIER_MODELS[2]["ds_model"],
                sonnet_client=anthropic_client,
                sonnet_model=TIER_MODELS[2]["claude_model"],
                raw_votes_dir=raw_votes_dir,
            )
        else:  # tier == 3
            answers = run_tier3(
                questions=questions,
                client=anthropic_client,
                model=TIER_MODELS[3]["claude_model"],
            )

        output_path = results_dir / f"{task_name}_results.jsonl"
        save_results(output_path, questions, answers)
        print(f"  ✓ Saved {len(answers)} answers → {output_path}")


def main():
    parser = argparse.ArgumentParser(description="MedBench multi-model ensemble runner")
    parser.add_argument("--test-dir", default="TEST")
    parser.add_argument("--cycle", type=int, default=1)
    parser.add_argument("--tier-state", default="tier_state.json")
    parser.add_argument("--task", type=str, help="Run a single task only")
    args = parser.parse_args()

    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    deepseek_key = os.environ["DEEPSEEK_API_KEY"]

    with open(args.tier_state, encoding="utf-8") as f:
        tier_state = json.load(f)

    anthropic_client = AnthropicClient(api_key=anthropic_key)
    deepseek_client = DeepSeekClient(api_key=deepseek_key)

    test_dir = args.test_dir
    if args.task:
        # Single-task mode: temporarily filter
        from pathlib import Path as P
        all_files = list(P(args.test_dir).glob("*.jsonl"))
        matching = [f for f in all_files if f.stem == args.task]
        if not matching:
            print(f"Task '{args.task}' not found in {args.test_dir}")
            return
        import tempfile, shutil
        tmp = tempfile.mkdtemp()
        shutil.copy(matching[0], tmp)
        test_dir = tmp

    run_cycle(
        test_dir=test_dir,
        cycle_dir=f"cycle{args.cycle}",
        tier_state=tier_state,
        anthropic_client=anthropic_client,
        deepseek_client=deepseek_client,
    )


if __name__ == "__main__":
    main()
```

**Step 4: Run tests — expect PASS**

```bash
python -m pytest tests/test_main.py -v
```

**Step 5: Commit**

```bash
git add runner/main.py tests/test_main.py
git commit -m "feat: add main orchestrator with 4-tier routing"
```

---

## Task 8: Full test suite + smoke test

**Step 1: Run full test suite**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: all tests PASS.

**Step 2: Smoke test single task (no API calls)**

Test the CLI help works:
```bash
python -m runner.main --help
```

Expected: prints usage without errors.

**Step 3: Smoke test Tier 3 with 1 question (uses real API)**

```bash
export ANTHROPIC_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key
python -m runner.main --task MedDiag --cycle 1
```

Expected:
- `[Tier 3] MedDiag (format=freeform)` printed
- `cycle1/final_results/MedDiag_results.jsonl` created with 30 answers

**Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete MedBench 4-tier ensemble runner (cycle 1 ready)"
```

---

## Usage After Implementation

### Run all tasks for a full cycle submission:
```bash
python -m runner.main --cycle 1
```

### Run a single weak task to test:
```bash
python -m runner.main --task DDx-advanced --cycle 1
```

### After submission, update tier_state.json:
Edit `tier_state.json` with new scores. Tasks that crossed a tier boundary will automatically get upgraded/downgraded treatment next cycle.

### Copy results for submission:
```bash
cp cycle1/final_results/* results/
```
Then submit via existing MedBench submission process.

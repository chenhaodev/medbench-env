# runner/multi_model_runner.py
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional

from .aggregator import claude_anchored_vote_tier1, claude_anchored_vote_tier2, normalize_answer, is_error_answer
from .clients import AnthropicClient, DeepSeekClient
from .prompt_builder import build_prompt


def _save_raw_votes(raw_votes_dir: Path, task_name: str, run_name: str, answers: List):
    task_dir = raw_votes_dir / task_name
    task_dir.mkdir(parents=True, exist_ok=True)
    out_file = task_dir / f"{run_name}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for answer in answers:
            if answer is not None:
                f.write(json.dumps({"answer": answer}, ensure_ascii=False) + "\n")


def _run_model_on_questions(
    questions: List[Dict], client, model: str
) -> List[str]:
    answers = []
    for item in questions:
        answer = client.query(item["question"], model=model)
        answers.append(answer)
    return answers


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
            run_idx = futures[future]
            ds_runs[run_idx] = future.result()

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
        }
        if qwen_ans and not is_error_answer(qwen_ans):
            other["Qwen"] = qwen_ans
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

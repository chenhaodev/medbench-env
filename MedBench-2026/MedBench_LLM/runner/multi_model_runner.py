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

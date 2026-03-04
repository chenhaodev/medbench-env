# runner/main.py
import json
import os
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Dict

from .clients import AnthropicClient, DeepSeekClient
from .tier_config import get_tier, get_format_type, get_models
from .multi_model_runner import run_tier1, run_tier2
from .single_runner import run_tier3


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
            result = {
                "question": item["question"],
                "answer": answer,
                "other": item.get("other", {}),
            }
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
            )
        else:  # tier == 3
            answers = run_tier3(
                questions=questions,
                client=anthropic_client,
                model=models["claude"]["model_id"],
            )

        output_path = results_dir / f"{task_name}_results.jsonl"
        save_results(output_path, questions, answers)
        print(f"  Saved {len(answers)} answers -> {output_path}")


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
    tmp = None
    if args.task:
        all_files = list(Path(args.test_dir).glob("*.jsonl"))
        matching = [f for f in all_files if f.stem == args.task]
        if not matching:
            print(f"Task '{args.task}' not found in {args.test_dir}")
            return
        tmp = tempfile.mkdtemp()
        shutil.copy(matching[0], tmp)
        test_dir = tmp

    try:
        run_cycle(
            test_dir=test_dir,
            cycle_dir=f"cycle{args.cycle}",
            tier_state=tier_state,
            anthropic_client=anthropic_client,
            deepseek_client=deepseek_client,
        )
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

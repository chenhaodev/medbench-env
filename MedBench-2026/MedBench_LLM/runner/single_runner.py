# runner/single_runner.py
from typing import List, Dict, Any, Optional

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

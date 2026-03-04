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

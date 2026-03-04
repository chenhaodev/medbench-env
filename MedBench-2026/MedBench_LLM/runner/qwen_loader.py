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

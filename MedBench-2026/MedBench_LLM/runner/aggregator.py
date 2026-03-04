# runner/aggregator.py
import re
from collections import Counter
from typing import List


def normalize_answer(answer: str, format_type: str) -> str:
    if format_type == "mcq":
        letters = re.sub(r"[^a-zA-Z]", "", answer).lower()
        return letters[:1] if letters else ""
    if format_type == "multi_select":
        letters = re.findall(r"[a-zA-Z]", answer)
        return ",".join(sorted(set(l.lower() for l in letters)))
    # freeform / json_struct: just strip whitespace
    return answer.strip()


def is_error_answer(answer: str) -> bool:
    """Returns True if the answer is an API error response, not a model answer."""
    return answer.strip().startswith("ERROR:")


def majority_vote(answers: List[str], format_type: str) -> str:
    if not answers:
        return ""
    normalized = [normalize_answer(a, format_type) for a in answers]
    counts = Counter(normalized)
    return counts.most_common(1)[0][0]


def claude_anchored_vote_tier1(
    ds_answers: List[str], claude_answer: str, format_type: str
) -> str:
    """Tier 1: DS unanimous override only. Claude wins otherwise."""
    if format_type == "freeform":
        return claude_answer.strip()

    # Filter out error responses from DS answers
    valid_ds = [a for a in ds_answers if not is_error_answer(a)]
    if not valid_ds:
        return claude_answer.strip()  # all DS failed, use Claude

    norm_ds = [normalize_answer(a, format_type) for a in valid_ds]
    norm_claude = normalize_answer(claude_answer, format_type)

    ds_unanimous = len(set(norm_ds)) == 1
    ds_differs_from_claude = ds_unanimous and (norm_ds[0] != norm_claude)

    # Only override Claude if ALL original DS answers were valid and unanimous
    all_ds_valid = len(valid_ds) == len(ds_answers)
    if all_ds_valid and ds_differs_from_claude:
        return norm_ds[0]
    return norm_claude


def claude_anchored_vote_tier2(
    ds_answers: List[str], claude_answer: str, format_type: str
) -> str:
    """Tier 2: both DS must agree AND differ from Claude to override."""
    if format_type in ("freeform", "json_struct"):
        return claude_answer.strip()

    # Filter out error responses - if any DS answer is an error, Claude wins
    if any(is_error_answer(a) for a in ds_answers):
        return claude_answer.strip()

    norm_ds = [normalize_answer(a, format_type) for a in ds_answers]
    norm_claude = normalize_answer(claude_answer, format_type)

    both_agree = len(set(norm_ds)) == 1
    differs = both_agree and (norm_ds[0] != norm_claude)

    if differs:
        return norm_ds[0]
    return norm_claude

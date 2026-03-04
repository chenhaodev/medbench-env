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

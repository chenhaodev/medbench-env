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
    ds_answers: List[str],
    claude_answer: str,
    format_type: str,
    qwen_answer: str = "",
) -> str:
    """Tier 1: All challengers (DS×3 + Qwen) must be unanimous to override Claude."""
    if format_type == "freeform":
        return normalize_answer(claude_answer, format_type)

    # Build full challenger list; include Qwen only if valid (non-empty, non-error)
    challengers = list(ds_answers)
    if qwen_answer and not is_error_answer(qwen_answer):
        challengers.append(qwen_answer)

    valid = [a for a in challengers if not is_error_answer(a)]
    if not valid:
        return normalize_answer(claude_answer, format_type)

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
        return normalize_answer(claude_answer, format_type)

    if any(is_error_answer(a) for a in ds_answers):
        return normalize_answer(claude_answer, format_type)

    norm_ds = [normalize_answer(a, format_type) for a in ds_answers]
    norm_claude = normalize_answer(claude_answer, format_type)
    both_ds_agree = len(set(norm_ds)) == 1

    qwen_valid = bool(qwen_answer) and not is_error_answer(qwen_answer)

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

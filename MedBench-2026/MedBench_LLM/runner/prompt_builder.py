# runner/prompt_builder.py
from typing import Dict

FORMAT_SUFFIXES: Dict[str, str] = {
    "mcq":          "请只输出选项字母，例如：A",
    "freeform":     "请用中文详细回答",
    "multi_select": "请输出所有正确选项，例如：A, B, C",
    "json_struct":  "请只输出JSON格式答案",
}


def _is_error(answer: str) -> bool:
    return answer.strip().startswith("ERROR:")


def build_prompt(question: str, format_type: str, other_answers: Dict[str, str]) -> str:
    """Build a Claude prompt with optional context from other models.

    Args:
        question: The original question text.
        format_type: One of 'mcq', 'freeform', 'multi_select', 'json_struct'.
        other_answers: Dict mapping model label to answer string. Errors and
                       empty strings are silently excluded from the context block.

    Returns:
        A prompt string with format suffix appended. If valid context exists,
        a Chinese-language reference block is injected before the suffix.
    """
    suffix = FORMAT_SUFFIXES.get(format_type, FORMAT_SUFFIXES["freeform"])

    valid_context = {
        label: ans
        for label, ans in other_answers.items()
        if ans and ans.strip() and not _is_error(ans)
    }

    if not valid_context:
        return f"{question}\n\n{suffix}"

    context_lines = "\n".join(
        f"- {label}：{answer}" for label, answer in valid_context.items()
    )
    return (
        f"{question}\n\n"
        f"---\n"
        f"其他模型的参考回答：\n{context_lines}\n\n"
        f"请综合以上参考，给出你的最佳答案。\n{suffix}"
    )

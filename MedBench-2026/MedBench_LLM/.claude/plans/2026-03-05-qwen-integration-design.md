# Qwen Integration Design
**Date:** 2026-03-05
**Goal:** Use cycle0 Qwen answers (from `../SUBMIT/results-qwen-wxw-20251215/MedBench_LLM/`) as free votes and context signals to boost ensemble quality, with zero extra API cost.

---

## Context

- Qwen (cycle0) answers exist for all 38 tasks, perfectly aligned with TEST/ files by position and `other.id`
- Qwen answer format is sometimes messy (e.g., `<D>` instead of `D`, explanations instead of letters for MCQ tasks)
- Current runner already handles Tier 1–3 via Claude + DeepSeek ensemble; Tier 4 (≥80) was skipped entirely

---

## Two Integration Roles

### Role C: Tier 4 — Copy Qwen directly (zero API calls)
For all 6 tasks with score ≥ 80 (MedExam, MedHG, MedTreat, MedPathQC, MedInsureCheck, MedTeach):
- Copy Qwen's `{question, answer, other}` records verbatim to `cycle{N}/final_results/{task}_results.jsonl`
- If Qwen file missing → log warning and skip (no regression)

### Role A: Tier 1/2/3 — Qwen as context + vote

**Claude is a synthesizer, not just a voter.** When Claude is called, it sees other models' answers as context, enabling it to produce a more informed final answer.

---

## Prompt Design (prompt_builder.py)

For every Claude call, the prompt is structured as:

```
{original_question}

---
其他模型的参考回答：
{model_label}: {answer}
...

请综合以上参考，给出你的最佳答案。
{format_suffix}
```

Where `{format_suffix}` is injected as before (e.g., "请只输出选项字母，例如：A").

If no other-model answers are available (all errored), fall back to plain question prompt.

---

## Tier 1 (score < 55): DS-R1 ×3 + Qwen context + Claude Opus synthesizer

1. Run DS-R1 ×3 in parallel → `[ds1, ds2, ds3]`
2. Load Qwen answer → `qwen`
3. Normalize all four answers with `normalize_answer()`
4. Filter out ERROR responses
5. **If all 4 valid votes unanimously agree** → use that answer, **skip Claude call** (cost saving)
6. **Otherwise** → build context prompt `[ds1, ds2, ds3, qwen]` + call Claude Opus as synthesizer
7. Claude's output is the final answer (Claude sees full context, not just a tiebreak)

Applies to: MCQ and multi_select format tasks only. Freeform tasks: Claude receives `[ds1, ds2, ds3, qwen]` as context but Claude always called.

---

## Tier 2 (55–70): DS-V3 ×2 + Qwen context + Claude Opus anchor

1. Run Claude Opus + DS-V3 ×2 in parallel (existing)
2. Load Qwen answer
3. Claude prompt includes `[ds1, ds2, qwen]` as context → Claude produces an **informed** answer
4. For MCQ/multi_select: DS override requires **3-way agreement** (both DS + Qwen agree AND differ from Claude's raw pick)
5. For freeform/json_struct: Claude's context-informed answer always wins

---

## Tier 3 (70–80): Single Claude pass with Qwen context

- Load Qwen answer → inject as context into Claude's prompt
- Zero extra API calls — Qwen context is free
- Claude produces a better answer by seeing Qwen's reference response

---

## File Changes

| File | Change |
|------|--------|
| `runner/qwen_loader.py` | NEW: `load_qwen_answers(qwen_dir, task_name) → List[str] \| None` |
| `runner/prompt_builder.py` | NEW: `build_prompt(question, format_type, other_answers) → str` |
| `runner/aggregator.py` | UPDATE: `claude_anchored_vote_tier1/2` accept `qwen_answer` param |
| `runner/multi_model_runner.py` | UPDATE: load Qwen, pass context to Claude calls |
| `runner/single_runner.py` | UPDATE: inject Qwen context into Tier 3 prompt |
| `runner/main.py` | UPDATE: Tier 4 copy + pass `qwen_dir` to `run_cycle` |
| `runner/tier_config.py` | ADD: `QWEN_DIR` constant |

---

## Format Suffix Map (unchanged)

```python
FORMAT_SUFFIXES = {
    "mcq":          "请只输出选项字母，例如：A",
    "freeform":     "请用中文详细回答",
    "multi_select": "请输出所有正确选项，例如：A, B, C",
    "json_struct":  "请只输出JSON格式答案",
}
```

---

## Cost Impact

| Tier | Before | After |
|------|--------|-------|
| Tier 1 MCQ | DS×3 + Opus ~20-30% of questions | DS×3 + Opus only when not unanimous (fewer calls) |
| Tier 2 | Claude always + DS×2 | Claude always (with richer context) + DS×2 |
| Tier 3 | Claude single pass | Claude single pass (with Qwen context, free) |
| Tier 4 | Skip | Copy Qwen (free) |

Net: Slightly lower Tier 1 cost, same Tier 2/3 cost, Tier 4 now produces output.

---

## Qwen Answer Normalization

Same `normalize_answer(answer, format_type)` function from `aggregator.py`:
- `mcq`: extract first letter, lowercase (handles `<D>` → `d`)
- `multi_select`: extract all letters, sort, join (handles `A,B,C,D,E` → `a,b,c,d,e`)
- `freeform`/`json_struct`: strip whitespace

If normalization yields empty string for MCQ → treat as ERROR, exclude from vote.

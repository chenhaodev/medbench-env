# MedBench Score Boost — Design Document
**Date:** 2026-03-04
**Goal:** Maximize MedBench LLM sub-task score through multi-model ensemble, targeting intentional overfitting within a $6/day budget.

---

## Context

- Current rank: 7th, overall score ~65.2
- 38 test tasks, mostly 30 questions each (MedEthics, MedExam, MedRxCheck_SCQ, MedSafety have 150)
- Multiple submissions allowed → enables iterative cycle-based improvement
- Infrastructure: Anthropic API (Claude), Poe API (non-Claude), DeepSeek API

---

## 4-Tier System

| Tier | Score range | Strategy | Models |
|------|-------------|----------|--------|
| 1 | < 55 | 3-model ensemble → Dawid-Skene | DeepSeek-R1 ×3 + Claude Opus 4.6 (tie-break) |
| 2 | 55–70 | 3-model majority vote | DeepSeek-V3 ×2 + Claude Sonnet 4.6 |
| 3 | 70–80 | Single pass | Claude Sonnet 4.5 |
| 4 | > 80 | Skip | — |

---

## Task Assignment (cycle0 scores)

**Tier 1 — Critical (<55):**
`DDx-advanced` (33), `MedOutcome` (39), `MedReportQC` (39), `MedDiffer` (48), `MedLitQA` (50)

**Tier 2 — Weak (55–70):**
`MedExplain` (55), `MedChartQC` (57), `MedInsureCalc` (59), `MedHC` (59), `MedSafety` (60),
`MedPrimary` (62), `MedEthics` (63), `CMB-Clin-extended` (63), `MedPopular` (64), `MedSummary` (65),
`MedCare` (66), `MedSpeQA` (68), `MedPHM` (69), `MedTerm` (69), `MedAnalysis` (61),
`MedRehab` (63), `MedMC` (66), `SMDoc` (65), `MedPsychCare` (66),
`MedRxCheck_MSQ` (58), `MedRxCheck_SCQ` (58), `MedRxCheck_SQ` (58)

**Tier 3 — Moderate (70–80):**
`MedDiag` (73), `MedSynonym` (75), `MedRecordGen` (76), `MedRxPlan` (78), `MedPsychQA` (72)

**Tier 4 — Strong (>80, skip):**
`MedExam` (80), `MedHG` (81), `MedTreat` (81), `MedPathQC` (82), `MedInsureCheck` (84), `MedTeach` (97)

---

## Voting Strategy

### Principle: Claude-anchored, DeepSeek as challenger

Claude is trusted by default. DeepSeek runs are cheap challengers that can only override Claude if unanimous.

### Tier 1 — DS-R1 ×3 + Claude Opus 4.6

```
1. Run DeepSeek-R1 ×3  → [a1, a2, a3]
2. If DS unanimous (3/3 agree) → ds_answer
3. If ds_answer differs from what Claude would say → call Claude Opus 4.6 as tiebreaker
4. Otherwise → use DS unanimous answer directly
Note: Claude Opus called only on DS disagreement (~20-30% of questions)
```

### Tier 2 — DS-V3 ×2 + Claude Sonnet 4.6

```
1. Run Claude Sonnet 4.6 → answer_claude
2. Run DeepSeek-V3 ×2  → [a1, a2]
3. If both DS agree AND differ from Claude → use DS answer
4. Otherwise → use Claude's answer (wins ties)
```

### Tier 3 — Claude Sonnet 4.5 single pass

No voting. One call per question.

---

## Answer Format Handling

| Format type | Example tasks | Required output |
|-------------|---------------|----------------|
| `mcq` | MedExam, MedRxCheck_SCQ | Single letter: `A` |
| `freeform` | MedHC, MedExplain, MedSummary | Free-form Chinese text |
| `multi_select` | MedRxCheck_MSQ, SMDoc | Letter set: `A, B, C` |
| `numeric` | MedInsureCalc | Numeric value only |

Format instruction suffixes injected into every prompt:

```python
FORMAT_SUFFIXES = {
    "mcq":          "请只输出选项字母，例如：A",
    "freeform":     "请用中文详细回答",
    "multi_select": "请输出所有正确选项，例如：A, B, C",
    "numeric":      "请只输出数字答案，不含单位",
}
```

Answer normalization before voting: strip whitespace, punctuation, lowercase.

---

## File Structure

```
MedBench_LLM/
├── runner/
│   ├── tier_config.py        # task → tier + format + model list (reads tier_state.json)
│   ├── multi_model_runner.py # Tier 1 & 2: calls N models, saves raw votes
│   ├── aggregator.py         # majority vote + Dawid-Skene for Tier 1
│   ├── single_runner.py      # Tier 3: single Sonnet 4.5 pass
│   └── main.py               # orchestrates all tiers, writes final_results/
├── tier_state.json           # editable: task → current score (update after each submission)
├── cycle1/
│   ├── raw_votes/            # per-model raw answers (seeds Dawid-Skene for cycle 2+)
│   └── final_results/        # submission-ready JSONL
└── .claude/plans/
    └── 2026-03-04-medbench-score-boost-design.md
```

---

## API Routing

| Model | API | Model ID |
|-------|-----|----------|
| Claude Opus 4.6 | Anthropic API | `claude-opus-4-6` |
| Claude Sonnet 4.6 | Anthropic API | `claude-sonnet-4-6` |
| Claude Sonnet 4.5 | Anthropic API | `claude-sonnet-4-5-20251001` |
| DeepSeek-R1 | DeepSeek API | `deepseek-reasoner` |
| DeepSeek-V3 | DeepSeek API | `deepseek-chat` |

---

## Cost Estimate Per Cycle

Assuming ~500 tokens input + 300 tokens output per question:

| Tier | Tasks | Questions | Calls | Est. cost |
|------|-------|-----------|-------|-----------|
| 1 | 5 | 150 | DS-R1 ×3 + Opus ~30% | ~$0.50 |
| 2 | 22 | 660 | DS-V3 ×2 + Sonnet 4.6 ×1 | ~$1.20 |
| 3 | 5 | 150 | Sonnet 4.5 ×1 | ~$0.15 |
| 4 | 6 | — | skipped | $0 |
| **Total** | | | | **~$1.85/cycle** |

~3 full cycles per day within $6/day budget.

---

## Multi-Cycle Feedback Loop

```
Cycle N:
  1. Run runner/main.py → cycle{N}/final_results/
  2. Submit to MedBench → get per-task scores
  3. Update tier_state.json with new scores
  4. Tasks that crossed tier boundary are auto-reassigned next cycle
  5. raw_votes/ accumulates → feeds Dawid-Skene weight calibration in cycle 2+

Cycle N+1:
  - Re-tiered tasks get appropriate model treatment
  - Dawid-Skene uses accumulated votes to weight models per task type
  - Budget focused on tasks still below threshold
```

`tier_state.json` is the single source of truth. Edit it after each submission to reflect actual scores.

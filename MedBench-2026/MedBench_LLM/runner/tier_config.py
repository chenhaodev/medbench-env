# runner/tier_config.py
import copy
from typing import Dict, Any

TIER_THRESHOLDS = {1: 55, 2: 70, 3: 80}

# Format types: mcq=single letter, multi_select=comma-separated letters,
# freeform=Chinese text, json_struct=JSON output
TASK_FORMATS: Dict[str, str] = {
    "DDx-advanced": "multi_select",
    "MedOutcome": "freeform",
    "MedReportQC": "freeform",
    "MedDiffer": "freeform",
    "MedLitQA": "mcq",
    "MedExplain": "freeform",
    "MedChartQC": "freeform",
    "MedInsureCalc": "json_struct",
    "MedHC": "freeform",
    "MedSafety": "mcq",
    "MedPrimary": "freeform",
    "MedEthics": "mcq",
    "CMB-Clin-extended": "freeform",
    "MedPopular": "freeform",
    "MedSummary": "freeform",
    "MedCare": "freeform",
    "MedSpeQA": "freeform",
    "MedPHM": "freeform",
    "MedTerm": "freeform",
    "MedAnalysis": "freeform",
    "MedRehab": "freeform",
    "MedMC": "mcq",
    "SMDoc": "freeform",
    "MedPsychCare": "freeform",
    "MedRxCheck_MSQ": "multi_select",
    "MedRxCheck_SCQ": "mcq",
    "MedRxCheck_SQ": "freeform",
    "MedDiag": "freeform",
    "MedSynonym": "freeform",
    "MedRecordGen": "freeform",
    "MedRxPlan": "freeform",
    "MedPsychQA": "freeform",
    "MedExam": "mcq",
    "MedHG": "freeform",
    "MedTreat": "freeform",
    "MedPathQC": "freeform",
    "MedInsureCheck": "freeform",
    "MedTeach": "freeform",
}

MODELS: Dict[int, Dict[str, Any]] = {
    1: {
        "deepseek": {"model_id": "deepseek-reasoner", "runs": 3},
        "claude_tiebreak": {"model_id": "claude-opus-4-6"},
    },
    2: {
        "deepseek": {"model_id": "deepseek-chat", "runs": 2},
        "claude_anchor": {"model_id": "claude-sonnet-4-6"},
    },
    3: {
        "claude": {"model_id": "claude-sonnet-4-5-20251001"},
    },
}


def get_tier(task_name: str, tier_state: Dict[str, float]) -> int:
    score = tier_state.get(task_name)
    if score is None:
        return 2  # default to Tier 2 for unknown tasks
    if score < TIER_THRESHOLDS[1]:
        return 1
    if score < TIER_THRESHOLDS[2]:
        return 2
    if score < TIER_THRESHOLDS[3]:
        return 3
    return 4


def get_format_type(task_name: str) -> str:
    return TASK_FORMATS.get(task_name, "freeform")


def get_models(tier: int) -> Dict[str, Any]:
    if tier == 4:
        return {}
    config = MODELS.get(tier, MODELS[2])
    return copy.deepcopy(config)

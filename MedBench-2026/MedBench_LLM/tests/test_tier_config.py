# tests/test_tier_config.py
import json
import pytest
from runner.tier_config import get_tier, get_format_type, get_models, TIER_THRESHOLDS

def test_tier1_task():
    assert get_tier("DDx-advanced", {"DDx-advanced": 33}) == 1

def test_tier2_task():
    assert get_tier("MedHC", {"MedHC": 59}) == 2

def test_tier3_task():
    assert get_tier("MedDiag", {"MedDiag": 73}) == 3

def test_tier4_task():
    assert get_tier("MedTeach", {"MedTeach": 97}) == 4

def test_unknown_task_defaults_tier2():
    assert get_tier("UnknownTask", {}) == 2

def test_format_multi_select():
    assert get_format_type("DDx-advanced") == "multi_select"

def test_format_freeform():
    assert get_format_type("MedHC") == "freeform"

def test_format_mcq():
    assert get_format_type("MedExam") == "mcq"

def test_tier1_models():
    models = get_models(1)
    assert "deepseek" in models
    assert "claude_tiebreak" in models
    assert models["deepseek"]["runs"] == 3

def test_tier2_models():
    models = get_models(2)
    assert "deepseek" in models
    assert "claude_anchor" in models
    assert models["deepseek"]["runs"] == 2

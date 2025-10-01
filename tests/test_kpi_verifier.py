"""
Unit tests for KPI verifier module
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.kpi_verifier import extract_numeric_claims, recompute_metrics, verify_answer


def test_extract_numeric_claims_basic():
    """Test basic numeric claim extraction"""
    text = "flow_efficiency = 0.62"
    claims = extract_numeric_claims(text)
    
    assert len(claims) > 0
    assert claims[0]["name"] == "flow_efficiency"
    assert claims[0]["value"] == 0.62


def test_extract_numeric_claims_multiple_patterns():
    """Test extraction of various patterns"""
    text = """
    The analysis shows:
    - flow_efficiency = 0.62
    - 14 handoffs for Sales-Ops
    - average duration is 45.2 seconds
    - 62% flow efficiency
    """
    
    claims = extract_numeric_claims(text)
    
    assert len(claims) >= 3
    
    # Check for flow efficiency
    flow_claims = [c for c in claims if "flow" in c["name"].lower() or "efficiency" in c["name"].lower()]
    assert len(flow_claims) > 0


def test_extract_numeric_claims_facts_block():
    """Test extraction from JSON facts block"""
    text = """
    Summary analysis.
    
    ```facts
    {
      "dataset": "sf",
      "filters": {"team": "Sales-Ops"},
      "metrics": {
        "flow_efficiency": 0.62,
        "handoffs": 14,
        "aging_>14d": 7
      }
    }
    ```
    """
    
    claims = extract_numeric_claims(text)
    
    assert len(claims) >= 3
    
    # Check all metrics were extracted
    metric_names = {c["name"] for c in claims}
    assert "flow_efficiency" in metric_names
    assert "handoffs" in metric_names
    assert any("aging" in name or "14d" in name for name in metric_names)


def test_recompute_metrics_with_small_dataframe():
    """Test metric recomputation with a small test dataframe"""
    # Create small test dataframe
    data = {
        "case_id": [1, 1, 1, 2, 2, 3],
        "user": ["Alice", "Bob", "Alice", "Bob", "Charlie", "Alice"],
        "activity": ["Start", "Review", "Complete", "Start", "Review", "Start"],
        "duration_seconds": [10.0, 30.0, 5.0, 12.0, 28.0, 8.0],
        "team": ["Sales", "Sales", "Sales", "Support", "Support", "Sales"]
    }
    
    df = pd.DataFrame(data)
    
    # Test claim
    claims = [
        {"name": "cases", "slice": None, "value": 3.0, "units": "", "raw_text": "3 cases"}
    ]
    
    results = recompute_metrics(claims, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert len(results) == 1
    assert results[0]["name"] == "cases"
    assert results[0]["recomputed"] == 3.0
    assert results[0]["pass"] is True


def test_recompute_metrics_duration():
    """Test duration metric recomputation"""
    data = {
        "case_id": [1, 1, 2, 2],
        "user": ["Alice", "Bob", "Alice", "Bob"],
        "activity": ["Start", "Complete", "Start", "Complete"],
        "duration_seconds": [10.0, 20.0, 15.0, 25.0]
    }
    
    df = pd.DataFrame(data)
    
    # Average duration should be (10 + 20 + 15 + 25) / 4 = 17.5
    claims = [
        {"name": "avg_duration", "slice": None, "value": 17.5, "units": "seconds", "raw_text": "avg duration 17.5"}
    ]
    
    results = recompute_metrics(claims, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert len(results) > 0
    result = results[0]
    assert result["recomputed"] == 17.5
    assert result["pass"] is True


def test_recompute_metrics_with_tolerance():
    """Test that tolerance is applied correctly"""
    data = {
        "case_id": [1, 1, 2, 2],
        "duration_seconds": [100.0, 100.0, 100.0, 100.0]
    }
    
    df = pd.DataFrame(data)
    
    # Claim is 101, actual is 100 -> 1% error, within 2% tolerance
    claims = [
        {"name": "avg_duration", "slice": None, "value": 101.0, "units": "seconds", "raw_text": "avg 101"}
    ]
    
    results = recompute_metrics(claims, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert len(results) > 0
    result = results[0]
    assert result["pass"] is True


def test_recompute_metrics_exceeds_tolerance():
    """Test that claims exceeding tolerance fail"""
    data = {
        "case_id": [1, 1, 2, 2],
        "duration_seconds": [100.0, 100.0, 100.0, 100.0]
    }
    
    df = pd.DataFrame(data)
    
    # Claim is 110, actual is 100 -> 10% error, exceeds 2% tolerance
    claims = [
        {"name": "avg_duration", "slice": None, "value": 110.0, "units": "seconds", "raw_text": "avg 110"}
    ]
    
    results = recompute_metrics(claims, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert len(results) > 0
    result = results[0]
    assert result["pass"] is False
    assert result["pct_err"] > 0.02


def test_verify_answer_full_pipeline():
    """Test full verification pipeline"""
    data = {
        "case_id": [1, 1, 2, 2, 3, 3],
        "user": ["Alice", "Bob", "Alice", "Bob", "Charlie", "Alice"],
        "activity": ["Start", "Complete", "Start", "Complete", "Start", "Complete"],
        "duration_seconds": [10.0, 20.0, 15.0, 25.0, 12.0, 18.0],
        "team": ["Sales", "Sales", "Support", "Support", "Sales", "Sales"]
    }
    
    df = pd.DataFrame(data)
    
    answer_text = """
    The analysis shows:
    - 3 cases total
    - Average duration is 16.67 seconds
    
    ```facts
    {
      "dataset": "sf",
      "filters": {},
      "metrics": {
        "case_count": 3,
        "avg_duration_seconds": 16.67
      }
    }
    ```
    """
    
    verification = verify_answer(answer_text, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert verification["has_numeric_claims"] is True
    assert verification["claims_verified"] > 0
    # At least one claim should pass (case count)
    assert verification["claims_passed"] > 0


def test_verify_answer_no_claims():
    """Test verification when no numeric claims are present"""
    data = {
        "case_id": [1, 2],
        "duration_seconds": [10.0, 20.0]
    }
    
    df = pd.DataFrame(data)
    
    answer_text = "This is a qualitative analysis with no numeric claims."
    
    verification = verify_answer(answer_text, df, "salesforce", {}, tolerance_pct=0.02)
    
    assert verification["has_numeric_claims"] is False
    assert verification["grounded_accuracy_pass"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


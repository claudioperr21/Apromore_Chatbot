"""
KPI Verifier for Auto-Verification of Numeric Claims
====================================================

Extracts numeric claims from AI responses and verifies them against
actual pandas computations for grounded accuracy and metric parity.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import pandas as pd
from backend.metrics import (
    flow_efficiency, case_aging_buckets, throughput_minutes, handoffs,
    filter_dataframe, compute_panel_metrics, find_column
)


def extract_numeric_claims(text: str) -> List[Dict[str, Any]]:
    """
    Extract numeric claims from text
    
    Patterns detected:
    - "metric_name = value"
    - "value units by group"
    - "X% of Y"
    - "average/mean/median X is Y"
    
    Args:
        text: Response text to analyze
    
    Returns:
        List of claims with structure: {name, slice, value, units}
    """
    claims = []
    
    # Pattern 1: "metric = value" or "metric: value"
    # Examples: "flow_efficiency = 0.62", "handoffs: 14"
    pattern1 = r'(\w+(?:_\w+)*)\s*[=:]\s*([\d.]+)\s*([%a-zA-Z]*)'
    matches1 = re.finditer(pattern1, text, re.IGNORECASE)
    
    for match in matches1:
        metric_name = match.group(1).lower()
        value = match.group(2)
        units = match.group(3) if match.group(3) else ""
        
        try:
            numeric_value = float(value)
            claims.append({
                "name": metric_name,
                "slice": None,  # No specific slice
                "value": numeric_value,
                "units": units,
                "raw_text": match.group(0)
            })
        except ValueError:
            pass
    
    # Pattern 2: "X units by/for group"
    # Examples: "14 handoffs for Sales-Ops", "12 cases by Team A"
    pattern2 = r'([\d.]+)\s+(\w+)\s+(?:by|for|in)\s+(["\']?)([^"\',.!?\n]+)\3'
    matches2 = re.finditer(pattern2, text, re.IGNORECASE)
    
    for match in matches2:
        value = match.group(1)
        metric_name = match.group(2).lower()
        slice_name = match.group(4).strip()
        
        try:
            numeric_value = float(value)
            claims.append({
                "name": metric_name,
                "slice": slice_name,
                "value": numeric_value,
                "units": metric_name,  # Units are the metric name
                "raw_text": match.group(0)
            })
        except ValueError:
            pass
    
    # Pattern 3: "average/mean/median X is Y"
    # Examples: "average duration is 45.2 seconds", "mean flow efficiency is 0.67"
    pattern3 = r'(?:average|mean|median|avg)\s+(\w+(?:_\w+)*)\s+(?:is|of|=)\s*([\d.]+)\s*([%a-zA-Z]*)'
    matches3 = re.finditer(pattern3, text, re.IGNORECASE)
    
    for match in matches3:
        metric_name = f"avg_{match.group(1).lower()}"
        value = match.group(2)
        units = match.group(3) if match.group(3) else ""
        
        try:
            numeric_value = float(value)
            claims.append({
                "name": metric_name,
                "slice": None,
                "value": numeric_value,
                "units": units,
                "raw_text": match.group(0)
            })
        except ValueError:
            pass
    
    # Pattern 4: "X% of Y" or "X percent"
    # Examples: "62% flow efficiency", "80 percent of cases"
    pattern4 = r'([\d.]+)\s*(?:%|percent)\s+(?:of\s+)?(\w+(?:_\w+)*)'
    matches4 = re.finditer(pattern4, text, re.IGNORECASE)
    
    for match in matches4:
        value = match.group(1)
        metric_name = match.group(2).lower()
        
        try:
            numeric_value = float(value) / 100.0  # Convert percentage to decimal
            claims.append({
                "name": metric_name,
                "slice": None,
                "value": numeric_value,
                "units": "%",
                "raw_text": match.group(0)
            })
        except ValueError:
            pass
    
    # Pattern 5: JSON facts block
    # Extract from ```facts code blocks
    facts_pattern = r'```facts\s*\n(.*?)\n```'
    facts_matches = re.finditer(facts_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in facts_matches:
        try:
            import json
            facts_data = json.loads(match.group(1))
            
            if "metrics" in facts_data:
                filters = facts_data.get("filters", {})
                slice_desc = None
                if filters:
                    # Create slice description from filters
                    slice_parts = []
                    if "team" in filters:
                        slice_parts.append(f"team={filters['team']}")
                    if "resource" in filters:
                        slice_parts.append(f"resource={filters['resource']}")
                    slice_desc = ", ".join(slice_parts) if slice_parts else None
                
                for metric_name, metric_value in facts_data["metrics"].items():
                    if isinstance(metric_value, (int, float)):
                        claims.append({
                            "name": metric_name,
                            "slice": slice_desc,
                            "value": float(metric_value),
                            "units": "",
                            "raw_text": f"{metric_name}={metric_value}",
                            "from_facts_block": True
                        })
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Deduplicate claims (keep first occurrence)
    unique_claims = []
    seen = set()
    
    for claim in claims:
        key = (claim["name"], claim["slice"], claim["value"])
        if key not in seen:
            seen.add(key)
            unique_claims.append(claim)
    
    return unique_claims


def recompute_metrics(claims: List[Dict[str, Any]], 
                     dataset_slice: pd.DataFrame,
                     dataset_name: str = "salesforce",
                     filters: Dict[str, Any] = None,
                     tolerance_pct: float = 0.02) -> List[Dict[str, Any]]:
    """
    Recompute metrics from claims and compare with actual pandas calculations
    
    Args:
        claims: List of extracted claims
        dataset_slice: DataFrame slice to compute metrics on
        dataset_name: Name of dataset (salesforce/amadeus)
        filters: Filters applied to the slice
        tolerance_pct: Tolerance percentage for comparisons (default 2%)
    
    Returns:
        List of verification results with {name, claimed, recomputed, pass, abs_err, pct_err}
    """
    results = []
    
    if len(dataset_slice) == 0:
        return results
    
    # Compute full panel metrics once
    panel_metrics = compute_panel_metrics(dataset_slice, dataset_name, filters)
    
    for claim in claims:
        metric_name = claim["name"]
        claimed_value = claim["value"]
        slice_desc = claim["slice"]
        
        # Get the appropriate slice if needed
        working_df = dataset_slice
        if slice_desc:
            # Parse slice description and apply filters
            slice_filters = {}
            if "team=" in slice_desc:
                team_match = re.search(r'team=([^,]+)', slice_desc)
                if team_match:
                    slice_filters["team"] = team_match.group(1).strip()
            if "resource=" in slice_desc:
                resource_match = re.search(r'resource=([^,]+)', slice_desc)
                if resource_match:
                    slice_filters["resource"] = resource_match.group(1).strip()
            
            if slice_filters:
                working_df = filter_dataframe(dataset_slice, slice_filters)
        
        # Recompute the metric
        recomputed_value = None
        
        try:
            # Map claim names to metric functions
            if metric_name in ["flow_efficiency", "flow efficiency"]:
                recomputed_value = flow_efficiency(working_df, dataset_name)
            
            elif metric_name in ["handoffs", "handoff", "avg_handoffs"]:
                recomputed_value = handoffs(working_df, dataset_name)
            
            elif metric_name in ["throughput_minutes", "throughput", "avg_throughput"]:
                recomputed_value = throughput_minutes(working_df, dataset_name)
            
            elif "aging" in metric_name or "age" in metric_name:
                aging = case_aging_buckets(working_df, dataset_name)
                # Extract specific bucket if mentioned
                if ">14d" in claim.get("raw_text", "") or "14d" in metric_name:
                    recomputed_value = aging.get(">14d", 0)
                elif "8-14" in claim.get("raw_text", "") or "8_14" in metric_name:
                    recomputed_value = aging.get("8-14d", 0)
                elif "0-7" in claim.get("raw_text", "") or "0_7" in metric_name:
                    recomputed_value = aging.get("0-7d", 0)
            
            elif metric_name in ["cases", "case_count", "case count"]:
                recomputed_value = float(len(working_df))
                # If it's case count, might need unique cases
                case_col = find_column(working_df, ["case_id", "case", "id"])
                if case_col:
                    recomputed_value = float(working_df[case_col].nunique())
            
            elif "duration" in metric_name or metric_name in ["avg_duration", "mean_duration"]:
                duration_col = find_column(working_df, ["duration_seconds", "duration", "task_duration"])
                if duration_col:
                    if not pd.api.types.is_numeric_dtype(working_df[duration_col]):
                        working_df = working_df.copy()
                        working_df[duration_col] = pd.to_numeric(working_df[duration_col], errors="coerce")
                    
                    if "avg" in metric_name or "mean" in metric_name or "average" in metric_name:
                        recomputed_value = working_df[duration_col].mean()
                    elif "median" in metric_name:
                        recomputed_value = working_df[duration_col].median()
                    elif "max" in metric_name or "maximum" in metric_name:
                        recomputed_value = working_df[duration_col].max()
                    else:
                        recomputed_value = working_df[duration_col].mean()
            
            elif metric_name in ["users", "user_count", "unique_users"]:
                user_col = find_column(working_df, ["user", "resource", "agent_profile_id"])
                if user_col:
                    recomputed_value = float(working_df[user_col].nunique())
            
            elif metric_name in ["activities", "activity_count", "unique_activities"]:
                activity_col = find_column(working_df, ["activity", "step", "original_activity"])
                if activity_col:
                    recomputed_value = float(working_df[activity_col].nunique())
            
            elif metric_name in ["teams", "team_count", "unique_teams"]:
                team_col = find_column(working_df, ["team", "teams"])
                if team_col:
                    recomputed_value = float(working_df[team_col].nunique())
            
            # Try to get from panel metrics if not computed
            if recomputed_value is None and metric_name in panel_metrics:
                recomputed_value = panel_metrics[metric_name]
        
        except Exception as e:
            # Metric computation failed
            results.append({
                "name": metric_name,
                "claimed": claimed_value,
                "recomputed": None,
                "pass": False,
                "abs_err": None,
                "pct_err": None,
                "error": str(e)
            })
            continue
        
        # Compare claimed vs recomputed
        if recomputed_value is not None:
            abs_err = abs(claimed_value - recomputed_value)
            
            # Calculate percentage error
            if recomputed_value != 0:
                pct_err = abs_err / abs(recomputed_value)
            else:
                # If recomputed is 0, check if claimed is also close to 0
                pct_err = abs_err if abs_err > tolerance_pct else 0.0
            
            # Determine pass/fail based on tolerance
            # For counts (integers), use ±1 tolerance
            if metric_name in ["cases", "case_count", "users", "activities", "teams", "handoffs"] or \
               "count" in metric_name or "aging" in metric_name:
                passes = abs_err <= 1.0
            else:
                # For rates and durations, use percentage tolerance
                passes = pct_err <= tolerance_pct
            
            results.append({
                "name": metric_name,
                "claimed": claimed_value,
                "recomputed": recomputed_value,
                "pass": passes,
                "abs_err": abs_err,
                "pct_err": pct_err
            })
        else:
            # Could not recompute metric
            results.append({
                "name": metric_name,
                "claimed": claimed_value,
                "recomputed": None,
                "pass": None,  # Unknown
                "abs_err": None,
                "pct_err": None,
                "error": "Metric not recomputable"
            })
    
    return results


def verify_answer(answer_text: str, 
                 dataset_slice: pd.DataFrame,
                 dataset_name: str = "salesforce",
                 filters: Dict[str, Any] = None,
                 tolerance_pct: float = 0.02) -> Dict[str, Any]:
    """
    Full verification pipeline: extract claims and verify them
    
    Args:
        answer_text: AI response text
        dataset_slice: DataFrame slice used for the answer
        dataset_name: Dataset name
        filters: Filters applied
        tolerance_pct: Tolerance for comparisons
    
    Returns:
        Verification summary with grounded_accuracy_pass and detailed results
    """
    # Extract claims
    claims = extract_numeric_claims(answer_text)
    
    if len(claims) == 0:
        return {
            "has_numeric_claims": False,
            "grounded_accuracy_pass": None,
            "claims_verified": 0,
            "claims_passed": 0,
            "claims_failed": 0,
            "verification_results": []
        }
    
    # Recompute and verify
    verification_results = recompute_metrics(
        claims, dataset_slice, dataset_name, filters, tolerance_pct
    )
    
    # Calculate summary statistics
    claims_with_pass_result = [r for r in verification_results if r["pass"] is not None]
    claims_passed = [r for r in claims_with_pass_result if r["pass"]]
    claims_failed = [r for r in claims_with_pass_result if not r["pass"]]
    
    grounded_accuracy_pass = len(claims_failed) == 0 if len(claims_with_pass_result) > 0 else None
    
    return {
        "has_numeric_claims": True,
        "grounded_accuracy_pass": grounded_accuracy_pass,
        "claims_verified": len(claims_with_pass_result),
        "claims_passed": len(claims_passed),
        "claims_failed": len(claims_failed),
        "verification_results": verification_results,
        "all_claims": claims
    }


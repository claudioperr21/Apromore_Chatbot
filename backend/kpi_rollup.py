"""
Daily KPI Rollup and Aggregation
=================================

Reads JSONL trace files and computes aggregated KPIs including:
- Grounded accuracy rate
- Routing accuracy
- Metric parity (MAPE)
- Hallucination rate
- Contradiction rate
- Latency metrics
- Adoption metrics
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, date, timedelta
import numpy as np
from collections import defaultdict


def read_traces(trace_file: Path) -> List[Dict[str, Any]]:
    """
    Read JSONL trace file
    
    Args:
        trace_file: Path to JSONL trace file
    
    Returns:
        List of trace records
    """
    traces = []
    
    if not trace_file.exists():
        return traces
    
    try:
        with open(trace_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        trace = json.loads(line)
                        traces.append(trace)
                    except json.JSONDecodeError:
                        pass  # Skip malformed lines
    except Exception as e:
        print(f"Error reading trace file {trace_file}: {e}")
    
    return traces


def compute_grounded_accuracy_rate(traces: List[Dict[str, Any]]) -> float:
    """
    Calculate grounded accuracy rate: passed turns / turns with numeric claims
    """
    turns_with_claims = []
    
    for trace in traces:
        extracted_metrics = trace.get("extracted_metrics", {})
        if extracted_metrics and extracted_metrics.get("has_numeric_claims"):
            grounded_pass = extracted_metrics.get("grounded_accuracy_pass")
            if grounded_pass is not None:
                turns_with_claims.append(1 if grounded_pass else 0)
    
    if len(turns_with_claims) == 0:
        return None
    
    return sum(turns_with_claims) / len(turns_with_claims)


def compute_routing_accuracy(traces: List[Dict[str, Any]]) -> float:
    """
    Calculate routing accuracy: correct_routes / total_routed_turns
    """
    routed_turns = []
    
    for trace in traces:
        router_correct = trace.get("router_correct")
        if router_correct is not None:
            routed_turns.append(1 if router_correct else 0)
    
    if len(routed_turns) == 0:
        return None
    
    return sum(routed_turns) / len(routed_turns)


def compute_metric_parity_mape(traces: List[Dict[str, Any]], 
                               panel_metrics: List[str] = None) -> Dict[str, float]:
    """
    Calculate Mean Absolute Percentage Error (MAPE) for key metrics
    
    Args:
        traces: List of trace records
        panel_metrics: List of metric names to compute MAPE for
    
    Returns:
        Dictionary with MAPE per metric
    """
    if panel_metrics is None:
        panel_metrics = [
            "flow_efficiency", "handoffs", "throughput_minutes",
            "aging_>14d", "case_count"
        ]
    
    metric_errors = defaultdict(list)
    
    for trace in traces:
        extracted_metrics = trace.get("extracted_metrics", {})
        if not extracted_metrics:
            continue
        
        verification_results = extracted_metrics.get("verification_results", [])
        
        for result in verification_results:
            metric_name = result.get("name")
            pct_err = result.get("pct_err")
            
            if metric_name and pct_err is not None:
                # Normalize metric name
                normalized_name = metric_name.lower().replace("_", "").replace(" ", "")
                
                # Match to panel metrics
                for panel_metric in panel_metrics:
                    panel_normalized = panel_metric.lower().replace("_", "").replace(" ", "")
                    if panel_normalized in normalized_name or normalized_name in panel_normalized:
                        metric_errors[panel_metric].append(pct_err)
                        break
    
    # Compute MAPE
    mape_results = {}
    for metric, errors in metric_errors.items():
        if errors:
            mape_results[metric] = np.mean(errors)
    
    # Overall MAPE
    all_errors = [err for errors in metric_errors.values() for err in errors]
    if all_errors:
        mape_results["overall"] = np.mean(all_errors)
    
    return mape_results


def compute_hallucination_rate(traces: List[Dict[str, Any]]) -> float:
    """
    Calculate hallucination rate: answers with unknown references / total answers
    """
    total_answers = 0
    hallucinated_answers = 0
    
    for trace in traces:
        # Only count traces that generated answers
        if trace.get("endpoint") not in ["/api/analyze", "/api/agent"]:
            continue
        
        total_answers += 1
        
        # Check for hallucinations
        extracted_metrics = trace.get("extracted_metrics", {})
        if extracted_metrics:
            hallucination_check = extracted_metrics.get("hallucination_check", {})
            if hallucination_check.get("has_hallucinations"):
                hallucinated_answers += 1
    
    if total_answers == 0:
        return None
    
    return hallucinated_answers / total_answers


def compute_contradiction_rate(traces: List[Dict[str, Any]]) -> float:
    """
    Calculate contradiction rate: sessions with contradictory claims / sessions
    
    A contradiction occurs when two successive claims for the same metric differ > tolerance
    """
    # Group traces by session (if session_id available)
    sessions = defaultdict(list)
    
    for trace in traces:
        session_id = trace.get("session_id", "default")
        timestamp = trace.get("timestamp_utc", "")
        extracted_metrics = trace.get("extracted_metrics", {})
        
        if extracted_metrics and extracted_metrics.get("has_numeric_claims"):
            sessions[session_id].append({
                "timestamp": timestamp,
                "claims": extracted_metrics.get("all_claims", [])
            })
    
    if len(sessions) == 0:
        return None
    
    sessions_with_contradictions = 0
    total_sessions = len(sessions)
    
    for session_id, session_traces in sessions.items():
        # Sort by timestamp
        session_traces.sort(key=lambda x: x["timestamp"])
        
        # Track metric values across session
        metric_history = defaultdict(list)
        
        for trace in session_traces:
            for claim in trace["claims"]:
                metric_name = claim.get("name")
                value = claim.get("value")
                if metric_name and value is not None:
                    metric_history[metric_name].append(value)
        
        # Check for contradictions (successive values differ > 10%)
        has_contradiction = False
        for metric_name, values in metric_history.items():
            for i in range(1, len(values)):
                prev_val = values[i-1]
                curr_val = values[i]
                
                if prev_val != 0:
                    pct_diff = abs(curr_val - prev_val) / abs(prev_val)
                    if pct_diff > 0.10:  # 10% threshold for contradiction
                        has_contradiction = True
                        break
            
            if has_contradiction:
                break
        
        if has_contradiction:
            sessions_with_contradictions += 1
    
    return sessions_with_contradictions / total_sessions


def compute_latency_percentiles(traces: List[Dict[str, Any]], 
                                endpoint: str = None) -> Dict[str, float]:
    """
    Calculate latency percentiles (p50, p95) overall or per endpoint
    """
    latencies_total = []
    latencies_model = []
    
    for trace in traces:
        if endpoint and trace.get("endpoint") != endpoint:
            continue
        
        latency_total = trace.get("latency_ms_total")
        latency_model = trace.get("latency_ms_model")
        
        if latency_total is not None:
            latencies_total.append(latency_total)
        if latency_model is not None:
            latencies_model.append(latency_model)
    
    results = {}
    
    if latencies_total:
        results["p50_total"] = np.percentile(latencies_total, 50)
        results["p95_total"] = np.percentile(latencies_total, 95)
        results["mean_total"] = np.mean(latencies_total)
    
    if latencies_model:
        results["p50_model"] = np.percentile(latencies_model, 50)
        results["p95_model"] = np.percentile(latencies_model, 95)
        results["mean_model"] = np.mean(latencies_model)
    
    return results


def compute_adoption_metrics(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate adoption metrics: WAU, sessions, queries per session
    """
    # Unique users (dedupe by some identifier - for now use session_id as proxy)
    unique_sessions = set()
    unique_users = set()
    queries_by_session = defaultdict(int)
    
    for trace in traces:
        session_id = trace.get("session_id", "anonymous")
        user_id = trace.get("user_id", session_id)  # Use session as proxy if no user_id
        
        unique_sessions.add(session_id)
        unique_users.add(user_id)
        queries_by_session[session_id] += 1
    
    # Calculate queries per session
    if queries_by_session:
        queries_per_session = np.mean(list(queries_by_session.values()))
    else:
        queries_per_session = 0
    
    return {
        "wau": len(unique_users),  # Weekly active users (for daily, this is DAU)
        "sessions": len(unique_sessions),
        "queries_per_session": queries_per_session,
        "total_queries": len(traces)
    }


def compute_resolution_metrics(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate resolution metrics: resolution rate, turns to resolution
    """
    sessions = defaultdict(list)
    
    for trace in traces:
        session_id = trace.get("session_id", "default")
        resolved = trace.get("resolved", False)
        sessions[session_id].append({"resolved": resolved})
    
    if len(sessions) == 0:
        return {"sessions_resolved_rate": None, "turns_to_resolution_p50": None}
    
    resolved_sessions = 0
    turns_to_resolution = []
    
    for session_id, session_traces in sessions.items():
        # Check if session ended with resolution
        if any(trace["resolved"] for trace in session_traces):
            resolved_sessions += 1
            # Count turns until resolution
            for i, trace in enumerate(session_traces):
                if trace["resolved"]:
                    turns_to_resolution.append(i + 1)
                    break
    
    resolution_rate = resolved_sessions / len(sessions)
    
    if turns_to_resolution:
        turns_p50 = np.percentile(turns_to_resolution, 50)
    else:
        turns_p50 = None
    
    return {
        "sessions_resolved_rate": resolution_rate,
        "turns_to_resolution_p50": turns_p50
    }


def rollup(day_path: Path) -> Dict[str, Any]:
    """
    Compute daily KPI rollup from trace file
    
    Args:
        day_path: Path to daily trace file (traces-YYYYMMDD.jsonl)
    
    Returns:
        Dictionary with all computed KPIs
    """
    # Read traces
    traces = read_traces(day_path)
    
    if len(traces) == 0:
        return {
            "date": day_path.stem.replace("traces-", ""),
            "trace_count": 0,
            "error": "No traces found"
        }
    
    # Compute all KPIs
    kpis = {
        "date": day_path.stem.replace("traces-", ""),
        "trace_count": len(traces),
        "grounded_accuracy_rate": compute_grounded_accuracy_rate(traces),
        "routing_accuracy": compute_routing_accuracy(traces),
        "metric_parity_mape": compute_metric_parity_mape(traces),
        "hallucination_rate": compute_hallucination_rate(traces),
        "contradiction_rate": compute_contradiction_rate(traces),
        "latency": {
            "overall": compute_latency_percentiles(traces),
            "by_endpoint": {}
        },
        "adoption": compute_adoption_metrics(traces),
        "resolution": compute_resolution_metrics(traces)
    }
    
    # Compute per-endpoint latency
    endpoints = set(trace.get("endpoint") for trace in traces if trace.get("endpoint"))
    for endpoint in endpoints:
        kpis["latency"]["by_endpoint"][endpoint] = compute_latency_percentiles(traces, endpoint)
    
    return kpis


def rollup_today(traces_dir: Path) -> Dict[str, Any]:
    """
    Compute KPI rollup for today's traces
    
    Args:
        traces_dir: Directory containing trace files
    
    Returns:
        KPI rollup for today
    """
    today_str = datetime.now().strftime("%Y%m%d")
    today_file = traces_dir / f"traces-{today_str}.jsonl"
    
    if not today_file.exists():
        return {
            "date": today_str,
            "trace_count": 0,
            "error": "No traces for today"
        }
    
    return rollup(today_file)


def rollup_date_range(traces_dir: Path, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Compute KPI rollups for a date range
    
    Args:
        traces_dir: Directory containing trace files
        start_date: Start date
        end_date: End date
    
    Returns:
        List of daily KPI rollups
    """
    rollups = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        trace_file = traces_dir / f"traces-{date_str}.jsonl"
        
        if trace_file.exists():
            rollups.append(rollup(trace_file))
        
        current_date += timedelta(days=1)
    
    return rollups


def save_rollup(kpis: Dict[str, Any], output_dir: Path):
    """
    Save KPI rollup to JSON file
    
    Args:
        kpis: KPI dictionary
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = kpis.get("date", datetime.now().strftime("%Y%m%d"))
    output_file = output_dir / f"kpis-{date_str}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kpis, f, indent=2, default=str)
        print(f"KPI rollup saved to {output_file}")
    except Exception as e:
        print(f"Error saving KPI rollup: {e}")


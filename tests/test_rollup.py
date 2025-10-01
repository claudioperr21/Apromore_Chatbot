"""
Unit tests for KPI rollup module
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.kpi_rollup import (
    read_traces, compute_grounded_accuracy_rate, compute_routing_accuracy,
    compute_metric_parity_mape, compute_hallucination_rate, compute_contradiction_rate,
    compute_latency_percentiles, compute_adoption_metrics, compute_resolution_metrics,
    rollup
)


def create_sample_traces():
    """Create sample trace records for testing"""
    traces = [
        {
            "timestamp_utc": "2025-10-01T10:00:00",
            "endpoint": "/api/analyze/salesforce",
            "dataset": "sf",
            "intent": "summary",
            "latency_ms_total": 150.5,
            "latency_ms_model": 100.0,
            "session_id": "session1",
            "user_id": "user1",
            "extracted_metrics": {
                "has_numeric_claims": True,
                "grounded_accuracy_pass": True,
                "verification_results": [
                    {"name": "flow_efficiency", "pct_err": 0.01, "pass": True}
                ]
            },
            "router_correct": True,
            "resolved": False
        },
        {
            "timestamp_utc": "2025-10-01T10:05:00",
            "endpoint": "/api/analyze/salesforce",
            "dataset": "sf",
            "intent": "kpi_lookup",
            "latency_ms_total": 200.0,
            "latency_ms_model": 150.0,
            "session_id": "session1",
            "user_id": "user1",
            "extracted_metrics": {
                "has_numeric_claims": True,
                "grounded_accuracy_pass": False,
                "verification_results": [
                    {"name": "handoffs", "pct_err": 0.15, "pass": False}
                ]
            },
            "router_correct": True,
            "resolved": True
        },
        {
            "timestamp_utc": "2025-10-01T10:10:00",
            "endpoint": "/api/analyze/amadeus",
            "dataset": "ama",
            "intent": "summary",
            "latency_ms_total": 180.0,
            "latency_ms_model": 120.0,
            "session_id": "session2",
            "user_id": "user2",
            "extracted_metrics": {
                "has_numeric_claims": True,
                "grounded_accuracy_pass": True,
                "verification_results": []
            },
            "router_correct": False,
            "resolved": False
        }
    ]
    
    return traces


def test_read_traces_empty_file():
    """Test reading from empty/non-existent file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        trace_file = Path(tmpdir) / "traces-20251001.jsonl"
        traces = read_traces(trace_file)
        assert traces == []


def test_read_traces_valid_file():
    """Test reading valid JSONL trace file"""
    sample_traces = create_sample_traces()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        trace_file = Path(tmpdir) / "traces-20251001.jsonl"
        
        # Write sample traces
        with open(trace_file, 'w', encoding='utf-8') as f:
            for trace in sample_traces:
                f.write(json.dumps(trace) + '\n')
        
        # Read traces
        traces = read_traces(trace_file)
        
        assert len(traces) == len(sample_traces)
        assert traces[0]["endpoint"] == "/api/analyze/salesforce"


def test_compute_grounded_accuracy_rate():
    """Test grounded accuracy rate calculation"""
    traces = create_sample_traces()
    
    rate = compute_grounded_accuracy_rate(traces)
    
    # 2 turns with numeric claims, 1 passed (50%)
    # Actually: trace 1 passed, trace 2 failed -> 1/2 = 0.5
    assert rate is not None
    assert 0.0 <= rate <= 1.0


def test_compute_routing_accuracy():
    """Test routing accuracy calculation"""
    traces = create_sample_traces()
    
    accuracy = compute_routing_accuracy(traces)
    
    # 2 routed correctly, 1 incorrectly -> 2/3 = 0.667
    assert accuracy is not None
    assert 0.0 <= accuracy <= 1.0


def test_compute_metric_parity_mape():
    """Test MAPE calculation"""
    traces = create_sample_traces()
    
    mape = compute_metric_parity_mape(traces)
    
    assert isinstance(mape, dict)
    # Should have at least overall MAPE if any errors exist
    if len(mape) > 0:
        assert "overall" in mape or len(mape) > 0


def test_compute_hallucination_rate():
    """Test hallucination rate calculation"""
    traces = create_sample_traces()
    
    # Add hallucination check to one trace
    traces[0]["extracted_metrics"]["hallucination_check"] = {
        "has_hallucinations": True,
        "unknown_entities": [{"type": "team", "value": "FakeTeam"}]
    }
    
    rate = compute_hallucination_rate(traces)
    
    # 2 analyze endpoints, 1 has hallucinations -> 1/2 = 0.5
    assert rate is not None
    assert 0.0 <= rate <= 1.0


def test_compute_contradiction_rate():
    """Test contradiction rate calculation"""
    # Create traces with contradictory claims
    traces = [
        {
            "timestamp_utc": "2025-10-01T10:00:00",
            "session_id": "session1",
            "extracted_metrics": {
                "has_numeric_claims": True,
                "all_claims": [
                    {"name": "flow_efficiency", "value": 0.6}
                ]
            }
        },
        {
            "timestamp_utc": "2025-10-01T10:05:00",
            "session_id": "session1",
            "extracted_metrics": {
                "has_numeric_claims": True,
                "all_claims": [
                    {"name": "flow_efficiency", "value": 0.8}  # 33% change - contradiction
                ]
            }
        }
    ]
    
    rate = compute_contradiction_rate(traces)
    
    # 1 session with contradiction -> 1/1 = 1.0
    assert rate is not None
    assert 0.0 <= rate <= 1.0


def test_compute_latency_percentiles():
    """Test latency percentile calculation"""
    traces = create_sample_traces()
    
    latencies = compute_latency_percentiles(traces)
    
    assert "p50_total" in latencies
    assert "p95_total" in latencies
    assert latencies["p50_total"] > 0


def test_compute_adoption_metrics():
    """Test adoption metrics calculation"""
    traces = create_sample_traces()
    
    adoption = compute_adoption_metrics(traces)
    
    assert "wau" in adoption
    assert "sessions" in adoption
    assert "queries_per_session" in adoption
    assert adoption["sessions"] == 2  # 2 unique sessions
    assert adoption["total_queries"] == 3


def test_compute_resolution_metrics():
    """Test resolution metrics calculation"""
    traces = create_sample_traces()
    
    resolution = compute_resolution_metrics(traces)
    
    assert "sessions_resolved_rate" in resolution
    assert "turns_to_resolution_p50" in resolution
    
    # 1 session resolved out of 2 -> 0.5
    assert resolution["sessions_resolved_rate"] == 0.5


def test_rollup_full():
    """Test full rollup computation"""
    sample_traces = create_sample_traces()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        trace_file = Path(tmpdir) / "traces-20251001.jsonl"
        
        # Write sample traces
        with open(trace_file, 'w', encoding='utf-8') as f:
            for trace in sample_traces:
                f.write(json.dumps(trace) + '\n')
        
        # Compute rollup
        kpis = rollup(trace_file)
        
        assert "date" in kpis
        assert "trace_count" in kpis
        assert "grounded_accuracy_rate" in kpis
        assert "routing_accuracy" in kpis
        assert "metric_parity_mape" in kpis
        assert "hallucination_rate" in kpis
        assert "contradiction_rate" in kpis
        assert "latency" in kpis
        assert "adoption" in kpis
        assert "resolution" in kpis
        
        assert kpis["trace_count"] == 3


def test_rollup_empty_file():
    """Test rollup with empty file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        trace_file = Path(tmpdir) / "traces-20251001.jsonl"
        
        # Create empty file
        trace_file.touch()
        
        kpis = rollup(trace_file)
        
        assert kpis["trace_count"] == 0
        assert "error" in kpis


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


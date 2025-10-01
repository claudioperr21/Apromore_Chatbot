#!/usr/bin/env python3
"""
Performance Metrics Viewer
==========================

View KPI and performance metrics from the chatbot system.
"""

import json
from pathlib import Path
from datetime import datetime
from backend.kpi_rollup import rollup_today, read_traces

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def format_percentage(value):
    """Format a value as percentage"""
    if value is None:
        return "N/A"
    return f"{value*100:.2f}%"

def format_number(value, decimals=2):
    """Format a number"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"

def view_kpis():
    """View today's KPIs"""
    traces_dir = Path("./logs")
    
    print_section("📊 TODAY'S PERFORMANCE METRICS")
    
    try:
        kpis = rollup_today(traces_dir)
        
        if kpis.get("error"):
            print(f"\n⚠️  {kpis['error']}")
            print("\nNo metrics available yet. Start using the chatbot to generate data!")
            return
        
        # Overview
        print(f"\n📅 Date: {kpis['date']}")
        print(f"📝 Total Requests: {kpis['trace_count']}")
        
        # Accuracy Metrics
        print_section("✅ ACCURACY METRICS")
        print(f"  Grounded Accuracy Rate: {format_percentage(kpis.get('grounded_accuracy_rate'))}")
        print(f"  Routing Accuracy: {format_percentage(kpis.get('routing_accuracy'))}")
        print(f"  Hallucination Rate: {format_percentage(kpis.get('hallucination_rate'))}")
        print(f"  Contradiction Rate: {format_percentage(kpis.get('contradiction_rate'))}")
        
        # Latency Metrics
        print_section("⚡ LATENCY METRICS")
        latency = kpis.get('latency', {}).get('overall', {})
        print(f"  P50 (Median): {format_number(latency.get('p50_total'))} ms")
        print(f"  P95: {format_number(latency.get('p95_total'))} ms")
        print(f"  Mean: {format_number(latency.get('mean_total'))} ms")
        
        if latency.get('p50_model'):
            print(f"\n  Model Latency:")
            print(f"    P50: {format_number(latency.get('p50_model'))} ms")
            print(f"    P95: {format_number(latency.get('p95_model'))} ms")
        
        # Per-endpoint Latency
        endpoint_latency = kpis.get('latency', {}).get('by_endpoint', {})
        if endpoint_latency:
            print(f"\n  By Endpoint:")
            for endpoint, metrics in endpoint_latency.items():
                print(f"    {endpoint}:")
                print(f"      P50: {format_number(metrics.get('p50_total'))} ms")
                print(f"      P95: {format_number(metrics.get('p95_total'))} ms")
        
        # Adoption Metrics
        print_section("👥 ADOPTION METRICS")
        adoption = kpis.get('adoption', {})
        print(f"  Active Users (DAU): {adoption.get('wau', 0)}")
        print(f"  Total Sessions: {adoption.get('sessions', 0)}")
        print(f"  Queries per Session: {format_number(adoption.get('queries_per_session'))}")
        print(f"  Total Queries: {adoption.get('total_queries', 0)}")
        
        # Resolution Metrics
        print_section("🎯 RESOLUTION METRICS")
        resolution = kpis.get('resolution', {})
        print(f"  Session Resolution Rate: {format_percentage(resolution.get('sessions_resolved_rate'))}")
        print(f"  Turns to Resolution (P50): {format_number(resolution.get('turns_to_resolution_p50'))}")
        
        # Metric Parity (MAPE)
        print_section("📏 METRIC PARITY (MAPE)")
        mape = kpis.get('metric_parity_mape', {})
        if mape:
            for metric, value in mape.items():
                print(f"  {metric}: {format_number(value)}%")
        else:
            print("  No metric parity data available")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error loading metrics: {e}")
        print("\nMake sure the logs directory exists and contains trace files.")

def view_raw_traces():
    """View raw trace data"""
    traces_dir = Path("./logs")
    today_str = datetime.now().strftime("%Y%m%d")
    trace_file = traces_dir / f"traces-{today_str}.jsonl"
    
    print_section("📝 RAW TRACE DATA")
    
    if not trace_file.exists():
        print(f"\n⚠️  No trace file found for today: {trace_file}")
        print("\nTry using the chatbot first to generate trace data!")
        return
    
    traces = read_traces(trace_file)
    print(f"\nTotal traces: {len(traces)}")
    
    if traces:
        print("\nRecent traces (last 5):")
        for i, trace in enumerate(traces[-5:], 1):
            print(f"\n  {i}. Endpoint: {trace.get('endpoint')}")
            print(f"     Dataset: {trace.get('dataset')}")
            print(f"     Intent: {trace.get('intent')}")
            print(f"     Latency: {trace.get('latency_ms_total')} ms")
            print(f"     Timestamp: {trace.get('timestamp_utc')}")
            if trace.get('error'):
                print(f"     ❌ Error: {trace.get('error')}")

def main():
    """Main function"""
    import sys
    
    print("\n" + "="*60)
    print("  🎯 APROMORE CHATBOT - PERFORMANCE METRICS")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--raw':
        view_raw_traces()
    else:
        view_kpis()
        print("\n💡 Tip: Run with --raw flag to see raw trace data")
        print("   Example: python view_metrics.py --raw\n")

if __name__ == "__main__":
    main()


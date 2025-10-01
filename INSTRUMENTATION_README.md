# Apromore Chatbot Instrumentation & KPI Tracking

## Overview

This document describes the comprehensive instrumentation system added to the Apromore Chatbot backend. The system provides privacy-safe telemetry, auto-verification, quality metrics, and performance monitoring.

## Key Features

### 1. **Request/Response Telemetry**
- Automatic logging of all API requests to JSONL trace files
- Privacy-safe: no PII or raw prompts exposed in public endpoints
- Daily rotating log files: `logs/traces-YYYYMMDD.jsonl`

### 2. **Auto-Verification**
- **Grounded Accuracy (GA)**: Automatically extracts numeric claims from AI responses and verifies them against pandas recomputations
- **Metric Parity with Dashboard (MPD)**: Ensures metrics match dashboard calculations within tolerance
- Supports multiple claim formats: explicit values, percentages, ranges, and structured facts blocks

### 3. **Router Accuracy Tracking**
- Monitors whether the orchestrator selects the correct dataset
- Detects when users explicitly mention a dataset and tracks routing correctness
- Enables Dataset Routing Accuracy (DRA) analysis

### 4. **Hallucination Detection**
- Schema dictionary validates references to columns, teams, activities, users
- Detects when AI mentions unknown entities
- Refreshable cache with 10-minute TTL

### 5. **KPI Aggregation**
- Daily rollup of key metrics
- Available via `/api/kpis/today` endpoint
- Metrics include:
  - Grounded accuracy rate
  - Routing accuracy
  - Metric parity MAPE
  - Hallucination rate
  - Contradiction rate (within sessions)
  - Latency percentiles (p50, p95)
  - Adoption metrics (WAU, sessions, queries/session)
  - Resolution metrics

### 6. **Facts Blocks**
- Agents emit machine-readable JSON facts blocks
- Zero-regex parsing for extracted metrics
- Format:
  ```facts
  {
    "dataset": "sf",
    "filters": {"team": "Sales"},
    "metrics": {
      "flow_efficiency": 0.62,
      "handoffs": 14
    }
  }
  ```

## Architecture

### New Modules

#### `backend/schema_dict.py`
- `SchemaDict`: Builds and caches dataset schemas
- `build_schema_dict()`: Initialize global schema dictionary
- `validate_references()`: Check for hallucinated entities

#### `backend/metrics.py`
- `flow_efficiency()`: Calculate flow efficiency ratio
- `case_aging_buckets()`: Age distribution of cases
- `throughput_minutes()`: Average case throughput
- `handoffs()`: Average handoffs per case
- `compute_panel_metrics()`: Compute standard metric panel
- `filter_dataframe()`: Apply filters to dataset slices

#### `backend/kpi_verifier.py`
- `extract_numeric_claims()`: Parse numeric claims from text
- `recompute_metrics()`: Verify claims against pandas
- `verify_answer()`: Full verification pipeline

#### `backend/kpi_rollup.py`
- `rollup()`: Compute daily KPI aggregation
- `rollup_today()`: Get today's KPIs
- Multiple compute functions for each KPI category

### Modified Files

#### `backend/config.py`
New environment variables:
- `LOG_DIR`: Directory for logs and traces (default: `./logs`)
- `ENABLE_TRACING`: Enable/disable telemetry (default: `True`)
- `TOLERANCE_PCT`: Tolerance for metric comparisons (default: `0.02` = 2%)

#### `backend/app.py`
- Flask `before_request` and `after_request` hooks for telemetry
- Auto-verification integrated into `/api/analyze/<dataset>`
- New endpoints:
  - `/api/kpis/today`: Get today's KPI rollup
  - `/api/summary`: Summary endpoint with telemetry
  - `/api/recommendations`: Recommendations endpoint with telemetry
  - `/api/agent`: Generic agent endpoint with telemetry
- Schema dictionary initialized on startup

#### `main.py`
- `CreativeOrchestrator`: Enhanced with router accuracy tracking
- `append_facts_block()`: Helper to emit facts blocks
- Updated `summary()` and `top_bottlenecks()` to include facts blocks

## Usage

### Configuration

1. **Copy environment template**:
   ```bash
   cp env.template .env
   ```

2. **Set instrumentation variables** in `.env`:
   ```bash
   LOG_DIR=./logs
   ENABLE_TRACING=True
   TOLERANCE_PCT=0.02
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

#### Start Backend with Instrumentation
```bash
cd backend
python app.py
```

Output:
```
[INFO] Schema dictionary initialized for hallucination detection
[INFO] Flask app starting on 0.0.0.0:5000
[INFO] Telemetry enabled: True
[INFO] Log directory: ./logs
```

#### Access KPI Dashboard
```bash
curl http://localhost:5000/api/kpis/today
```

### API Examples

#### Query with Auto-Verification
```bash
curl -X POST http://localhost:5000/api/analyze/salesforce \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: session123" \
  -d '{
    "query": "show me bottlenecks",
    "filters": {"team": "Sales"}
  }'
```

The response will be automatically verified, and telemetry will be logged to `logs/traces-YYYYMMDD.jsonl`.

#### Get KPIs
```bash
curl http://localhost:5000/api/kpis/today | jq .
```

Response:
```json
{
  "date": "20251001",
  "trace_count": 150,
  "grounded_accuracy_rate": 0.94,
  "routing_accuracy": 0.98,
  "metric_parity_mape": {
    "flow_efficiency": 0.015,
    "handoffs": 0.008,
    "overall": 0.012
  },
  "hallucination_rate": 0.02,
  "contradiction_rate": 0.01,
  "latency": {
    "overall": {
      "p50_total": 125.5,
      "p95_total": 380.2,
      "mean_total": 156.7
    }
  },
  "adoption": {
    "wau": 45,
    "sessions": 89,
    "queries_per_session": 3.2
  }
}
```

## Trace File Format

Each trace is one JSON line in `logs/traces-YYYYMMDD.jsonl`:

```json
{
  "timestamp_utc": "2025-10-01T15:23:45",
  "endpoint": "/api/analyze/salesforce",
  "route_version": "v1",
  "dataset": "sf",
  "intent": "kpi_lookup",
  "filters": {"team": "Sales"},
  "request_bytes": 145,
  "response_bytes": 2048,
  "latency_ms_total": 156.7,
  "latency_ms_model": 98.3,
  "model_name": "gpt-3.5-turbo",
  "prompt_tokens": null,
  "completion_tokens": null,
  "error": null,
  "extracted_metrics": {
    "has_numeric_claims": true,
    "grounded_accuracy_pass": true,
    "claims_verified": 3,
    "claims_passed": 3,
    "claims_failed": 0,
    "verification_results": [
      {
        "name": "flow_efficiency",
        "claimed": 0.62,
        "recomputed": 0.618,
        "pass": true,
        "abs_err": 0.002,
        "pct_err": 0.003
      }
    ],
    "hallucination_check": {
      "has_hallucinations": false,
      "unknown_entities": [],
      "checked": true
    }
  },
  "router_selected": "salesforce",
  "router_should_have_selected": "salesforce",
  "router_correct": true,
  "session_id": "session123",
  "user_id": null,
  "resolved": false
}
```

## Metrics Explained

### Grounded Accuracy (GA)
**Definition**: Percentage of turns with numeric claims where all claims pass verification.

**Formula**: `passed_turns / turns_with_numeric_claims`

**Interpretation**:
- `>95%`: Excellent grounding
- `90-95%`: Good grounding
- `<90%`: Review claim extraction and metric logic

### Metric Parity with Dashboard (MPD)
**Definition**: Mean Absolute Percentage Error between claimed and recomputed metrics.

**Formula**: `mean(|claimed - recomputed| / |recomputed|)` for panel metrics

**Panel Metrics**:
- `flow_efficiency`
- `handoffs`
- `throughput_minutes`
- `aging_>14d`
- `case_count`

**Interpretation**:
- `<2%`: Excellent parity
- `2-5%`: Acceptable parity
- `>5%`: Review metric computation logic

### Hallucination Rate
**Definition**: Percentage of answers referencing unknown entities.

**Formula**: `answers_with_unknown_entities / total_answers`

**Checked Entities**:
- Column names
- Team names
- Activity names
- User/resource names

**Interpretation**:
- `<5%`: Low hallucination
- `5-10%`: Moderate hallucination
- `>10%`: High hallucination - review prompts

### Contradiction Rate
**Definition**: Percentage of sessions with contradictory numeric claims for the same metric.

**Formula**: `sessions_with_contradictions / total_sessions`

**Threshold**: Claims differ by >10%

**Interpretation**:
- `<5%`: Consistent responses
- `5-15%`: Some inconsistency
- `>15%`: Review session state management

### Dataset Routing Accuracy (DRA)
**Definition**: Percentage of queries where the router selected the correct dataset.

**Formula**: `correct_routes / routed_queries`

**Detection**: When user explicitly mentions "salesforce" or "amadeus"

**Interpretation**:
- `>95%`: Excellent routing
- `90-95%`: Good routing
- `<90%`: Review routing logic

## Testing

### Run Unit Tests
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_kpi_verifier.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Results
```
tests/test_kpi_verifier.py::test_extract_numeric_claims_basic PASSED
tests/test_kpi_verifier.py::test_extract_numeric_claims_facts_block PASSED
tests/test_kpi_verifier.py::test_recompute_metrics_with_small_dataframe PASSED
tests/test_kpi_verifier.py::test_verify_answer_full_pipeline PASSED
tests/test_rollup.py::test_read_traces_valid_file PASSED
tests/test_rollup.py::test_compute_grounded_accuracy_rate PASSED
tests/test_rollup.py::test_rollup_full PASSED
```

## Best Practices

### 1. **Facts Blocks**
Always emit facts blocks in agent responses:
```python
text = append_facts_block(text, "sf", filters, {
    "flow_efficiency": 0.62,
    "handoffs": 14
})
```

### 2. **Session Tracking**
Include session headers in frontend requests:
```javascript
headers: {
  "X-Session-ID": sessionId,
  "X-User-ID": userId  // optional
}
```

### 3. **Tolerance Configuration**
Adjust tolerance based on metric type:
- **Rates/percentages**: 2% (0.02)
- **Counts**: ±1 absolute
- **Durations**: 2% relative

### 4. **Log Rotation**
Traces rotate daily automatically. For long-term storage:
```bash
# Archive old traces
find logs -name "traces-*.jsonl" -mtime +30 -exec gzip {} \;
```

### 5. **Performance**
- Verification adds ~10-50ms per request
- Schema dict refreshes every 10 minutes
- Trace writes are async with fsync

## Troubleshooting

### Telemetry Not Writing
1. Check `ENABLE_TRACING=True` in `.env`
2. Verify `LOG_DIR` is writable
3. Check disk space
4. Review error logs for write failures

### Verification Failures
1. Check tolerance setting: `TOLERANCE_PCT`
2. Verify claim extraction patterns
3. Review metric computation logic
4. Check for numeric type mismatches

### Hallucination False Positives
1. Verify schema dictionary is initialized
2. Check for typos in schema extraction
3. Review column name normalization
4. Adjust validation patterns

### High Latency
1. Disable verification for non-critical endpoints
2. Reduce schema refresh frequency
3. Sample traces instead of logging all
4. Use async trace writes

## Future Enhancements

### Planned Features
- [ ] Streaming support with token-by-token verification
- [ ] A/B testing framework for routing strategies
- [ ] Real-time KPI dashboard UI
- [ ] Alerting on quality degradation
- [ ] Integration with Prometheus/Grafana
- [ ] Multi-model comparison metrics

### Configuration Options
- [ ] Configurable claim extraction patterns
- [ ] Per-metric tolerance overrides
- [ ] Trace sampling rates
- [ ] Async batch verification

## Support

For issues or questions:
1. Check trace logs: `logs/traces-YYYYMMDD.jsonl`
2. Review KPI endpoint: `/api/kpis/today`
3. Run unit tests: `pytest tests/ -v`
4. Check configuration: `.env` file

## License

Part of Apromore In-company project for ESADE Masters in Business Analytics.


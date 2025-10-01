# Instrumentation Quick Reference Card

## 🚀 Quick Start

### 1. Enable Instrumentation
```bash
# In .env file
LOG_DIR=./logs
ENABLE_TRACING=True
TOLERANCE_PCT=0.02
```

### 2. Start Backend
```bash
cd backend && python app.py
```

### 3. View Today's KPIs
```bash
curl http://localhost:5000/api/kpis/today | jq .
```

## 📊 Key Metrics

| Metric | Good | Warning | Action |
|--------|------|---------|--------|
| **Grounded Accuracy** | >95% | 90-95% | <90%: Review claims |
| **Routing Accuracy** | >95% | 90-95% | <90%: Fix router |
| **Metric Parity (MAPE)** | <2% | 2-5% | >5%: Check logic |
| **Hallucination Rate** | <5% | 5-10% | >10%: Review prompts |
| **Latency p95** | <500ms | 500-1000ms | >1s: Optimize |

## 🔍 Common Tasks

### Check Trace Logs
```bash
# Today's traces
tail -f logs/traces-$(date +%Y%m%d).jsonl | jq .

# Search for errors
cat logs/traces-*.jsonl | jq 'select(.error != null)'

# Count by endpoint
cat logs/traces-*.jsonl | jq -r '.endpoint' | sort | uniq -c
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_kpi_verifier.py::test_verify_answer_full_pipeline -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

### Disable Telemetry
```bash
# In .env
ENABLE_TRACING=False

# Restart backend
```

## 💡 Agent Facts Blocks

### Template
```python
from main import append_facts_block

metrics = {
    "flow_efficiency": 0.62,
    "handoffs": 14,
    "case_count": 150
}

text = append_facts_block(text, "sf", filters, metrics)
```

### Result
```
Analysis text here...

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
```

## 🎯 Verification Patterns

### Supported Claim Formats
```python
# Explicit assignment
"flow_efficiency = 0.62"

# Natural language
"14 handoffs for Sales-Ops"

# Averages
"average duration is 45.2 seconds"

# Percentages
"62% flow efficiency"

# Facts block (preferred)
{
  "metrics": {
    "flow_efficiency": 0.62
  }
}
```

## 🔧 Troubleshooting

### Traces Not Writing
1. Check `ENABLE_TRACING=True`
2. Verify `LOG_DIR` writable
3. Check disk space
4. Review error logs

### Verification Failing
1. Check `TOLERANCE_PCT` (default 2%)
2. Verify metric names match
3. Check data types (numeric)
4. Review claim extraction

### High Latency
1. Check verification overhead (~10-50ms)
2. Review model latency
3. Disable verification for specific endpoints
4. Optimize pandas operations

## 📁 File Structure

```
backend/
├── app.py              # Main Flask app with telemetry hooks
├── config.py           # Configuration with new env vars
├── schema_dict.py      # Hallucination detection
├── metrics.py          # Pandas metric functions
├── kpi_verifier.py     # Auto-verification
└── kpi_rollup.py       # Daily KPI aggregation

logs/
├── traces-YYYYMMDD.jsonl    # Daily trace logs
└── kpis-YYYYMMDD.json       # Daily KPI rollups

tests/
├── test_kpi_verifier.py     # Verification tests
└── test_rollup.py           # Rollup tests
```

## 🌐 API Endpoints

### Instrumented
- `POST /api/analyze/<dataset>` - ✅ Auto-verify
- `GET /api/kpis/today` - ✅ Get KPIs
- `POST /api/agent` - ✅ Generic agent
- `GET /api/summary` - ✅ Summary
- `POST /api/recommendations` - ✅ Recommendations

### Headers (Optional)
```javascript
{
  "X-Session-ID": "session-123",
  "X-User-ID": "user-456"
}
```

## 📈 KPI Dashboard

### Access
```bash
curl http://localhost:5000/api/kpis/today
```

### Response
```json
{
  "date": "20251001",
  "trace_count": 150,
  "grounded_accuracy_rate": 0.94,
  "routing_accuracy": 0.98,
  "metric_parity_mape": {
    "overall": 0.012
  },
  "hallucination_rate": 0.02,
  "latency": {
    "overall": {
      "p50_total": 125.5,
      "p95_total": 380.2
    }
  },
  "adoption": {
    "sessions": 89,
    "queries_per_session": 3.2
  }
}
```

## 🧪 Testing Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Traces writing: `ls -lh logs/traces-*.jsonl`
- [ ] KPIs computing: `curl localhost:5000/api/kpis/today`
- [ ] No errors: `grep -i error logs/*.log`
- [ ] Latency acceptable: Check p95 < 500ms
- [ ] Grounded accuracy >90%: Check KPI endpoint

## 🎨 Best Practices

### DO ✅
- Emit facts blocks in agent responses
- Use tolerant comparisons (±2%)
- Include session headers
- Monitor KPI trends weekly
- Archive old traces monthly

### DON'T ❌
- Log PII or raw prompts
- Expose raw traces publicly
- Skip verification for critical endpoints
- Ignore failing tests
- Commit sensitive env vars

## 📚 Documentation

- **Full Guide**: `INSTRUMENTATION_README.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **API Docs**: `README.md`
- **Tests**: `tests/test_*.py`

## 🆘 Support

```bash
# Check logs
tail -100 backend/logs/*.log

# Validate config
python -c "from backend.config import get_config; print(get_config().ENABLE_TRACING)"

# Test connection
curl http://localhost:5000/api/health
```

---

**Version**: 1.0  
**Last Updated**: October 1, 2025  
**Status**: ✅ Production Ready


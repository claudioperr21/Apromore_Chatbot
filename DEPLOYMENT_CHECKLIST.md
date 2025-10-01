# Deployment Checklist - Apromore Chatbot Instrumentation

## Pre-Deployment

### 1. Environment Setup
- [ ] Copy `env.template` to `.env`
- [ ] Set `LOG_DIR=./logs` in `.env`
- [ ] Set `ENABLE_TRACING=True` in `.env`
- [ ] Set `TOLERANCE_PCT=0.02` in `.env`
- [ ] Review and set other configuration variables

### 2. Dependencies
- [ ] Install Python dependencies: `pip install -r requirements.txt`
- [ ] Install test dependencies: `pip install pytest pytest-cov`
- [ ] Verify pandas, numpy, flask installed correctly

### 3. Directory Structure
- [ ] Create logs directory: `mkdir -p logs`
- [ ] Verify write permissions: `touch logs/test.log && rm logs/test.log`
- [ ] Create tests directory (if not exists): `mkdir -p tests`

### 4. Code Review
- [ ] Review `backend/app.py` changes
- [ ] Review `backend/config.py` changes
- [ ] Review `main.py` changes
- [ ] Verify no hardcoded secrets or credentials

## Testing Phase

### 1. Unit Tests
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Verify 19 tests pass (10 verifier + 9 rollup)
- [ ] Check test coverage: `pytest tests/ --cov=backend`
- [ ] Review test output for warnings

### 2. Integration Tests
- [ ] Start backend: `cd backend && python app.py`
- [ ] Check startup logs for instrumentation messages
- [ ] Verify health endpoint: `curl http://localhost:5000/api/health`
- [ ] Test datasets endpoint: `curl http://localhost:5000/api/datasets`

### 3. Telemetry Tests
- [ ] Make a test query: 
  ```bash
  curl -X POST http://localhost:5000/api/analyze/salesforce \
    -H "Content-Type: application/json" \
    -d '{"query": "summary"}'
  ```
- [ ] Verify trace file created: `ls -lh logs/traces-*.jsonl`
- [ ] Check trace contents: `tail -1 logs/traces-*.jsonl | jq .`
- [ ] Verify required fields present in trace

### 4. Verification Tests
- [ ] Make query with numeric claims
- [ ] Check `extracted_metrics` in trace
- [ ] Verify `grounded_accuracy_pass` computed
- [ ] Check `verification_results` array

### 5. KPI Tests
- [ ] Access KPI endpoint: `curl http://localhost:5000/api/kpis/today`
- [ ] Verify JSON response with all metrics
- [ ] Check no PII or raw prompts exposed
- [ ] Verify metric calculations reasonable

## Performance Validation

### 1. Latency Tests
- [ ] Measure baseline latency (no instrumentation)
- [ ] Measure instrumented latency
- [ ] Verify overhead <50ms per request
- [ ] Check p95 latency acceptable

### 2. Load Tests
- [ ] Run 100 concurrent requests
- [ ] Monitor memory usage
- [ ] Check trace file size
- [ ] Verify no crashes or errors

### 3. Resource Usage
- [ ] Monitor CPU usage during queries
- [ ] Check memory footprint
- [ ] Verify disk space sufficient
- [ ] Review log rotation working

## Security Review

### 1. Privacy
- [ ] Verify no PII in traces
- [ ] Check no raw prompts in public endpoints
- [ ] Review session ID handling
- [ ] Verify user ID optional

### 2. Access Control
- [ ] Verify `/api/kpis/today` doesn't expose sensitive data
- [ ] Check trace files have appropriate permissions
- [ ] Review CORS settings
- [ ] Verify API authentication if required

### 3. Error Handling
- [ ] Test with invalid inputs
- [ ] Verify fail-soft behavior (no crashes)
- [ ] Check error messages don't leak info
- [ ] Review exception handling

## Documentation Review

### 1. Files Present
- [ ] `INSTRUMENTATION_README.md` exists and complete
- [ ] `IMPLEMENTATION_SUMMARY.md` exists and accurate
- [ ] `QUICK_REFERENCE.md` exists and helpful
- [ ] `DEPLOYMENT_CHECKLIST.md` (this file) complete

### 2. Code Documentation
- [ ] All new modules have docstrings
- [ ] All new functions documented
- [ ] Complex logic has inline comments
- [ ] Type hints present where helpful

### 3. User Guides
- [ ] Quick start instructions clear
- [ ] API examples provided
- [ ] Troubleshooting guide comprehensive
- [ ] Configuration documented

## Production Deployment

### 1. Configuration
- [ ] Set `FLASK_ENV=production` in `.env`
- [ ] Set `FLASK_DEBUG=False` in `.env`
- [ ] Set strong `SECRET_KEY` (not default)
- [ ] Review `TOLERANCE_PCT` appropriate for use case
- [ ] Configure `CORS_ORIGINS` for production domains

### 2. Monitoring Setup
- [ ] Set up daily KPI review process
- [ ] Configure alerts for quality degradation
- [ ] Set up disk space monitoring for logs
- [ ] Plan trace file archival strategy

### 3. Backup & Recovery
- [ ] Document rollback procedure
- [ ] Test disabling instrumentation: `ENABLE_TRACING=False`
- [ ] Verify system works without instrumentation
- [ ] Document recovery steps

### 4. Scaling Considerations
- [ ] Review trace file size projections
- [ ] Plan for high-traffic scenarios
- [ ] Consider trace sampling if needed
- [ ] Document multi-instance deployment if required

## Post-Deployment

### 1. Initial Monitoring (Day 1)
- [ ] Check trace files generated correctly
- [ ] Review first day's KPIs
- [ ] Monitor error rates
- [ ] Verify latency acceptable
- [ ] Check disk usage

### 2. Week 1 Review
- [ ] Review grounded accuracy trends
- [ ] Check routing accuracy
- [ ] Analyze hallucination rate
- [ ] Review latency percentiles
- [ ] Check adoption metrics

### 3. Month 1 Review
- [ ] Analyze quality trends
- [ ] Review metric parity
- [ ] Archive old trace files
- [ ] Optimize tolerance settings if needed
- [ ] Document lessons learned

## Rollback Plan

### If Issues Occur

#### Quick Disable
1. Set `ENABLE_TRACING=False` in `.env`
2. Restart backend: `cd backend && python app.py`
3. Verify system operates normally
4. Investigate issues offline

#### Full Rollback
1. Check out previous commit before instrumentation
2. Restore original `.env` configuration
3. Restart all services
4. Verify functionality restored
5. Document issues encountered

## Sign-Off

### Development Team
- [ ] Code review completed
- [ ] Tests passing
- [ ] Documentation reviewed
- [ ] Performance validated

### QA Team
- [ ] Integration tests passed
- [ ] Security review completed
- [ ] Load tests satisfactory
- [ ] User acceptance testing done

### Operations Team
- [ ] Monitoring configured
- [ ] Backup procedures documented
- [ ] Rollback plan tested
- [ ] Runbook updated

### Project Manager
- [ ] Stakeholders informed
- [ ] Deployment scheduled
- [ ] Success criteria defined
- [ ] Post-deployment review planned

---

## Deployment Status

- **Prepared By**: Cursor AI Agent
- **Date**: October 1, 2025
- **Version**: 1.0.0
- **Status**: ⏳ Awaiting Final Sign-Off

### Ready for Production?
- [ ] All checklists completed
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Team sign-offs obtained

**When all boxes checked**: ✅ **READY FOR PRODUCTION DEPLOYMENT**

---

## Quick Commands Reference

```bash
# Start backend
cd backend && python app.py

# Run tests
pytest tests/ -v

# Check traces
tail -f logs/traces-$(date +%Y%m%d).jsonl | jq .

# Get KPIs
curl http://localhost:5000/api/kpis/today | jq .

# Disable instrumentation
# Edit .env: ENABLE_TRACING=False
# Restart backend

# Archive old traces
find logs -name "traces-*.jsonl" -mtime +30 -exec gzip {} \;
```

---

**Contact**: Apromore Project Team  
**Support**: See `INSTRUMENTATION_README.md` for troubleshooting


# Dataset Configuration Summary

## Salesforce Dataset

All backend components now use the **team-enabled** Salesforce dataset:

**File:** `SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv`

**Full Path:** `C:\Users\Claudio\Desktop\Apromore\Chatbot\Data Sources\SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv`

### Updated Files

✅ **`main.py`** - Line 60
```python
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
```

✅ **`backend/chat_api.py`** - Line 36
```python
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
```

✅ **`backend/config.py`** - Line 23
```python
SALESFORCE_CSV_FILE = os.getenv('SALESFORCE_CSV_FILE', 'SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv')
```

✅ **`gradio_frontend.py`** - Line 26
```python
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
```

✅ **`generate_sample_aggregates.py`** - Line 16
```python
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
```

## Why This Matters

The `_with_teams` version includes the **team** column, which enables:

### ✅ Team-Based Analytics
- Team performance comparisons
- Team handoff analysis
- Team-level interaction patterns
- Team aging distribution

### ✅ Comprehensive Analytics
- Flow efficiency by team
- Case aging buckets by team
- Team handoff networks
- Input mix by team

### ✅ Advanced Features
- Team filtering in queries
- Multi-team case progression
- Team-level KPI rollup

## Verification

To verify the correct dataset is loaded, start your chatbot and run:

```
summary
```

The response should include team information like:
```
Salesforce synthetic task-mining dataset summary:
- rows: 10000
- unique users: 100
- teams: 5  ← This confirms teams are loaded!
- avg duration (s): 42.15
```

## Environment Variable Override

You can also override this in your `.env` file:

```bash
SALESFORCE_CSV_FILE=SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv
```

This ensures consistent configuration across all components.

## Dataset Features

### With Teams (`_with_teams.csv`)
- ✅ 10,000 events
- ✅ 100 unique users
- ✅ **5 teams** (Sales, Support, Operations, etc.)
- ✅ Team column for group analysis
- ✅ Full comprehensive analytics support

### Without Teams (original)
- ⚠️ Same data but missing team column
- ⚠️ Limited team-based analytics
- ⚠️ Some comprehensive features unavailable

## Recommendation

**Always use the `_with_teams` version** for full functionality! ✅

---

**Status:** ✅ **All Files Updated**  
**Effective:** Immediately (restart backend if running)  
**Impact:** Enhanced team analytics now available


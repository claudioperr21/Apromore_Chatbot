# Chat API - Comprehensive Analytics Endpoints

## Overview

The backend chat API (`backend/chat_api.py`) now includes comprehensive analytics endpoints that provide **text-based insights** without requiring chart visualization.

## Base URL

```
http://localhost:5000
```

## New Endpoints

### 1. Check Analytics Availability

**Endpoint:** `GET /api/analytics/available`

**Description:** Check if comprehensive analytics are available and what types of analyses are supported.

**Example Request:**
```bash
curl http://localhost:5000/api/analytics/available
```

**Example Response:**
```json
{
  "comprehensive_analytics_available": true,
  "has_aggregate_data": true,
  "available_analyses": [
    {
      "type": "case_aging",
      "description": "Case aging distribution analysis",
      "keywords": ["aging", "age", "old", "stale"]
    },
    {
      "type": "flow_efficiency",
      "description": "Flow efficiency (touch vs wait time)",
      "keywords": ["flow", "efficiency", "touch", "wait"]
    },
    {
      "type": "handoffs",
      "description": "Team handoff analysis",
      "keywords": ["handoff", "handoffs", "transition", "transfer"]
    },
    {
      "type": "interactions",
      "description": "User interaction patterns",
      "keywords": ["interaction", "clicks", "keys", "effort"]
    },
    {
      "type": "comprehensive",
      "description": "Complete analytics summary",
      "keywords": ["comprehensive", "complete", "all", "summary"]
    }
  ],
  "supported_datasets": ["salesforce", "amadeus"],
  "timestamp": "2025-10-01T12:00:00"
}
```

---

### 2. Query Comprehensive Analytics

**Endpoint:** `POST /api/analytics/comprehensive`

**Description:** Query comprehensive analytics using natural language.

**Request Body:**
```json
{
  "query": "What is the case aging distribution?",
  "dataset": "salesforce"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/analytics/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the case aging distribution?",
    "dataset": "salesforce"
  }'
```

**Example Response:**
```json
{
  "response": "Case Aging Analysis for Salesforce:\n• Total cases analyzed: 1,234\n• Cases aged 0-1 days: 456 (37.0%)\n• Cases aged 1-3 days: 321 (26.0%)\n• Cases aged 3-7 days: 234 (19.0%)\n• Cases aged 7-14 days: 156 (12.6%)\n• Cases aged >14 days: 67 (5.4%)\n\nKey Insight: 67 cases (5.4%) are over 14 days old, which may indicate bottlenecks or stalled processes.",
  "dataset": "salesforce",
  "query": "What is the case aging distribution?",
  "timestamp": "2025-10-01T12:00:00",
  "type": "comprehensive_analytics"
}
```

**Supported Query Keywords:**
- **Case Aging**: "aging", "age", "old", "stale"
- **Flow Efficiency**: "flow", "efficiency", "touch", "wait"
- **Handoffs**: "handoff", "handoffs", "transition", "transfer"
- **Interactions**: "interaction", "clicks", "keys", "effort", "mouse", "keyboard"
- **Summary**: "comprehensive", "complete", "all", "everything", "summary"

---

### 3. Get Specific Analytics Type

**Endpoint:** `GET /api/analytics/{analysis_type}/{dataset}`

**Description:** Get a specific type of analytics for a dataset.

**Path Parameters:**
- `analysis_type`: Type of analysis (aging, flow, handoffs, interactions, summary)
- `dataset`: Dataset name (salesforce, amadeus)

**Query Parameters:**
- `level` (optional, for interactions): team or resource

**Example Requests:**

#### Case Aging
```bash
curl http://localhost:5000/api/analytics/aging/salesforce
```

#### Flow Efficiency
```bash
curl http://localhost:5000/api/analytics/flow/salesforce
```

#### Team Handoffs
```bash
curl http://localhost:5000/api/analytics/handoffs/salesforce
```

#### Team Interactions
```bash
curl http://localhost:5000/api/analytics/interactions/salesforce?level=team
```

#### Resource Interactions
```bash
curl http://localhost:5000/api/analytics/interactions/salesforce?level=resource
```

#### Comprehensive Summary
```bash
curl http://localhost:5000/api/analytics/summary/salesforce
```

**Example Response:**
```json
{
  "response": "Flow Efficiency Analysis for Salesforce:\n• Total touch time: 1,234.5 minutes (20.6 hours)\n• Total wait time: 5,678.2 minutes (94.6 hours)\n• Flow efficiency: 17.9%\n\nInterpretation:\n- Flow efficiency shows the ratio of value-add time to total time\n- Current efficiency of 17.9% means 82.1% of time is spent waiting\n- Industry benchmark for good flow efficiency is typically 15-25%\n- Your current rate is within industry benchmarks",
  "dataset": "salesforce",
  "analysis_type": "flow",
  "timestamp": "2025-10-01T12:00:00"
}
```

---

## Integration with Chat Endpoint

The comprehensive analytics are **automatically integrated** into the main chat endpoint:

**Endpoint:** `POST /api/chat`

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the flow efficiency?",
    "dataset": "salesforce"
  }'
```

The chat endpoint will automatically detect analytics queries and route them to the comprehensive analytics system, returning text-based insights in the response.

---

## Error Responses

### Analytics Not Available
```json
{
  "error": "Comprehensive analytics not available",
  "message": "Aggregate data files may be missing from mnt/data/aggregates/"
}
```
**Status Code:** 503

### Invalid Dataset
```json
{
  "error": "Invalid dataset: invalid_name",
  "supported_datasets": ["salesforce", "amadeus"]
}
```
**Status Code:** 400

### Invalid Analysis Type
```json
{
  "error": "Invalid analysis type: invalid_type",
  "supported_types": ["aging", "flow", "handoffs", "interactions", "summary"]
}
```
**Status Code:** 400

---

## Data Requirements

Comprehensive analytics require pre-aggregated CSV files in the following directory structure:

```
mnt/data/aggregates/
├── salesforce/
│   ├── sf_case_timeline_gantt.csv
│   ├── sf_case_stage_stack.csv
│   ├── sf_case_wait_touch_waterfall.csv
│   ├── sf_input_mix_by_team.csv
│   ├── sf_effort_rate_by_team.csv
│   ├── sf_resource_effort_leaderboard.csv
│   └── ... (other aggregate files)
└── amadeus/
    ├── ama_case_timeline_gantt.csv
    ├── ama_case_stage_stack.csv
    ├── ama_case_wait_touch_waterfall.csv
    ├── ama_input_mix_by_activity.csv
    └── ... (other aggregate files)
```

If these files are missing, the analytics endpoints will return a 503 error, but the chat system will continue to function normally.

---

## Telemetry

All analytics requests are automatically logged with telemetry metadata:
- Dataset
- Query (first 100 characters)
- Latency
- Errors

Telemetry traces are written to: `logs/traces-YYYYMMDD.jsonl`

---

## Example Use Cases

### Frontend Integration

```javascript
// Check if analytics are available
const checkAnalytics = async () => {
  const response = await fetch('http://localhost:5000/api/analytics/available');
  const data = await response.json();
  console.log('Analytics available:', data.comprehensive_analytics_available);
};

// Query analytics via chat
const queryAnalytics = async (message, dataset) => {
  const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': sessionId
    },
    body: JSON.stringify({ message, dataset })
  });
  const data = await response.json();
  console.log('Response:', data.message);
};

// Get specific analytics
const getFlowEfficiency = async (dataset) => {
  const response = await fetch(`http://localhost:5000/api/analytics/flow/${dataset}`);
  const data = await response.json();
  console.log('Flow Efficiency:', data.response);
};
```

### Python Client

```python
import requests

# Check availability
response = requests.get('http://localhost:5000/api/analytics/available')
print(response.json())

# Query analytics
response = requests.post(
    'http://localhost:5000/api/analytics/comprehensive',
    json={
        'query': 'What is the case aging distribution?',
        'dataset': 'salesforce'
    }
)
print(response.json()['response'])

# Get specific analytics
response = requests.get('http://localhost:5000/api/analytics/flow/salesforce')
print(response.json()['response'])
```

---

## Benefits

✅ **Text-only responses** - No chart rendering required  
✅ **RESTful API** - Standard HTTP endpoints  
✅ **Automatic integration** - Works through chat endpoint  
✅ **Direct access** - Specific analytics endpoints available  
✅ **Telemetry integrated** - All requests logged  
✅ **Graceful degradation** - Falls back if data missing  

---

## Startup Output

When the backend starts with comprehensive analytics enabled:

```
🚀 Starting Task Mining Chat API Server...
System Status: ✅ Ready
Message: System initialized successfully
Telemetry: ✅ Enabled
Comprehensive Analytics: ✅ Available
Log Directory: C:\Users\Claudio\Desktop\Apromore\Chatbot\logs

📊 Available Endpoints:
  • Frontend: http://localhost:3000
  • API Base: http://localhost:5000
  • Health: http://localhost:5000/api/health
  • Chat: POST http://localhost:5000/api/chat
  • KPIs: http://localhost:5000/api/kpis/today
  • Analytics Check: http://localhost:5000/api/analytics/available
  • Comprehensive: POST http://localhost:5000/api/analytics/comprehensive
  • Specific: GET http://localhost:5000/api/analytics/{type}/{dataset}
```

---

## Summary

The comprehensive analytics endpoints provide rich, text-based insights from pre-aggregated process mining data. They integrate seamlessly with the existing chat system while also providing direct API access for custom integrations.

**Ready to use!** Start the backend with `python backend/chat_api.py` and query analytics through the chat or direct API endpoints.


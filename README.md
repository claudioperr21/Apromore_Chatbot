# Task Mining Multi-Agent Analysis System

A comprehensive task mining analysis system that provides interactive data visualization, managerial insights, and automated reporting capabilities using Vega-Lite charts and React components.

## Features

### Core Capabilities
- **Multi-Agent Architecture**: Separate analysis agents for different datasets (Salesforce, Amadeus)
- **Interactive Vega-Lite Charts**: High-quality visualizations that can be exported to PDF
- **React Frontend**: Modern, responsive web interface
- **REST API Backend**: Flask-based API for data processing and chart generation
- **PDF Export**: Generate professional reports with embedded charts
- **Managerial Recommendations**: AI-powered insights for process optimization

### 🆕 Performance Metrics & Instrumentation
- **Request/Response Telemetry**: Automatic logging of all API requests to JSONL trace files
- **Auto-Verification**: Grounded Accuracy (GA) and Metric Parity with Dashboard (MPD)
- **Router Accuracy Tracking**: Dataset Routing Accuracy (DRA) monitoring
- **Hallucination Detection**: Schema validation to detect unknown entity references
- **Daily KPI Rollup**: Aggregated metrics including quality, performance, and adoption
- **Comprehensive Analytics**: Text-based insights for case aging, flow efficiency, handoffs, and interactions
- **Facts Blocks**: Machine-readable metric emission for reliable extraction

## Project Structure

```
Apromore Chatbot/
├── Data Sources/
│   ├── SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv
│   ├── amadeus-demo-full-no-fields.csv
│   └── charts/ (generated charts)
├── backend/
│   ├── app.py (Flask API server with telemetry)
│   ├── chat_api.py (Chat API with comprehensive analytics)
│   ├── config.py (Configuration management)
│   ├── schema_dict.py (Hallucination detection)
│   ├── metrics.py (Pandas metric computations)
│   ├── kpi_verifier.py (Auto-verification system)
│   ├── kpi_rollup.py (Daily KPI aggregation)
│   └── comprehensive_analytics.py (Text-based analytics)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VegaLiteChart.js
│   │   │   ├── DatasetSelector.js
│   │   │   ├── AnalysisPanel.js
│   │   │   └── ExportPanel.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   └── package.json
├── tests/
│   ├── test_kpi_verifier.py (10 verification tests)
│   └── test_rollup.py (9 rollup tests)
├── logs/
│   ├── traces-YYYYMMDD.jsonl (Daily trace logs)
│   └── kpis-YYYYMMDD.json (Daily KPI rollups)
├── mnt/data/aggregates/ (Pre-computed analytics)
│   ├── salesforce/ (7 aggregate files)
│   └── amadeus/ (3 aggregate files)
├── main.py (Main application with AI chat)
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Environment Setup

Copy the environment template and configure your settings:

```bash
# Copy the environment template
cp env.template .env

# Edit the .env file with your specific paths and settings
# The most important setting is DATA_BASE_DIR pointing to your CSV files
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Test the System

```bash
python test_system.py
```

### 4. Start the System

**Option A: Main Application (AI Chat Interface - Recommended)**
```bash
python main.py
# or on Windows:
run_main.bat
```

**Option B: Web Interface**
```bash
python start_system.py --mode web
```

**Option C: Manual Start**
```bash
# Start backend
cd backend
python app.py

# In another terminal, start frontend
cd frontend
npm start
```

**Option D: CLI Only**
```bash
python start_system.py --mode cli
```

### 5. Access the Application

- **Web Interface**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

## Usage

### Web Interface

1. **Select Dataset**: Choose between Salesforce or Amadeus datasets
2. **Run Analysis**: Use quick analysis buttons or custom queries
3. **View Charts**: Interactive Vega-Lite visualizations
4. **Export Reports**: Generate PDF reports with selected charts

### Available Analysis Types

#### Salesforce Dataset
- **Summary**: Overview of users, teams, and average durations
- **Bottlenecks**: Activities with longest average durations
- **Team Performance**: Performance comparison across teams
- **App Usage**: Application usage patterns
- **Time Analysis**: Temporal patterns and peak efficiency hours

#### Amadeus Dataset
- **Summary**: Dataset overview and activity distribution
- **Bottlenecks**: Process bottlenecks identification
- **Process Analysis**: Application usage patterns
- **User Efficiency**: User performance analysis

### API Endpoints

#### Core Endpoints
- `GET /api/datasets` - List available datasets
- `POST /api/analyze/{dataset}` - Run custom analysis with auto-verification
- `GET /api/chart/{dataset}/{chart_type}` - Get specific chart
- `POST /api/export/pdf` - Export PDF report
- `GET /api/data/{dataset}/info` - Get dataset information

#### 🆕 Performance & Metrics Endpoints
- `GET /api/kpis/today` - Get today's KPI dashboard (grounded accuracy, latency, adoption)
- `GET /api/health` - Health check with system status

#### 🆕 Comprehensive Analytics Endpoints
- `GET /api/analytics/available` - Check analytics availability
- `POST /api/analytics/comprehensive` - Query analytics with natural language
- `GET /api/analytics/{type}/{dataset}` - Get specific analytics (aging, flow, handoffs, interactions, summary)

## Chart Types and Visualizations

### Vega-Lite Chart Specifications

The system generates interactive Vega-Lite charts that include:

- **Bar Charts**: For categorical comparisons (bottlenecks, team performance)
- **Line Charts**: For temporal analysis
- **Scatter Plots**: For correlation analysis (user efficiency)
- **Multi-panel Charts**: Combined visualizations

### Export Formats

- **HTML**: Interactive charts with zoom/pan capabilities
- **Vega-Lite JSON**: Raw chart specifications for custom use
- **PDF**: Professional reports with embedded chart images

## Managerial Recommendations

The system provides actionable insights:

1. **Process Standardization**: Identify activities needing SOPs
2. **Automation Opportunities**: Highlight repetitive tasks
3. **Resource Allocation**: Team performance optimization
4. **Escalation Triggers**: Set up alerts for bottlenecks

## Environment Configuration

The system uses environment variables for configuration. Key settings include:

### Essential Settings
- `DATA_BASE_DIR`: Path to your CSV data directory
- `SALESFORCE_CSV_FILE`: Name of Salesforce CSV file
- `AMADEUS_CSV_FILE`: Name of Amadeus CSV file
- `FLASK_PORT`: Backend server port (default: 5000)
- `SECRET_KEY`: Flask secret key (change in production)

### Chart Configuration
- `CHART_WIDTH`: Default chart width (default: 800)
- `CHART_HEIGHT`: Default chart height (default: 500)
- `CHART_DPI`: Chart resolution for exports (default: 300)

### Analysis Settings
- `DEFAULT_CHART_LIMIT`: Maximum items in charts (default: 20)
- `BOTTLENECK_THRESHOLD_PERCENTILE`: Bottleneck threshold (default: 80)

### 🆕 Instrumentation & KPI Settings
- `LOG_DIR`: Directory for logs and traces (default: ./logs)
- `ENABLE_TRACING`: Enable telemetry and tracing (default: True)
- `TOLERANCE_PCT`: Tolerance for metric verification (default: 0.02 = 2%)

### Example .env File
```bash
# Data Sources
DATA_BASE_DIR=./Data Sources
SALESFORCE_CSV_FILE=SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv
AMADEUS_CSV_FILE=amadeus-demo-full-no-fields.csv

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here

# Chart Settings
CHART_WIDTH=800
CHART_HEIGHT=500
CHART_DPI=300

# 🆕 Instrumentation & KPI Settings
LOG_DIR=./logs
ENABLE_TRACING=True
TOLERANCE_PCT=0.02
```

## Customization

### Adding New Chart Types

1. Extend the agent classes in `task_mining_multi_agent.py`
2. Add new methods for chart generation
3. Update the frontend chart type lists
4. Add corresponding API endpoints

### Custom Data Sources

1. Create new agent class inheriting from `Agent`
2. Implement column detection logic
3. Add dataset-specific analysis methods
4. Update the orchestrator configuration

## Troubleshooting

### Common Issues

1. **CSV Loading Errors**: Check file paths and column names
2. **Chart Rendering Issues**: Verify Vega-Lite dependencies
3. **PDF Export Problems**: Ensure matplotlib and reportlab are installed
4. **API Connection**: Check backend server status

### Data Requirements

CSV files should contain columns for:
- User/Resource identification
- Activity/Step information
- Duration/Timing data
- Team/Process classification (optional)

## Performance Metrics & Monitoring

### 🎯 Key Performance Indicators (KPIs)

The system automatically tracks and aggregates the following metrics:

#### Quality Metrics
- **Grounded Accuracy (GA)**: Percentage of AI responses with verified numeric claims
  - **Target**: >95% | **Warning**: 90-95% | **Action**: <90%
- **Metric Parity (MPD)**: Mean Absolute Percentage Error vs dashboard calculations
  - **Target**: <2% | **Warning**: 2-5% | **Action**: >5%
- **Hallucination Rate**: Percentage of responses with unknown entity references
  - **Target**: <5% | **Warning**: 5-10% | **Action**: >10%
- **Contradiction Rate**: Sessions with conflicting metric claims
  - **Target**: <5% | **Warning**: 5-15% | **Action**: >15%
- **Dataset Routing Accuracy (DRA)**: Correctness of dataset selection
  - **Target**: >95% | **Warning**: 90-95% | **Action**: <90%

#### Performance Metrics
- **Latency Percentiles**: p50, p95, mean for total and model latency
  - **Target**: p95 <500ms | **Warning**: 500-1000ms | **Action**: >1s
- **Throughput**: Requests per minute
- **Error Rate**: Failed requests percentage

#### Adoption Metrics
- **Weekly Active Users (WAU)**: Unique users per week
- **Sessions**: Total chat sessions
- **Queries per Session**: Average interaction depth
- **Resolution Rate**: Percentage of resolved sessions
- **Turns to Resolution**: Median turns needed

### 📊 Accessing Metrics

#### KPI Dashboard
```bash
# Get today's metrics
curl http://localhost:5000/api/kpis/today | jq .

# Response includes:
# - grounded_accuracy_rate
# - routing_accuracy
# - metric_parity_mape
# - hallucination_rate
# - contradiction_rate
# - latency (p50, p95, mean)
# - adoption (WAU, sessions, queries/session)
# - resolution (rate, turns_to_resolution_p50)
```

#### Trace Logs
All requests are logged to `logs/traces-YYYYMMDD.jsonl` with:
- Timestamp, endpoint, dataset, intent
- Request/response sizes
- Latency metrics (total, model)
- Extracted metrics and verification results
- Router accuracy tracking
- Session and user IDs

### 📈 Comprehensive Analytics

The system provides text-based insights from pre-computed aggregates:

#### Available Analytics
- **Case Aging**: Distribution of case ages across buckets (0-1d, 1-3d, 3-7d, 7-14d, >14d)
- **Flow Efficiency**: Ratio of value-add time to total time with industry benchmarks
- **Team Handoffs**: Average handoffs per case and transition patterns
- **User Interactions**: Mouse clicks, keypresses, copy/paste patterns by team/resource

#### Query Examples
```bash
# Via API
curl -X POST http://localhost:5000/api/analytics/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the flow efficiency?", "dataset": "salesforce"}'

# Specific analytics
curl http://localhost:5000/api/analytics/aging/salesforce
curl http://localhost:5000/api/analytics/flow/salesforce
curl http://localhost:5000/api/analytics/handoffs/salesforce
curl http://localhost:5000/api/analytics/interactions/salesforce?level=team

# Via Chat (natural language)
# Just ask: "What's the flow efficiency?" or "Show me case aging"
```

### 🔍 Auto-Verification System

The system automatically verifies numeric claims in AI responses:

#### Verification Process
1. **Extract Claims**: Parse numeric statements from responses
2. **Recompute Metrics**: Calculate actual values using pandas
3. **Compare**: Check if claimed values match recomputed (within tolerance)
4. **Log Results**: Track pass/fail for quality monitoring

#### Supported Claim Formats
- Explicit: `flow_efficiency = 0.62`
- Natural: `14 handoffs for Sales-Ops`
- Averages: `average duration is 45.2 seconds`
- Percentages: `62% flow efficiency`
- Facts blocks: JSON-formatted metrics

#### Tolerance Settings
- **Rates/Percentages**: ±2% (configurable via `TOLERANCE_PCT`)
- **Counts**: ±1 absolute
- **Durations**: ±2% relative

## Development

### Running Tests

```bash
# Run all tests (19 tests)
pytest tests/ -v

# Expected output:
# tests/test_kpi_verifier.py::10 PASSED
# tests/test_rollup.py::9 PASSED
# ==================== 19 passed ====================

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Code Formatting

```bash
black .
flake8 .
```

### Adding Dependencies

Update `requirements.txt` for Python packages and `frontend/package.json` for Node.js packages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Apromore In-company project for ESADE Masters in Business Analytics.

## Documentation

### 📚 Comprehensive Guides

This repository includes extensive documentation:

1. **[INSTRUMENTATION_README.md](INSTRUMENTATION_README.md)** - Complete instrumentation and KPI tracking guide
2. **[COMPREHENSIVE_ANALYTICS_GUIDE.md](COMPREHENSIVE_ANALYTICS_GUIDE.md)** - Text-based analytics usage
3. **[CHAT_API_COMPREHENSIVE_ANALYTICS.md](CHAT_API_COMPREHENSIVE_ANALYTICS.md)** - API documentation for analytics endpoints
4. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Developer quick reference card
5. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Detailed implementation report
6. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment guide
7. **[DATASET_CONFIGURATION.md](DATASET_CONFIGURATION.md)** - Dataset configuration summary

### 📖 Quick Links

- **Getting Started**: See [Quick Start](#quick-start) section above
- **API Reference**: See [API Endpoints](#api-endpoints) section
- **Metrics Guide**: See [INSTRUMENTATION_README.md](INSTRUMENTATION_README.md)
- **Analytics Guide**: See [COMPREHENSIVE_ANALYTICS_GUIDE.md](COMPREHENSIVE_ANALYTICS_GUIDE.md)
- **Deployment**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## Performance Benchmarks

### Typical Response Times
- **Simple Query** (summary, bottlenecks): 50-150ms
- **With Verification**: 60-200ms (adds ~10-50ms)
- **With Charts**: 100-300ms
- **Comprehensive Analytics**: <100ms (pre-computed aggregates)

### Throughput
- **Requests per Second**: 10-50 (single process)
- **Concurrent Users**: 20-50 (Flask development server)
- **For Production**: Use gunicorn or uwsgi for higher throughput

### Resource Usage
- **Memory**: 100-300 MB (depends on dataset size)
- **Disk (Traces)**: ~1-10 MB per day (depends on traffic)
- **CPU**: Low (<10% idle, spikes during analysis)

## Monitoring & Quality Assurance

### Real-Time Monitoring
```bash
# View live traces
tail -f logs/traces-$(date +%Y%m%d).jsonl | jq .

# Check today's KPIs
curl http://localhost:5000/api/kpis/today | jq '{
  grounded_accuracy: .grounded_accuracy_rate,
  routing_accuracy: .routing_accuracy,
  hallucination_rate: .hallucination_rate,
  latency_p95: .latency.overall.p95_total
}'

# Count requests by endpoint
cat logs/traces-*.jsonl | jq -r '.endpoint' | sort | uniq -c
```

### Quality Thresholds

| Metric | Excellent | Good | Needs Review |
|--------|-----------|------|--------------|
| Grounded Accuracy | >95% | 90-95% | <90% |
| Metric Parity (MAPE) | <2% | 2-5% | >5% |
| Routing Accuracy | >95% | 90-95% | <90% |
| Hallucination Rate | <5% | 5-10% | >10% |
| Latency p95 | <500ms | 500-1000ms | >1s |

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the comprehensive documentation guides
3. Check the console logs: `logs/traces-*.jsonl`
4. View metrics dashboard: `http://localhost:5000/api/kpis/today`
5. Run tests: `pytest tests/ -v`
6. Verify data file formats and paths

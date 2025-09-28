# Task Mining Multi-Agent Analysis System

A comprehensive task mining analysis system that provides interactive data visualization, managerial insights, and automated reporting capabilities using Vega-Lite charts and React components.

## Features

- **Multi-Agent Architecture**: Separate analysis agents for different datasets (Salesforce, Amadeus)
- **Interactive Vega-Lite Charts**: High-quality visualizations that can be exported to PDF
- **React Frontend**: Modern, responsive web interface
- **REST API Backend**: Flask-based API for data processing and chart generation
- **PDF Export**: Generate professional reports with embedded charts
- **Managerial Recommendations**: AI-powered insights for process optimization

## Project Structure

```
Apromore Chatbot/
├── Data Sources/
│   ├── SalesforceOffice_synthetic_varied_100users_V1.csv
│   ├── amadeus-demo-full-no-fields.csv
│   └── charts/ (generated charts)
├── backend/
│   └── app.py (Flask API server)
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

- `GET /api/datasets` - List available datasets
- `POST /api/analyze/{dataset}` - Run custom analysis
- `GET /api/chart/{dataset}/{chart_type}` - Get specific chart
- `POST /api/export/pdf` - Export PDF report
- `GET /api/data/{dataset}/info` - Get dataset information

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

### Example .env File
```bash
# Data Sources
DATA_BASE_DIR=C:\Users\claud\OneDrive\Desktop\ESADE\Masters in Busienss Analytics\Apromore In-company project\Apromore Chatbot\Data Sources
SALESFORCE_CSV_FILE=SalesforceOffice_synthetic_varied_100users_V1.csv
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

## Development

### Running Tests

```bash
pytest tests/
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

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check the console logs for error messages
4. Verify data file formats and paths

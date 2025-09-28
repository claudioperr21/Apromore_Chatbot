# React Frontend for Task Mining System

A modern React-based web interface for the Task Mining Multi-Agent System with AI chat capabilities, running on `https://localhost:3000`.

## 🚀 Features

### 💬 AI Chat Interface
- **Natural Language Processing**: Ask questions in plain English
- **Real-time Chat**: Interactive conversation with AI
- **Smart Responses**: Creative AI with higher temperature for diverse responses
- **Chart Integration**: Automatic chart generation for relevant queries
- **Chat History**: Persistent conversation tracking

### 📊 Interactive Visualizations
- **Vega-Lite Charts**: High-quality, interactive visualizations
- **Real-time Updates**: Charts update based on your queries
- **Export Capabilities**: Download charts and chat history
- **Responsive Design**: Works on desktop and mobile

### 🔄 Multi-Dataset Support
- **Dataset Switching**: Toggle between Salesforce and Amadeus datasets
- **Context Awareness**: AI remembers which dataset you're using
- **Quick Actions**: One-click access to common analyses

## 🛠️ Installation & Setup

### Prerequisites
- **Node.js 16+**: For React development
- **Python 3.8+**: For backend API
- **npm**: Node package manager

### 1. Install Dependencies

#### Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
```

### 2. Setup Environment
```bash
# Copy environment template
copy env.template .env

# Edit .env and add your OpenAI API key
SECRET_KEY=your_openai_api_key_here
```

### 3. Run the System

#### Option A: Automated Startup (Recommended)
```bash
# Windows
run_react_frontend.bat

# This will start both backend and frontend automatically
```

#### Option B: Manual Startup
```bash
# Terminal 1: Start Backend API
cd backend
python chat_api.py

# Terminal 2: Start React Frontend
cd frontend
npm start
```

### 4. Access the Application
- **Frontend**: https://localhost:3000
- **Backend API**: http://localhost:5000

## 🎯 Usage Guide

### Chat Interface
1. **Select Dataset**: Choose between Salesforce or Amadeus
2. **Ask Questions**: Use natural language like:
   - "who is the most active user?"
   - "what are some bottlenecks?"
   - "how many users are there?"
   - "give me insights about the data"
3. **View Charts**: Interactive charts appear automatically
4. **Export Chat**: Download your conversation history

### Quick Actions
- **Summary**: Get dataset overview
- **Bottlenecks**: Find process bottlenecks
- **Team Performance**: Analyze team efficiency (Salesforce only)
- **Recommendations**: Get managerial insights

### Analysis Dashboard
- **Comprehensive Analysis**: Run full dataset analysis
- **Chart Gallery**: Generate specific chart types
- **Export Options**: Download charts and reports

## 🏗️ Architecture

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   └── VegaLiteChart.js    # Chart visualization
│   ├── services/
│   │   └── api.js             # API communication
│   ├── App.js                 # Main application
│   └── index.js               # Entry point
├── package.json               # Dependencies
└── public/
    └── index.html             # HTML template
```

### Backend (Flask)
```
backend/
├── chat_api.py                # Main API server
├── app.py                     # Original Flask app
└── config.py                  # Configuration
```

### API Endpoints
- `POST /api/chat` - Handle chat messages
- `POST /api/analyze/<dataset>` - Analyze dataset
- `GET /api/chart/<dataset>/<type>` - Get specific charts
- `POST /api/switch` - Switch datasets
- `POST /api/export/chat` - Export chat history
- `GET /api/health` - Health check

## 🎨 UI Components

### Chat Interface
- **Message Bubbles**: User and AI messages with timestamps
- **Typing Indicators**: Loading states during AI processing
- **Chart Display**: Embedded Vega-Lite visualizations
- **Export Buttons**: Download chat history and charts

### Dashboard
- **Dataset Selector**: Toggle between datasets
- **Quick Actions**: One-click analysis buttons
- **Analysis Results**: Formatted text and charts
- **Export Options**: Download capabilities

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
SECRET_KEY=your_openai_api_key_here

# Data Paths
DATA_BASE_DIR=Data Sources
SALESFORCE_CSV_FILE=SalesforceOffice_synthetic_varied_100users_V1.csv
AMADEUS_CSV_FILE=amadeus-demo-full-no-fields.csv

# Chart Configuration
CHART_WIDTH=800
CHART_HEIGHT=500
CHART_DPI=300
```

### React Configuration
```javascript
// In frontend/src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

## 📊 Chart Types

### Salesforce Dataset
- **Summary Charts**: User duration analysis
- **Bottleneck Charts**: Activity duration analysis (excluding completed tasks)
- **Team Performance**: Team efficiency analysis
- **App Usage**: Application usage patterns

### Amadeus Dataset
- **Summary Charts**: Activity and user analysis
- **Bottleneck Charts**: Process duration analysis (excluding completed tasks)

## 🐛 Troubleshooting

### Common Issues

#### Frontend Not Loading
- **Cause**: Node.js/npm not installed
- **Solution**: Install Node.js 16+ and npm

#### Backend Connection Failed
- **Cause**: Backend API not running
- **Solution**: Start backend with `python backend/chat_api.py`

#### Charts Not Displaying
- **Cause**: Vega-Lite dependencies missing
- **Solution**: Run `npm install` in frontend directory

#### Chat Not Working
- **Cause**: OpenAI API issues
- **Solution**: Check API key in `.env` file

### Debug Mode
Enable verbose logging by setting:
```javascript
// In frontend/src/services/api.js
api.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});
```

## 🚀 Development

### Adding New Features
1. **New Chat Commands**: Add handlers in `backend/chat_api.py`
2. **New Chart Types**: Extend chart generation functions
3. **New UI Components**: Add React components in `frontend/src/components/`

### Custom Styling
Modify Material-UI theme in `frontend/src/App.js`:
```javascript
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' }
  }
});
```

## 📈 Performance Tips

1. **Large Datasets**: Consider data sampling for very large CSV files
2. **Chart Caching**: Charts are cached - regenerate only when needed
3. **Memory Usage**: Close unused browser tabs
4. **API Limits**: Be mindful of OpenAI API rate limits

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **CORS**: Configured for localhost development only
- **Data Privacy**: Ensure sensitive data is properly handled

## 🎉 Getting Started

1. **Install**: `npm install` in frontend directory
2. **Configure**: Set up your `.env` file with OpenAI API key
3. **Run**: `run_react_frontend.bat` or start manually
4. **Open**: Navigate to https://localhost:3000
5. **Chat**: Start asking questions about your data!

## 📚 API Reference

### Chat Endpoint
```javascript
POST /api/chat
{
  "dataset": "salesforce",
  "message": "who is the most active user?"
}

Response:
{
  "message": "🎯 The most active user is 'User_45' with 127 activities...",
  "chart": "<html>...</html>",
  "chartJson": {...},
  "dataset": "salesforce",
  "timestamp": "2024-12-20T14:30:22"
}
```

### Analysis Endpoint
```javascript
POST /api/analyze/salesforce
{
  "query": "summary"
}

Response:
{
  "text": "Salesforce dataset summary...",
  "chart": "<html>...</html>",
  "chartJson": {...},
  "dataset": "salesforce"
}
```

The React frontend provides a modern, intuitive interface for your task mining analysis system with powerful AI chat capabilities and interactive visualizations! 🎯

# Gradio Frontend for Task Mining System

A modern web interface for the Task Mining Multi-Agent System built with Gradio, providing an intuitive chat interface, interactive charts, and export capabilities.

## 🚀 Features

### 💬 AI Chat Interface
- **Natural Language Processing**: Ask questions in plain English
- **Creative AI Responses**: Higher temperature for diverse, engaging responses
- **Smart Task Filtering**: Automatically excludes completed tasks from bottleneck analysis
- **Multi-Dataset Support**: Switch between Salesforce and Amadeus datasets
- **Real-time Chat History**: Persistent conversation tracking

### 📊 Interactive Charts
- **Vega-Lite Visualizations**: High-quality, interactive charts
- **Chart Gallery**: Generate and view different chart types
- **Export Capabilities**: Download charts as HTML or Vega-Lite JSON
- **Real-time Updates**: Charts update based on your queries

### 📤 Export Features
- **Chat History Export**: Download conversation history as JSON
- **Chart Export**: Save visualizations for reports and presentations
- **Analysis Reports**: Comprehensive dataset analysis with export options

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Copy environment template
copy env.template .env

# Edit .env and add your OpenAI API key
SECRET_KEY=your_openai_api_key_here
```

### 3. Run the Gradio Frontend
```bash
# Direct Python
python gradio_frontend.py

# Or use the batch file (Windows)
run_gradio.bat
```

### 4. Access the Interface
Open your browser and go to: `http://localhost:7860`

## 🎯 Usage Guide

### Chat Interface Tab
1. **Select Dataset**: Choose between Salesforce or Amadeus
2. **Ask Questions**: Use natural language like:
   - "who is the most active user?"
   - "what are some bottlenecks?"
   - "how many users are there?"
   - "give me insights about the data"
3. **View Charts**: Interactive charts appear automatically for relevant queries
4. **Export Chat**: Download your conversation history

### Analysis Dashboard Tab
1. **Select Dataset**: Choose your data source
2. **Run Analysis**: Get comprehensive analysis including:
   - Summary statistics
   - Bottleneck identification
   - Team performance (Salesforce only)
   - Managerial recommendations

### Chart Gallery Tab
1. **Select Dataset**: Choose between Salesforce or Amadeus
2. **Choose Chart Type**: 
   - Summary charts
   - Bottleneck analysis
   - Team performance (Salesforce only)
   - App usage (Salesforce only)
3. **Generate Chart**: Create and view interactive visualizations
4. **Download Chart**: Export as HTML or Vega-Lite JSON

### System Info Tab
- **System Status**: Check initialization and health
- **Refresh System**: Restart the system if needed
- **Feature Overview**: View available capabilities

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI API Configuration
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

### Gradio Server Settings
```python
# In gradio_frontend.py
demo.launch(
    server_name="0.0.0.0",    # Allow external access
    server_port=7860,         # Default Gradio port
    share=False,              # Set to True for public sharing
    show_error=True,          # Show detailed errors
    quiet=False               # Verbose logging
)
```

## 📊 Chart Types Available

### Salesforce Dataset
- **Summary Charts**: User duration analysis
- **Bottleneck Charts**: Activity duration analysis (excluding completed tasks)
- **Team Performance**: Team efficiency analysis
- **App Usage**: Application usage patterns

### Amadeus Dataset
- **Summary Charts**: Activity and user analysis
- **Bottleneck Charts**: Process duration analysis (excluding completed tasks)

## 🎨 Customization

### Styling
The interface uses Gradio's Soft theme. You can customize it by modifying:
```python
with gr.Blocks(title="Task Mining AI Chat System", theme=gr.themes.Soft()) as demo:
```

### Adding New Features
1. **New Chat Commands**: Add handlers in the `handle_chat` function
2. **New Chart Types**: Extend the chart generation functions
3. **New Export Formats**: Add export handlers in the export functions

## 🐛 Troubleshooting

### Common Issues

#### System Not Initialized
- **Cause**: Data files not found or OpenAI API key missing
- **Solution**: Check that CSV files are in the `Data Sources` folder and API key is set

#### Charts Not Displaying
- **Cause**: Altair/Vega-Lite dependencies missing
- **Solution**: Install requirements: `pip install -r requirements.txt`

#### Chat Not Working
- **Cause**: OpenAI API issues or network problems
- **Solution**: Check API key validity and internet connection

#### Port Already in Use
- **Cause**: Another Gradio instance running
- **Solution**: Change port in `gradio_frontend.py` or kill existing process

### Debug Mode
Enable verbose logging by setting:
```python
demo.launch(show_error=True, quiet=False)
```

## 📈 Performance Tips

1. **Large Datasets**: For very large CSV files, consider data sampling
2. **Chart Generation**: Charts are cached - regenerate only when needed
3. **Memory Usage**: Close unused browser tabs to free memory
4. **API Limits**: Be mindful of OpenAI API rate limits

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control
- **Network Access**: The interface binds to `0.0.0.0` - restrict access in production
- **Data Privacy**: Ensure sensitive data is properly handled

## 🚀 Advanced Usage

### Custom Analysis
Add custom analysis functions by extending the orchestrator:
```python
def custom_analysis(dataset, parameters):
    # Your custom analysis logic
    return results
```

### Integration with Other Systems
The Gradio frontend can be integrated with:
- **Jupyter Notebooks**: Use `gr.Interface` in notebooks
- **Streamlit**: Convert Gradio components to Streamlit
- **Flask Apps**: Embed Gradio interfaces in Flask applications

## 📚 API Reference

### Main Functions
- `initialize_system()`: Initialize the task mining system
- `handle_chat(message, history)`: Process chat messages
- `switch_dataset(dataset)`: Switch between datasets
- `export_chat_history(history)`: Export conversation data
- `generate_chart(dataset, chart_type)`: Create visualizations

### Event Handlers
- Chat message processing
- Dataset switching
- Chart generation
- Export functionality
- System status monitoring

## 🎉 Getting Started

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Set up your `.env` file with OpenAI API key
3. **Run**: `python gradio_frontend.py` or `run_gradio.bat`
4. **Open**: Navigate to `http://localhost:7860`
5. **Chat**: Start asking questions about your data!

The Gradio frontend provides a modern, intuitive interface for your task mining analysis system with powerful AI chat capabilities and interactive visualizations! 🎯

# Quick Start Guide

## 🚀 Main Application (Recommended)

The main application provides an AI-powered chat interface for task mining analysis.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
# Copy the template
copy env.template .env

# Edit .env and add your OpenAI API key
SECRET_KEY=your_openai_api_key_here
```

### 3. Run the Application
```bash
# Direct Python
python main.py

# Or use the batch file (Windows)
run_main.bat
```

### 4. Usage Examples

#### Natural Language Queries
```
[salesforce] Your query: who is the most active user?
[salesforce] Your query: what are some bottlenecks?
[salesforce] Your query: how many users are there?
[salesforce] Your query: give me insights about the data
```

#### Traditional Commands
```
[salesforce] Your query: summary
[salesforce] Your query: top bottlenecks
[salesforce] Your query: team performance
[salesforce] Your query: recommendations
```

#### Dataset Switching
```
[salesforce] Your query: switch to amadeus
[amadeus] Your query: summary
```

### 5. Chart Export
When charts are generated, you can export them:
```
Save chart? (y/n): y
Saved → HTML: charts\salesforce_20241220_143022.html | Vega-Lite JSON: charts\salesforce_20241220_143022.vl.json
```

### 6. Features

- **🎨 Creative AI Chat**: Higher temperature for diverse, engaging responses
- **✅ Smart Task Filtering**: Excludes completed tasks from bottleneck analysis
- **📊 Vega-Lite Charts**: Interactive visualizations with export capabilities
- **🔄 Multi-Dataset**: Switch between Salesforce and Amadeus datasets
- **💬 Natural Language**: Ask questions in plain English
- **📈 Managerial Insights**: AI-powered recommendations

### 7. Troubleshooting

#### OpenAI API Issues
- Ensure your API key is correctly set in `.env`
- Check that you have sufficient API credits
- Verify the key has the correct permissions

#### Data Issues
- Ensure CSV files are in the `Data Sources` folder
- Check that column names match expected patterns
- Verify data format and encoding

#### Chart Export Issues
- Check that the `charts` folder exists and is writable
- Ensure Altair and Vega-Lite dependencies are installed
- Verify file permissions in the output directory

## 🎯 Next Steps

1. **Explore the Data**: Start with `summary` to understand your datasets
2. **Find Bottlenecks**: Use `top bottlenecks` to identify process issues
3. **Analyze Teams**: Run `team performance` for team efficiency insights
4. **Get Recommendations**: Use `recommendations` for managerial guidance
5. **Export Charts**: Save visualizations for reports and presentations

## 📚 Additional Resources

- **Full Documentation**: See `README.md` for complete setup
- **Web Interface**: Use `python run_system.py` for the full web application
- **API Access**: Use `python run_cli_only.py` for backend-only mode
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import base64
from PIL import Image as PILImage
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Import our agent classes and configuration
import sys
sys.path.append('..')
from task_mining_multi_agent import SalesforceAgent, AmadeusAgent, load_csv, find_column, save_chart
from config import get_config

# Get configuration
config_class = get_config()
app = Flask(__name__)
app.config.from_object(config_class)
CORS(app, origins=config_class.CORS_ORIGINS)

# Global variables for loaded data
salesforce_agent = None
amadeus_agent = None

def load_data():
    """Load CSV data and initialize agents"""
    global salesforce_agent, amadeus_agent
    
    salesforce_path = config_class.SALESFORCE_PATH
    amadeus_path = config_class.AMADEUS_PATH
    
    # Create charts directory
    os.makedirs(config_class.CHARTS_DIR, exist_ok=True)
    
    if os.path.exists(salesforce_path):
        salesforce_df = load_csv(salesforce_path)
        salesforce_agent = SalesforceAgent(salesforce_df)
    
    if os.path.exists(amadeus_path):
        amadeus_df = load_csv(amadeus_path)
        amadeus_agent = AmadeusAgent(amadeus_df)

def chart_to_base64(chart):
    """Convert Vega-Lite chart to base64 image for PDF export"""
    try:
        # Get chart specification
        chart_spec = chart.to_dict()
        
        # Create matplotlib visualization based on Vega-Lite spec
        fig, ax = plt.subplots(figsize=(config_class.CHART_WIDTH/100, config_class.CHART_HEIGHT/100))
        
        # Extract data
        data = None
        if 'data' in chart_spec:
            if 'values' in chart_spec['data']:
                data = pd.DataFrame(chart_spec['data']['values'])
            elif 'url' in chart_spec['data']:
                # Handle URL data (would need to fetch)
                pass
        
        if data is not None and not data.empty:
            # Extract encoding information
            encoding = chart_spec.get('encoding', {})
            x_encoding = encoding.get('x', {})
            y_encoding = encoding.get('y', {})
            
            x_field = x_encoding.get('field', data.columns[0])
            y_field = y_encoding.get('field', data.columns[1] if len(data.columns) > 1 else data.columns[0])
            
            # Determine chart type
            mark = chart_spec.get('mark', {})
            mark_type = mark if isinstance(mark, str) else mark.get('type', 'bar')
            
            # Create appropriate chart type
            if mark_type in ['bar', 'column']:
                # Bar chart
                if pd.api.types.is_numeric_dtype(data[y_field]):
                    bars = ax.bar(range(len(data)), data[y_field])
                    ax.set_xticks(range(len(data)))
                    ax.set_xticklabels(data[x_field], rotation=45, ha='right')
                    ax.set_ylabel(y_field)
                else:
                    # Count categorical values
                    value_counts = data[x_field].value_counts().head(20)
                    bars = ax.bar(range(len(value_counts)), value_counts.values)
                    ax.set_xticks(range(len(value_counts)))
                    ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                    ax.set_ylabel('Count')
                    
            elif mark_type in ['line', 'area']:
                # Line chart
                if pd.api.types.is_numeric_dtype(data[y_field]):
                    ax.plot(data[x_field], data[y_field], marker='o', linewidth=2, markersize=6)
                    ax.set_xlabel(x_field)
                    ax.set_ylabel(y_field)
                else:
                    # Time series or categorical line
                    value_counts = data[x_field].value_counts()
                    ax.plot(range(len(value_counts)), value_counts.values, marker='o', linewidth=2)
                    ax.set_xticks(range(len(value_counts)))
                    ax.set_xticklabels(value_counts.index, rotation=45, ha='right')
                    ax.set_ylabel('Count')
                    
            elif mark_type == 'point':
                # Scatter plot
                if len(data.columns) >= 2:
                    scatter = ax.scatter(data[x_field], data[y_field], alpha=0.6, s=50)
                    ax.set_xlabel(x_field)
                    ax.set_ylabel(y_field)
                else:
                    # Single variable scatter
                    ax.scatter(range(len(data)), data[x_field], alpha=0.6, s=50)
                    ax.set_xlabel('Index')
                    ax.set_ylabel(x_field)
            
            # Set title
            title = chart_spec.get('title', 'Chart')
            if isinstance(title, dict):
                title = title.get('text', 'Chart')
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Add color if specified
            color_encoding = encoding.get('color', {})
            if color_encoding and 'field' in color_encoding:
                color_field = color_encoding['field']
                if color_field in data.columns:
                    # Use color mapping
                    unique_values = data[color_field].unique()
                    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_values)))
                    color_map = dict(zip(unique_values, colors))
                    
                    if mark_type in ['bar', 'column']:
                        for i, bar in enumerate(bars):
                            if i < len(data):
                                bar.set_color(color_map.get(data.iloc[i][color_field], 'blue'))
            
            # Improve layout
            plt.tight_layout()
            
            # Add grid for better readability
            ax.grid(True, alpha=0.3)
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=config_class.CHART_DPI, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        else:
            # Fallback: create a simple placeholder
            ax.text(0.5, 0.5, 'Chart data not available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=16)
            ax.set_title('Chart', fontsize=14, fontweight='bold')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=config_class.CHART_DPI, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
            
    except Exception as e:
        print(f"Error converting chart to image: {e}")
        # Return a placeholder image
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'Chart rendering error: {str(e)[:50]}...', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('Chart Error', fontsize=14, fontweight='bold')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=config_class.CHART_DPI, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return image_base64
        except:
            return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get available datasets"""
    datasets = []
    
    if salesforce_agent:
        datasets.append({
            "id": "salesforce",
            "name": "Salesforce Office Data",
            "description": "Synthetic CRM task mining data",
            "available": True
        })
    
    if amadeus_agent:
        datasets.append({
            "id": "amadeus", 
            "name": "Amadeus Demo Data",
            "description": "Trial task mining data",
            "available": True
        })
    
    return jsonify({"datasets": datasets})

@app.route('/api/analyze/<dataset>', methods=['POST'])
def analyze_dataset(dataset):
    """Analyze dataset based on query"""
    try:
        data = request.get_json()
        query = data.get('query', 'summary')
        
        agent = None
        if dataset == 'salesforce' and salesforce_agent:
            agent = salesforce_agent
        elif dataset == 'amadeus' and amadeus_agent:
            agent = amadeus_agent
        else:
            return jsonify({"error": "Dataset not found"}), 404
        
        result = agent.handle(query)
        
        # Convert chart to Vega-Lite spec if present
        if 'chart' in result:
            chart_spec = result['chart'].to_dict()
            result['vega_lite_spec'] = chart_spec
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart/<dataset>/<chart_type>', methods=['GET'])
def get_chart(dataset, chart_type):
    """Get specific chart type for dataset"""
    try:
        agent = None
        if dataset == 'salesforce' and salesforce_agent:
            agent = salesforce_agent
        elif dataset == 'amadeus' and amadeus_agent:
            agent = amadeus_agent
        else:
            return jsonify({"error": "Dataset not found"}), 404
        
        # Map chart types to methods
        chart_methods = {
            'summary': agent.summary,
            'bottlenecks': agent.top_bottlenecks,
            'team_performance': getattr(agent, 'team_performance', None),
            'app_usage': getattr(agent, 'app_usage', None),
            'time_analysis': getattr(agent, 'time_analysis', None),
            'process_analysis': getattr(agent, 'process_analysis', None),
            'user_efficiency': getattr(agent, 'user_efficiency', None)
        }
        
        method = chart_methods.get(chart_type)
        if not method:
            return jsonify({"error": "Chart type not supported"}), 400
        
        result = method()
        
        if 'chart' in result:
            chart_spec = result['chart'].to_dict()
            result['vega_lite_spec'] = chart_spec
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Export charts and analysis to PDF"""
    try:
        data = request.get_json()
        dataset = data.get('dataset')
        chart_types = data.get('chart_types', ['summary', 'bottlenecks'])
        title = data.get('title', f'Task Mining Analysis - {dataset.title()}')
        
        agent = None
        if dataset == 'salesforce' and salesforce_agent:
            agent = salesforce_agent
        elif dataset == 'amadeus' and amadeus_agent:
            agent = amadeus_agent
        else:
            return jsonify({"error": "Dataset not found"}), 404
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
        )
        
        story = []
        
        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Add charts
        for chart_type in chart_types:
            chart_methods = {
                'summary': agent.summary,
                'bottlenecks': agent.top_bottlenecks,
                'team_performance': getattr(agent, 'team_performance', None),
                'app_usage': getattr(agent, 'app_usage', None),
                'time_analysis': getattr(agent, 'time_analysis', None),
                'process_analysis': getattr(agent, 'process_analysis', None),
                'user_efficiency': getattr(agent, 'user_efficiency', None)
            }
            
            method = chart_methods.get(chart_type)
            if method:
                result = method()
                
                # Add chart title
                chart_title = chart_type.replace('_', ' ').title()
                story.append(Paragraph(chart_title, styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Add analysis text
                if 'text' in result:
                    story.append(Paragraph(result['text'].replace('\n', '<br/>'), styles['Normal']))
                    story.append(Spacer(1, 12))
                
                # Add chart image
                if 'chart' in result:
                    chart_image = chart_to_base64(result['chart'])
                    if chart_image:
                        img_data = base64.b64decode(chart_image)
                        img_buffer = io.BytesIO(img_data)
                        img = Image(img_buffer, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
        
        # Add recommendations
        recommendations = agent.recommendations()
        if 'text' in recommendations:
            story.append(Paragraph("Recommendations", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(recommendations['text'].replace('\n', '<br/>'), styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        # Return PDF file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'task_mining_analysis_{dataset}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart/save', methods=['POST'])
def save_chart_api():
    """Save chart as HTML and Vega-Lite JSON"""
    try:
        data = request.get_json()
        dataset = data.get('dataset')
        chart_type = data.get('chart_type', 'summary')
        name = data.get('name', f'{dataset}_{chart_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        agent = None
        if dataset == 'salesforce' and salesforce_agent:
            agent = salesforce_agent
        elif dataset == 'amadeus' and amadeus_agent:
            agent = amadeus_agent
        else:
            return jsonify({"error": "Dataset not found"}), 404
        
        # Get chart
        chart_methods = {
            'summary': agent.summary,
            'bottlenecks': agent.top_bottlenecks,
            'team_performance': getattr(agent, 'team_performance', None),
            'app_usage': getattr(agent, 'app_usage', None),
            'time_analysis': getattr(agent, 'time_analysis', None),
            'process_analysis': getattr(agent, 'process_analysis', None),
            'user_efficiency': getattr(agent, 'user_efficiency', None)
        }
        
        method = chart_methods.get(chart_type)
        if not method:
            return jsonify({"error": "Chart type not supported"}), 400
        
        result = method()
        
        if 'chart' in result:
            paths = save_chart(result['chart'], name)
            return jsonify({
                "success": True,
                "paths": paths,
                "message": f"Chart saved as {paths['html']} and {paths['vegalite']}"
            })
        else:
            return jsonify({"error": "No chart found in result"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/<dataset>/info', methods=['GET'])
def get_dataset_info(dataset):
    """Get dataset information and column details"""
    try:
        agent = None
        if dataset == 'salesforce' and salesforce_agent:
            agent = salesforce_agent
            df = salesforce_agent.df
        elif dataset == 'amadeus' and amadeus_agent:
            agent = amadeus_agent
            df = amadeus_agent.df
        else:
            return jsonify({"error": "Dataset not found"}), 404
        
        # Get basic info
        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(5).to_dict('records')
        }
        
        return jsonify(info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load data on startup
    load_data()
    
    # Run the Flask app
    app.run(
        debug=config_class.FLASK_DEBUG, 
        host=config_class.FLASK_HOST, 
        port=config_class.FLASK_PORT
    )

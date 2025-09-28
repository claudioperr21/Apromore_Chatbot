#!/usr/bin/env python3
"""
Flask API Backend for Task Mining Chat System
============================================

This backend integrates with main.py to provide REST API endpoints for the React frontend.
"""

import os
import sys
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import altair as alt

# Import from main.py
from main import (
    load_csv, find_column, save_chart, fmt,
    SalesforceAgent, AmadeusAgent, CreativeDataChatBot, CreativeOrchestrator
)

# Configuration
BASE_DIR = r"C:\Users\claud\OneDrive\Desktop\ESADE\Masters in Busienss Analytics\Apromore In-company project\Apromore Chatbot\Data Sources"
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1.csv"
AMADEUS_FILE = "amadeus-demo-full-no-fields.csv"
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global system state
orchestrator = None
system_initialized = False

def initialize_system():
    """Initialize the task mining system"""
    global orchestrator, system_initialized
    
    try:
        # Load data
        salesforce_path = os.path.join(BASE_DIR, SALESFORCE_FILE)
        amadeus_path = os.path.join(BASE_DIR, AMADEUS_FILE)
        
        if not os.path.exists(salesforce_path) or not os.path.exists(amadeus_path):
            return False, "Data files not found"
        
        salesforce_df = load_csv(salesforce_path)
        amadeus_df = load_csv(amadeus_path)
        
        # Create agents
        agents = {
            "salesforce": SalesforceAgent(salesforce_df),
            "amadeus": AmadeusAgent(amadeus_df),
        }
        
        # Create orchestrator
        orchestrator = CreativeOrchestrator(agents)
        orchestrator.active = "salesforce"  # Default
        orchestrator.chatbot.current_dataset = "salesforce"
        
        system_initialized = True
        return True, "System initialized successfully"
        
    except Exception as e:
        return False, f"Error initializing system: {str(e)}"

# Initialize system on startup
init_success, init_message = initialize_system()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if system_initialized else "error",
        "message": init_message,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        "initialized": system_initialized,
        "active_dataset": orchestrator.active if orchestrator else None,
        "message": init_message
    })

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle chat messages"""
    if not system_initialized or not orchestrator:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        data = request.get_json()
        dataset = data.get('dataset', 'salesforce')
        message = data.get('message', '')
        
        if not message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Switch dataset if needed
        if dataset != orchestrator.active:
            orchestrator.active = dataset
            orchestrator.chatbot.current_dataset = dataset
        
        # Process the message
        result = orchestrator.route(message)
        response_text = result.get("text", "No response generated.")
        
        # Check if there's a chart
        chart_data = None
        chart_json = None
        
        if "chart" in result:
            # Generate chart
            chart_name = f"chat_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chart_paths = save_chart(result["chart"], chart_name)
            
            # Read chart HTML
            with open(chart_paths["html"], 'r', encoding='utf-8') as f:
                chart_data = f.read()
            
            # Read Vega-Lite JSON
            with open(chart_paths["vegalite"], 'r', encoding='utf-8') as f:
                chart_json = json.load(f)
        
        return jsonify({
            "message": response_text,
            "chart": chart_data,
            "chartJson": chart_json,
            "dataset": orchestrator.active,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500

@app.route('/api/analyze/<dataset>', methods=['POST'])
def analyze_dataset(dataset):
    """Analyze dataset with specific query"""
    if not system_initialized or not orchestrator:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if dataset not in orchestrator.agents:
            return jsonify({"error": f"Dataset {dataset} not found"}), 400
        
        # Switch to dataset
        orchestrator.active = dataset
        orchestrator.chatbot.current_dataset = dataset
        
        # Process query
        result = orchestrator.route(query)
        response_text = result.get("text", "No analysis available")
        
        # Generate chart if available
        chart_data = None
        chart_json = None
        
        if "chart" in result:
            chart_name = f"analysis_{dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chart_paths = save_chart(result["chart"], chart_name)
            
            with open(chart_paths["html"], 'r', encoding='utf-8') as f:
                chart_data = f.read()
            
            with open(chart_paths["vegalite"], 'r', encoding='utf-8') as f:
                chart_json = json.load(f)
        
        return jsonify({
            "text": response_text,
            "chart": chart_data,
            "chartJson": chart_json,
            "dataset": dataset,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Error analyzing dataset: {str(e)}"}), 500

@app.route('/api/chart/<dataset>/<chart_type>', methods=['GET'])
def get_chart(dataset, chart_type):
    """Get specific chart type for dataset"""
    if not system_initialized or not orchestrator:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        if dataset not in orchestrator.agents:
            return jsonify({"error": f"Dataset {dataset} not found"}), 400
        
        agent = orchestrator.agents[dataset]
        
        # Get chart based on type
        if chart_type == 'summary':
            result = agent.summary()
        elif chart_type == 'bottlenecks':
            result = agent.top_bottlenecks()
        elif chart_type == 'team_performance' and dataset == 'salesforce':
            result = agent.team_performance()
        elif chart_type == 'app_usage' and dataset == 'salesforce':
            result = agent.app_usage()
        else:
            return jsonify({"error": f"Chart type {chart_type} not available for {dataset}"}), 400
        
        if "chart" not in result:
            return jsonify({"error": "No chart available for this analysis"}), 400
        
        # Generate chart
        chart_name = f"{chart_type}_{dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        chart_paths = save_chart(result["chart"], chart_name)
        
        # Return chart data
        with open(chart_paths["html"], 'r', encoding='utf-8') as f:
            chart_html = f.read()
        
        with open(chart_paths["vegalite"], 'r', encoding='utf-8') as f:
            chart_json = json.load(f)
        
        return jsonify({
            "html": chart_html,
            "vegalite": chart_json,
            "text": result.get("text", ""),
            "dataset": dataset,
            "chartType": chart_type
        })
        
    except Exception as e:
        return jsonify({"error": f"Error generating chart: {str(e)}"}), 500

@app.route('/api/switch', methods=['POST'])
def switch_dataset():
    """Switch active dataset"""
    if not system_initialized or not orchestrator:
        return jsonify({"error": "System not initialized"}), 500
    
    try:
        data = request.get_json()
        dataset = data.get('dataset', 'salesforce')
        
        if dataset not in orchestrator.agents:
            return jsonify({"error": f"Dataset {dataset} not found"}), 400
        
        orchestrator.active = dataset
        orchestrator.chatbot.current_dataset = dataset
        
        return jsonify({
            "message": f"Switched to {dataset} dataset",
            "active_dataset": dataset,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"Error switching dataset: {str(e)}"}), 500

@app.route('/api/export/chat', methods=['POST'])
def export_chat_history():
    """Export chat history"""
    try:
        data = request.get_json()
        chat_history = data.get('chat_history', [])
        
        # Create export data
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "dataset": orchestrator.active if orchestrator else "unknown",
            "chat_history": chat_history,
            "system_info": {
                "version": "1.0",
                "features": ["AI Chat", "Vega-Lite Charts", "Multi-Dataset Support"]
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"chat_history_{orchestrator.active if orchestrator else 'unknown'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
        
    except Exception as e:
        return jsonify({"error": f"Error exporting chat: {str(e)}"}), 500

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Export analysis as PDF (placeholder)"""
    return jsonify({
        "message": "PDF export feature coming soon",
        "status": "not_implemented"
    }), 501

if __name__ == '__main__':
    print("🚀 Starting Task Mining Chat API Server...")
    print(f"System Status: {'✅ Ready' if system_initialized else '❌ Error'}")
    print(f"Message: {init_message}")
    print("Frontend will be available at: http://localhost:3000")
    print("API will be available at: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

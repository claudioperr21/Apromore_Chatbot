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

from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import pandas as pd
import altair as alt
import time
import traceback

# Import from main.py
from main import (
    load_csv, find_column, save_chart, fmt,
    SalesforceAgent, AmadeusAgent, CreativeDataChatBot, CreativeOrchestrator
)

# Configuration
# Use relative path from the script location
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(SCRIPT_DIR, "Data Sources")
SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
AMADEUS_FILE = "amadeus-demo-full-no-fields.csv"
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# Logs directory for telemetry
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Enable telemetry
ENABLE_TRACING = True

# Import instrumentation modules (optional)
try:
    from backend.kpi_rollup import rollup_today
    INSTRUMENTATION_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] KPI rollup not available: {e}")
    INSTRUMENTATION_AVAILABLE = False

# Import comprehensive analytics (optional)
try:
    from backend.comprehensive_analytics import ComprehensiveAnalyticsReader
    COMPREHENSIVE_ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] Comprehensive analytics not available: {e}")
    COMPREHENSIVE_ANALYTICS_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global system state
orchestrator = None
system_initialized = False
analytics_reader = None

def initialize_system():
    """Initialize the task mining system"""
    global orchestrator, system_initialized, analytics_reader
    
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
        
        # Initialize comprehensive analytics reader
        if COMPREHENSIVE_ANALYTICS_AVAILABLE:
            try:
                analytics_reader = ComprehensiveAnalyticsReader(SCRIPT_DIR)
                print("[INFO] Comprehensive analytics initialized")
            except Exception as e:
                print(f"[WARNING] Could not initialize comprehensive analytics: {e}")
                analytics_reader = None
        
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

# -------------------------------
# Telemetry and Instrumentation
# -------------------------------

def write_trace_log(trace_record: dict):
    """Write trace record to JSONL file"""
    if not ENABLE_TRACING:
        return
    
    try:
        # Create traces directory
        traces_dir = Path(LOG_DIR)
        traces_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily trace file
        today_str = datetime.now().strftime("%Y%m%d")
        trace_file = traces_dir / f"traces-{today_str}.jsonl"
        
        # Append trace record as JSONL
        with open(trace_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trace_record, default=str) + '\n')
            f.flush()
            os.fsync(f.fileno())  # Ensure write
    
    except Exception as e:
        # Fail soft - don't crash requests
        print(f"[WARNING] Failed to write trace log: {e}")


@app.before_request
def before_request_telemetry():
    """Start request timing and capture metadata"""
    g.start_time = time.time()
    g.request_metadata = {
        "endpoint": request.path,
        "method": request.method,
        "dataset": None,
        "query": None,
        "request_bytes": len(request.get_data()) if request.get_data() else 0
    }


@app.after_request
def after_request_telemetry(response):
    """End request timing and write telemetry trace"""
    if not ENABLE_TRACING or not hasattr(g, 'start_time'):
        return response
    
    try:
        # Calculate latency
        latency_ms_total = (time.time() - g.start_time) * 1000
        
        # Build trace record
        trace_record = {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "endpoint": g.request_metadata.get("endpoint"),
            "method": g.request_metadata.get("method"),
            "dataset": g.request_metadata.get("dataset", "unknown"),
            "query": g.request_metadata.get("query"),
            "request_bytes": g.request_metadata.get("request_bytes", 0),
            "response_bytes": len(response.get_data()) if response.get_data() else 0,
            "latency_ms_total": round(latency_ms_total, 2),
            "status_code": response.status_code,
            "error": g.request_metadata.get("error"),
            "session_id": request.headers.get("X-Session-ID", "anonymous"),
            "user_id": request.headers.get("X-User-ID"),
        }
        
        # Write trace
        write_trace_log(trace_record)
    
    except Exception as e:
        # Fail soft
        print(f"[WARNING] Telemetry error: {e}")
    
    return response


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
        
        # Update telemetry metadata
        if hasattr(g, 'request_metadata'):
            g.request_metadata['dataset'] = dataset
            g.request_metadata['query'] = message[:100]  # First 100 chars
        
        if not message.strip():
            if hasattr(g, 'request_metadata'):
                g.request_metadata['error'] = "Empty message"
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

@app.route('/api/kpis/today', methods=['GET'])
def get_kpis_today():
    """
    Get KPI rollup for today
    
    Returns aggregated KPIs without exposing raw prompts or PII
    """
    try:
        if not INSTRUMENTATION_AVAILABLE:
            return jsonify({
                "error": "KPI instrumentation not available",
                "trace_count": 0
            }), 503
        
        # Compute today's KPI rollup
        traces_dir = Path(LOG_DIR)
        kpis = rollup_today(traces_dir)
        
        # Ensure no PII is exposed
        if "traces" in kpis:
            del kpis["traces"]
        
        return jsonify(kpis)
    
    except Exception as e:
        print(f"[ERROR] get_kpis_today: {e}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Failed to compute KPIs",
            "details": str(e)
        }), 500

@app.route('/api/analytics/comprehensive', methods=['POST'])
def get_comprehensive_analytics():
    """
    Get comprehensive analytics insights (text-based, no charts)
    
    Supports queries about:
    - Case aging
    - Flow efficiency
    - Team handoffs
    - User interactions
    - Comprehensive summaries
    """
    try:
        if not COMPREHENSIVE_ANALYTICS_AVAILABLE or not analytics_reader:
            return jsonify({
                "error": "Comprehensive analytics not available",
                "message": "Aggregate data files may be missing from mnt/data/aggregates/"
            }), 503
        
        data = request.get_json()
        query = data.get('query', '')
        dataset = data.get('dataset', 'salesforce')
        
        if not query:
            return jsonify({
                "error": "Query parameter is required",
                "supported_queries": [
                    "case aging analysis",
                    "flow efficiency report",
                    "team handoff analysis",
                    "interaction patterns",
                    "comprehensive summary"
                ]
            }), 400
        
        if dataset not in ['salesforce', 'amadeus']:
            return jsonify({
                "error": f"Invalid dataset: {dataset}",
                "supported_datasets": ["salesforce", "amadeus"]
            }), 400
        
        # Update telemetry
        if hasattr(g, 'request_metadata'):
            g.request_metadata['dataset'] = dataset
            g.request_metadata['query'] = query[:100]
        
        # Query analytics
        response = analytics_reader.query_analytics(query, dataset)
        
        return jsonify({
            "response": response,
            "dataset": dataset,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "type": "comprehensive_analytics"
        })
    
    except Exception as e:
        if hasattr(g, 'request_metadata'):
            g.request_metadata['error'] = str(e)
        print(f"[ERROR] get_comprehensive_analytics: {e}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Failed to get analytics",
            "details": str(e)
        }), 500

@app.route('/api/analytics/available', methods=['GET'])
def check_analytics_availability():
    """
    Check if comprehensive analytics are available
    """
    available_analyses = []
    
    if COMPREHENSIVE_ANALYTICS_AVAILABLE and analytics_reader:
        # Check which datasets have aggregate data
        if analytics_reader.has_comprehensive_data:
            available_analyses.append({
                "type": "case_aging",
                "description": "Case aging distribution analysis",
                "keywords": ["aging", "age", "old", "stale"]
            })
            available_analyses.append({
                "type": "flow_efficiency",
                "description": "Flow efficiency (touch vs wait time)",
                "keywords": ["flow", "efficiency", "touch", "wait"]
            })
            available_analyses.append({
                "type": "handoffs",
                "description": "Team handoff analysis",
                "keywords": ["handoff", "handoffs", "transition", "transfer"]
            })
            available_analyses.append({
                "type": "interactions",
                "description": "User interaction patterns",
                "keywords": ["interaction", "clicks", "keys", "effort"]
            })
            available_analyses.append({
                "type": "comprehensive",
                "description": "Complete analytics summary",
                "keywords": ["comprehensive", "complete", "all", "summary"]
            })
    
    return jsonify({
        "comprehensive_analytics_available": COMPREHENSIVE_ANALYTICS_AVAILABLE and analytics_reader is not None,
        "has_aggregate_data": analytics_reader.has_comprehensive_data if analytics_reader else False,
        "available_analyses": available_analyses,
        "supported_datasets": ["salesforce", "amadeus"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analytics/<analysis_type>/<dataset>', methods=['GET'])
def get_specific_analytics(analysis_type, dataset):
    """
    Get specific analytics type for a dataset
    
    Supported analysis types:
    - aging: Case aging distribution
    - flow: Flow efficiency
    - handoffs: Team handoff analysis  
    - interactions: User interaction patterns
    - summary: Comprehensive summary
    """
    try:
        if not COMPREHENSIVE_ANALYTICS_AVAILABLE or not analytics_reader:
            return jsonify({
                "error": "Comprehensive analytics not available"
            }), 503
        
        if dataset not in ['salesforce', 'amadeus']:
            return jsonify({
                "error": f"Invalid dataset: {dataset}"
            }), 400
        
        # Update telemetry
        if hasattr(g, 'request_metadata'):
            g.request_metadata['dataset'] = dataset
        
        # Map analysis type to method
        if analysis_type == 'aging':
            response = analytics_reader.get_case_aging_insights(dataset)
        elif analysis_type == 'flow':
            response = analytics_reader.get_flow_efficiency_insights(dataset)
        elif analysis_type == 'handoffs':
            response = analytics_reader.get_handoff_insights(dataset)
        elif analysis_type == 'interactions':
            level = request.args.get('level', 'team')
            response = analytics_reader.get_interaction_insights(dataset, level)
        elif analysis_type == 'summary':
            response = analytics_reader.get_comprehensive_summary(dataset)
        else:
            return jsonify({
                "error": f"Invalid analysis type: {analysis_type}",
                "supported_types": ["aging", "flow", "handoffs", "interactions", "summary"]
            }), 400
        
        return jsonify({
            "response": response,
            "dataset": dataset,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        if hasattr(g, 'request_metadata'):
            g.request_metadata['error'] = str(e)
        print(f"[ERROR] get_specific_analytics: {e}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Failed to get analytics",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Task Mining Chat API Server...")
    print(f"System Status: {'✅ Ready' if system_initialized else '❌ Error'}")
    print(f"Message: {init_message}")
    print(f"Telemetry: {'✅ Enabled' if ENABLE_TRACING else '❌ Disabled'}")
    print(f"Comprehensive Analytics: {'✅ Available' if (COMPREHENSIVE_ANALYTICS_AVAILABLE and analytics_reader) else '❌ Not Available'}")
    print(f"Log Directory: {LOG_DIR}")
    print("\n📊 Available Endpoints:")
    print("  • Frontend: http://localhost:3000")
    print("  • API Base: http://localhost:5000")
    print("  • Health: http://localhost:5000/api/health")
    print("  • Chat: POST http://localhost:5000/api/chat")
    print("  • KPIs: http://localhost:5000/api/kpis/today")
    if COMPREHENSIVE_ANALYTICS_AVAILABLE and analytics_reader:
        print("  • Analytics Check: http://localhost:5000/api/analytics/available")
        print("  • Comprehensive: POST http://localhost:5000/api/analytics/comprehensive")
        print("  • Specific: GET http://localhost:5000/api/analytics/{type}/{dataset}")
    print("")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

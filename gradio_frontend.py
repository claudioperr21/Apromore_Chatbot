#!/usr/bin/env python3
"""
Gradio Frontend for Task Mining Multi-Agent System
==================================================

Web interface for the task mining system with chat, charts, and export capabilities.
"""

import gradio as gr
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
import pandas as pd
import altair as alt

# Import the main system components
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

# Global variables to store system state
orchestrator = None
chat_history = []

def initialize_system():
    """Initialize the task mining system"""
    global orchestrator
    
    try:
        # Load data
        salesforce_path = os.path.join(BASE_DIR, SALESFORCE_FILE)
        amadeus_path = os.path.join(BASE_DIR, AMADEUS_FILE)
        
        if not os.path.exists(salesforce_path) or not os.path.exists(amadeus_path):
            return False, "Data files not found. Please ensure CSV files are in the Data Sources folder."
        
        salesforce_df = load_csv(salesforce_path)
        amadeus_df = load_csv(amadeus_path)
        
        # Create agents
        agents = {
            "salesforce": SalesforceAgent(salesforce_df),
            "amadeus": AmadeusAgent(amadeus_df),
        }
        
        # Create orchestrator
        orchestrator = CreativeOrchestrator(agents)
        orchestrator.active = "salesforce"  # Default to salesforce
        orchestrator.chatbot.current_dataset = "salesforce"
        
        return True, "System initialized successfully!"
        
    except Exception as e:
        return False, f"Error initializing system: {str(e)}"

def handle_chat(message, history):
    """Handle chat messages"""
    global orchestrator, chat_history
    
    if orchestrator is None:
        return history, "System not initialized. Please refresh the page.", None, None
    
    if not message.strip():
        return history, "Please enter a message.", None, None
    
    try:
        # Add user message to history
        history.append([message, None])
        
        # Process the message
        result = orchestrator.route(message)
        response = result.get("text", "No response generated.")
        
        # Add AI response to history
        history[-1][1] = response
        
        # Check if there's a chart to display
        chart_path = None
        chart_json = None
        
        if "chart" in result:
            # Generate a temporary chart file
            chart_name = f"gradio_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chart_paths = save_chart(result["chart"], chart_name)
            chart_path = chart_paths["html"]
            
            # Also get the Vega-Lite JSON
            with open(chart_paths["vegalite"], 'r', encoding='utf-8') as f:
                chart_json = json.load(f)
        
        return history, response, chart_path, chart_json
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        history.append([message, error_msg])
        return history, error_msg, None, None

def switch_dataset(dataset):
    """Switch between datasets"""
    global orchestrator
    
    if orchestrator is None:
        return "System not initialized", None
    
    try:
        if dataset == "Salesforce":
            orchestrator.active = "salesforce"
            orchestrator.chatbot.current_dataset = "salesforce"
            return f"Switched to Salesforce dataset", "salesforce"
        else:
            orchestrator.active = "amadeus"
            orchestrator.chatbot.current_dataset = "amadeus"
            return f"Switched to Amadeus dataset", "amadeus"
    except Exception as e:
        return f"Error switching dataset: {str(e)}", None

def export_chat_history(history):
    """Export chat history to JSON"""
    if not history:
        return None, "No chat history to export"
    
    try:
        # Create export data
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "dataset": orchestrator.active if orchestrator else "unknown",
            "chat_history": history,
            "system_info": {
                "version": "1.0",
                "features": ["AI Chat", "Vega-Lite Charts", "Multi-Dataset Support"]
            }
        }
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        return temp_path, "Chat history exported successfully!"
        
    except Exception as e:
        return None, f"Error exporting chat: {str(e)}"

def get_dataset_summary(dataset):
    """Get dataset summary"""
    global orchestrator
    
    if orchestrator is None:
        return "System not initialized"
    
    try:
        if dataset == "Salesforce":
            result = orchestrator.agents["salesforce"].summary()
        else:
            result = orchestrator.agents["amadeus"].summary()
        
        return result.get("text", "No summary available")
        
    except Exception as e:
        return f"Error getting summary: {str(e)}"

def get_bottlenecks(dataset):
    """Get bottlenecks analysis"""
    global orchestrator
    
    if orchestrator is None:
        return "System not initialized", None
    
    try:
        if dataset == "Salesforce":
            result = orchestrator.agents["salesforce"].top_bottlenecks()
        else:
            result = orchestrator.agents["amadeus"].top_bottlenecks()
        
        text = result.get("text", "No bottlenecks analysis available")
        
        # Generate chart if available
        chart_path = None
        if "chart" in result:
            chart_name = f"bottlenecks_{dataset.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chart_paths = save_chart(result["chart"], chart_name)
            chart_path = chart_paths["html"]
        
        return text, chart_path
        
    except Exception as e:
        return f"Error getting bottlenecks: {str(e)}", None

def get_team_performance(dataset):
    """Get team performance analysis"""
    global orchestrator
    
    if orchestrator is None:
        return "System not initialized", None
    
    try:
        if dataset == "Salesforce":
            result = orchestrator.agents["salesforce"].team_performance()
        else:
            return "Team performance analysis not available for Amadeus dataset", None
        
        text = result.get("text", "No team performance analysis available")
        
        # Generate chart if available
        chart_path = None
        if "chart" in result:
            chart_name = f"team_performance_{dataset.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            chart_paths = save_chart(result["chart"], chart_name)
            chart_path = chart_paths["html"]
        
        return text, chart_path
        
    except Exception as e:
        return f"Error getting team performance: {str(e)}", None

def get_recommendations(dataset):
    """Get managerial recommendations"""
    global orchestrator
    
    if orchestrator is None:
        return "System not initialized"
    
    try:
        if dataset == "Salesforce":
            result = orchestrator.agents["salesforce"].recommendations()
        else:
            result = orchestrator.agents["amadeus"].recommendations()
        
        return result.get("text", "No recommendations available")
        
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"

# Initialize system
init_success, init_message = initialize_system()

# Create Gradio interface
with gr.Blocks(title="Task Mining AI Chat System", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🎯 Task Mining Multi-Agent System with AI Chat
    
    **Features:**
    - 🤖 Creative AI chat with natural language processing
    - 📊 Interactive Vega-Lite charts and visualizations
    - 🔄 Multi-dataset support (Salesforce & Amadeus)
    - ✅ Smart task filtering (excludes completed tasks from bottlenecks)
    - 📈 Managerial recommendations and insights
    - 💾 Export capabilities for charts and chat history
    
    **Status:** """ + ("✅ System Ready" if init_success else f"❌ {init_message}")
    )
    
    with gr.Tab("💬 AI Chat Interface"):
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="AI Chat",
                    height=400,
                    show_label=True,
                    container=True,
                    bubble_full_width=False
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask me anything about your data... (e.g., 'who is the most active user?', 'what are some bottlenecks?')",
                        label="Message",
                        lines=2,
                        scale=4
                    )
                    send_btn = gr.Button("Send", scale=1, variant="primary")
                
                # Chart display
                chart_display = gr.HTML(label="Chart Visualization")
                
            with gr.Column(scale=1):
                # Dataset selector
                dataset_selector = gr.Radio(
                    choices=["Salesforce", "Amadeus"],
                    value="Salesforce",
                    label="Active Dataset",
                    info="Switch between datasets"
                )
                
                # Quick actions
                gr.Markdown("### 🚀 Quick Actions")
                summary_btn = gr.Button("📊 Summary", variant="secondary")
                bottlenecks_btn = gr.Button("🚧 Bottlenecks", variant="secondary")
                team_btn = gr.Button("👥 Team Performance", variant="secondary")
                recommendations_btn = gr.Button("💡 Recommendations", variant="secondary")
                
                # Export options
                gr.Markdown("### 📤 Export Options")
                export_chat_btn = gr.Button("💾 Export Chat History", variant="secondary")
                export_status = gr.Textbox(label="Export Status", interactive=False)
        
        # Event handlers for chat
        def user(user_message, history):
            return "", history + [[user_message, None]]
        
        def bot(history):
            user_message = history[-1][0]
            history, response, chart_path, chart_json = handle_chat(user_message, history)
            return history, response, chart_path
        
        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, [chatbot, msg, chart_display]
        )
        send_btn.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, [chatbot, msg, chart_display]
        )
        
        # Dataset switching
        def switch_and_update(dataset):
            status, active = switch_dataset(dataset)
            return status, active
        
        dataset_selector.change(switch_and_update, dataset_selector, [gr.Textbox(visible=False), gr.Textbox(visible=False)])
        
        # Quick action handlers
        def handle_summary(dataset):
            return get_dataset_summary(dataset)
        
        def handle_bottlenecks(dataset):
            text, chart_path = get_bottlenecks(dataset)
            if chart_path:
                with open(chart_path, 'r', encoding='utf-8') as f:
                    chart_html = f.read()
                return text, chart_html
            return text, None
        
        def handle_team_performance(dataset):
            text, chart_path = get_team_performance(dataset)
            if chart_path:
                with open(chart_path, 'r', encoding='utf-8') as f:
                    chart_html = f.read()
                return text, chart_html
            return text, None
        
        def handle_recommendations(dataset):
            return get_recommendations(dataset)
        
        # Connect quick action buttons
        summary_btn.click(
            handle_summary, 
            dataset_selector, 
            gr.Textbox(label="Summary Results", lines=10)
        )
        
        bottlenecks_btn.click(
            handle_bottlenecks,
            dataset_selector,
            [gr.Textbox(label="Bottlenecks Analysis", lines=10), chart_display]
        )
        
        team_btn.click(
            handle_team_performance,
            dataset_selector,
            [gr.Textbox(label="Team Performance", lines=10), chart_display]
        )
        
        recommendations_btn.click(
            handle_recommendations,
            dataset_selector,
            gr.Textbox(label="Recommendations", lines=10)
        )
        
        # Export chat history
        def export_chat():
            if chatbot.value:
                file_path, status = export_chat_history(chatbot.value)
                return file_path, status
            return None, "No chat history to export"
        
        export_chat_btn.click(
            export_chat,
            outputs=[gr.File(label="Download Chat History"), export_status]
        )
    
    with gr.Tab("📊 Analysis Dashboard"):
        gr.Markdown("### Dataset Analysis Dashboard")
        
        with gr.Row():
            with gr.Column():
                analysis_dataset = gr.Radio(
                    choices=["Salesforce", "Amadeus"],
                    value="Salesforce",
                    label="Select Dataset for Analysis"
                )
                
                analysis_btn = gr.Button("🔍 Run Analysis", variant="primary")
            
            with gr.Column():
                analysis_results = gr.Textbox(
                    label="Analysis Results",
                    lines=15,
                    max_lines=20
                )
        
        def run_comprehensive_analysis(dataset):
            """Run comprehensive analysis for the selected dataset"""
            global orchestrator
            
            if orchestrator is None:
                return "System not initialized"
            
            try:
                results = []
                results.append(f"=== {dataset} Dataset Analysis ===\n")
                
                # Summary
                if dataset == "Salesforce":
                    summary_result = orchestrator.agents["salesforce"].summary()
                else:
                    summary_result = orchestrator.agents["amadeus"].summary()
                
                results.append("📊 SUMMARY:")
                results.append(summary_result.get("text", "No summary available"))
                results.append("\n" + "="*50 + "\n")
                
                # Bottlenecks
                if dataset == "Salesforce":
                    bottlenecks_result = orchestrator.agents["salesforce"].top_bottlenecks()
                else:
                    bottlenecks_result = orchestrator.agents["amadeus"].top_bottlenecks()
                
                results.append("🚧 BOTTLENECKS ANALYSIS:")
                results.append(bottlenecks_result.get("text", "No bottlenecks analysis available"))
                results.append("\n" + "="*50 + "\n")
                
                # Team Performance (Salesforce only)
                if dataset == "Salesforce":
                    team_result = orchestrator.agents["salesforce"].team_performance()
                    results.append("👥 TEAM PERFORMANCE:")
                    results.append(team_result.get("text", "No team performance analysis available"))
                    results.append("\n" + "="*50 + "\n")
                
                # Recommendations
                if dataset == "Salesforce":
                    rec_result = orchestrator.agents["salesforce"].recommendations()
                else:
                    rec_result = orchestrator.agents["amadeus"].recommendations()
                
                results.append("💡 RECOMMENDATIONS:")
                results.append(rec_result.get("text", "No recommendations available"))
                
                return "\n".join(results)
                
            except Exception as e:
                return f"Error running analysis: {str(e)}"
        
        analysis_btn.click(
            run_comprehensive_analysis,
            analysis_dataset,
            analysis_results
        )
    
    with gr.Tab("📈 Chart Gallery"):
        gr.Markdown("### Generated Charts and Visualizations")
        
        with gr.Row():
            with gr.Column():
                chart_dataset = gr.Radio(
                    choices=["Salesforce", "Amadeus"],
                    value="Salesforce",
                    label="Dataset for Charts"
                )
                
                chart_type = gr.Radio(
                    choices=["Summary", "Bottlenecks", "Team Performance", "App Usage"],
                    value="Summary",
                    label="Chart Type"
                )
                
                generate_chart_btn = gr.Button("📊 Generate Chart", variant="primary")
            
            with gr.Column():
                chart_output = gr.HTML(label="Generated Chart")
                chart_download = gr.File(label="Download Chart")
        
        def generate_chart(dataset, chart_type):
            """Generate and display a chart"""
            global orchestrator
            
            if orchestrator is None:
                return "System not initialized", None
            
            try:
                if dataset == "Salesforce":
                    agent = orchestrator.agents["salesforce"]
                else:
                    agent = orchestrator.agents["amadeus"]
                
                # Get the appropriate chart
                if chart_type == "Summary":
                    result = agent.summary()
                elif chart_type == "Bottlenecks":
                    result = agent.top_bottlenecks()
                elif chart_type == "Team Performance" and dataset == "Salesforce":
                    result = agent.team_performance()
                elif chart_type == "App Usage" and dataset == "Salesforce":
                    result = agent.app_usage()
                else:
                    return f"Chart type '{chart_type}' not available for {dataset} dataset", None
                
                if "chart" not in result:
                    return "No chart available for this analysis", None
                
                # Generate chart
                chart_name = f"{chart_type.lower().replace(' ', '_')}_{dataset.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                chart_paths = save_chart(result["chart"], chart_name)
                
                # Read and return chart HTML
                with open(chart_paths["html"], 'r', encoding='utf-8') as f:
                    chart_html = f.read()
                
                return chart_html, chart_paths["html"]
                
            except Exception as e:
                return f"Error generating chart: {str(e)}", None
        
        generate_chart_btn.click(
            generate_chart,
            [chart_dataset, chart_type],
            [chart_output, chart_download]
        )
    
    with gr.Tab("⚙️ System Info"):
        gr.Markdown("### System Information and Status")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown(f"""
                **System Status:** {'✅ Ready' if init_success else '❌ Error'}
                
                **Initialization Message:** {init_message}
                
                **Available Datasets:**
                - Salesforce: {SALESFORCE_FILE}
                - Amadeus: {AMADEUS_FILE}
                
                **Features:**
                - 🤖 AI Chat with OpenAI integration
                - 📊 Vega-Lite chart generation
                - 🔄 Multi-dataset support
                - ✅ Smart task filtering
                - 💾 Export capabilities
                - 📈 Managerial insights
                
                **Chart Output Directory:** {CHARTS_DIR}
                """)
            
            with gr.Column():
                refresh_btn = gr.Button("🔄 Refresh System", variant="secondary")
                system_status = gr.Textbox(
                    label="System Status",
                    value=init_message,
                    interactive=False
                )
        
        def refresh_system():
            """Refresh the system"""
            success, message = initialize_system()
            return f"System refresh: {message}"
        
        refresh_btn.click(refresh_system, outputs=system_status)

# Launch the interface
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )

#!/usr/bin/env python3
"""
Interactive Chat Interface for Task Mining Data Analysis
This allows users to ask natural language questions about their data.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import openai
from datetime import datetime

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

try:
    from task_mining_multi_agent import (
        SalesforceAgent, AmadeusAgent, load_csv, 
        find_column, save_chart, BASE_DIR
    )
    print("[OK] Task mining modules loaded")
except ImportError as e:
    print(f"[ERROR] Failed to import modules: {e}")
    sys.exit(1)

class DataChatBot:
    def __init__(self):
        """Initialize the chat bot with data and OpenAI"""
        self.salesforce_agent = None
        self.amadeus_agent = None
        self.current_dataset = None
        self.openai_client = None
        
        # Initialize OpenAI
        self.setup_openai()
        
        # Load data
        self.load_data()
    
    def setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('SECRET_KEY')
        if not api_key or not api_key.startswith('sk-'):
            print("[WARNING] OpenAI API key not found or invalid")
            print("Chat features will be limited. Please set SECRET_KEY in .env file")
            return
        
        try:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("[OK] OpenAI client initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize OpenAI: {e}")
    
    def load_data(self):
        """Load the datasets"""
        print("[INFO] Loading datasets...")
        
        # Load Salesforce data
        salesforce_path = os.path.join(BASE_DIR, "SalesforceOffice_synthetic_varied_100users_V1.csv")
        if os.path.exists(salesforce_path):
            try:
                salesforce_df = load_csv(salesforce_path)
                self.salesforce_agent = SalesforceAgent(salesforce_df)
                print(f"[OK] Salesforce data loaded: {len(salesforce_df)} rows")
            except Exception as e:
                print(f"[ERROR] Failed to load Salesforce data: {e}")
        
        # Load Amadeus data
        amadeus_path = os.path.join(BASE_DIR, "amadeus-demo-full-no-fields.csv")
        if os.path.exists(amadeus_path):
            try:
                amadeus_df = load_csv(amadeus_path)
                self.amadeus_agent = AmadeusAgent(amadeus_df)
                print(f"[OK] Amadeus data loaded: {len(amadeus_df)} rows")
            except Exception as e:
                print(f"[ERROR] Failed to load Amadeus data: {e}")
    
    def get_dataset_info(self, dataset_name):
        """Get basic information about a dataset"""
        if dataset_name == "salesforce" and self.salesforce_agent:
            agent = self.salesforce_agent
            df = agent.df
        elif dataset_name == "amadeus" and self.amadeus_agent:
            agent = self.amadeus_agent
            df = agent.df
        else:
            return None
        
        info = {
            "rows": len(df),
            "columns": list(df.columns),
            "user_col": agent.user_col,
            "duration_col": agent.duration_col,
            "activity_col": agent.activity_col,
            "team_col": getattr(agent, 'team_col', None),
            "app_col": getattr(agent, 'app_col', None)
        }
        
        return info
    
    def analyze_data_for_question(self, question):
        """Analyze data to answer a specific question"""
        results = {}
        
        # Analyze both datasets if available
        for dataset_name, agent in [("salesforce", self.salesforce_agent), ("amadeus", self.amadeus_agent)]:
            if agent is None:
                continue
            
            df = agent.df
            dataset_info = self.get_dataset_info(dataset_name)
            
            # Basic statistics
            stats = {
                "total_rows": len(df),
                "unique_users": df[agent.user_col].nunique() if agent.user_col else 0,
                "unique_activities": df[agent.activity_col].nunique() if agent.activity_col else 0,
                "avg_duration": df[agent.duration_col].mean() if agent.duration_col else 0
            }
            
            # Most active user
            if agent.user_col:
                user_activity = df[agent.user_col].value_counts()
                stats["most_active_user"] = user_activity.index[0] if len(user_activity) > 0 else None
                stats["most_active_count"] = user_activity.iloc[0] if len(user_activity) > 0 else 0
            
            # Longest activities
            if agent.activity_col and agent.duration_col:
                activity_duration = df.groupby(agent.activity_col)[agent.duration_col].mean().sort_values(ascending=False)
                stats["longest_activities"] = activity_duration.head(5).to_dict()
            
            # Team performance (if available)
            if hasattr(agent, 'team_col') and agent.team_col:
                team_performance = df.groupby(agent.team_col)[agent.duration_col].mean().sort_values(ascending=False)
                stats["team_performance"] = team_performance.to_dict()
            
            # App usage (if available)
            if hasattr(agent, 'app_col') and agent.app_col:
                app_usage = df[agent.app_col].value_counts()
                stats["app_usage"] = app_usage.head(10).to_dict()
            
            results[dataset_name] = {
                "info": dataset_info,
                "stats": stats
            }
        
        return results
    
    def get_ai_response(self, question, data_analysis):
        """Get AI response based on question and data analysis"""
        if not self.openai_client:
            return "AI features not available. Please check your OpenAI API key."
        
        # Prepare context for AI
        context = f"""
        You are a task mining data analyst. Here's the data analysis for the question: "{question}"
        
        Data Analysis Results:
        {data_analysis}
        
        Please provide a clear, actionable answer to the user's question based on this data.
        Include specific numbers, insights, and recommendations where relevant.
        Be conversational and helpful.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert task mining analyst. Provide clear, data-driven insights."},
                    {"role": "user", "content": context}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting AI response: {e}"
    
    def answer_question(self, question):
        """Answer a user question about the data"""
        print(f"\n[ANALYZING] Question: {question}")
        
        # Analyze data
        data_analysis = self.analyze_data_for_question(question)
        
        # Get AI response
        ai_response = self.get_ai_response(question, data_analysis)
        
        return ai_response
    
    def show_available_datasets(self):
        """Show available datasets"""
        print("\nAvailable datasets:")
        if self.salesforce_agent:
            print(f"  - salesforce: {len(self.salesforce_agent.df)} rows")
        if self.amadeus_agent:
            print(f"  - amadeus: {len(self.amadeus_agent.df)} rows")
    
    def show_sample_questions(self):
        """Show sample questions users can ask"""
        print("\nSample questions you can ask:")
        print("  - Who is the most active user?")
        print("  - What are the longest-running activities?")
        print("  - Which team performs best?")
        print("  - What applications are used most?")
        print("  - What are the main bottlenecks?")
        print("  - How many unique users do we have?")
        print("  - What's the average task duration?")
        print("  - Which activities take the longest time?")
        print("  - Compare performance between teams")
        print("  - What are the top 5 most common activities?")
    
    def run_chat(self):
        """Run the interactive chat"""
        print("\n" + "="*60)
        print("🤖 Task Mining Data Chat Assistant")
        print("="*60)
        print("Ask me anything about your task mining data!")
        print("Type 'help' for sample questions, 'datasets' for available data, or 'exit' to quit")
        
        self.show_available_datasets()
        self.show_sample_questions()
        
        while True:
            try:
                question = input("\n💬 Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Goodbye! Thanks for using the Task Mining Chat Assistant!")
                    break
                
                if question.lower() == 'help':
                    self.show_sample_questions()
                    continue
                
                if question.lower() == 'datasets':
                    self.show_available_datasets()
                    continue
                
                if not question:
                    continue
                
                # Answer the question
                answer = self.answer_question(question)
                print(f"\n🤖 Assistant: {answer}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using the Task Mining Chat Assistant!")
                break
            except Exception as e:
                print(f"\n[ERROR] An error occurred: {e}")

def main():
    """Main function"""
    print("Task Mining Data Chat Assistant")
    print("="*40)
    
    # Check if data files exist
    data_dir = Path("Data Sources")
    if not data_dir.exists():
        print("[ERROR] Data Sources directory not found")
        return False
    
    # Initialize chat bot
    try:
        chatbot = DataChatBot()
        chatbot.run_chat()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize chat bot: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

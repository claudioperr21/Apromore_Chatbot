#!/usr/bin/env python3
"""
Task Mining Multi-Agent System with Creative AI Chat
====================================================

Main application for task mining analysis with AI-powered chat interface.

Features:
- Creative AI chat with higher temperature for diverse responses
- Completed task filtering (excludes closed tasks from bottleneck analysis)
- Vega-Lite chart generation and export
- Multi-dataset support (Salesforce & Amadeus)
- Natural language query processing
- PDF export capabilities

Usage:
    python main.py
    run_main.bat (Windows)
"""

import os
import json
import textwrap
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys

import pandas as pd
import altair as alt

# Try to import OpenAI with new API
try:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize OpenAI client with new API
    client = OpenAI(api_key=os.getenv('SECRET_KEY'))
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] OpenAI not available. Chat features will be limited.")

# Try to import comprehensive analytics
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from comprehensive_analytics import ComprehensiveAnalyticsReader
    COMPREHENSIVE_ANALYTICS_AVAILABLE = True
except ImportError as e:
    COMPREHENSIVE_ANALYTICS_AVAILABLE = False
    print(f"[WARNING] Comprehensive analytics not available: {e}")

# -------------------------------
# Configuration
# -------------------------------
# Use relative path from the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, "Data Sources")

SALESFORCE_FILE = "SalesforceOffice_synthetic_varied_100users_V1_with_teams.csv"
AMADEUS_FILE = "amadeus-demo-full-no-fields.csv"

CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# -------------------------------
# Utilities
# -------------------------------
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    return df

def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    for c in df.columns:
        lc = c.lower()
        if any(cand.lower() in lc for cand in candidates):
            return c
    return None

def save_chart(chart: alt.Chart, name: str) -> Dict[str, str]:
    base = os.path.join(CHARTS_DIR, name)
    html_path = f"{base}.html"
    vl_path = f"{base}.vl.json"
    chart.save(html_path)
    chart_json = chart.to_dict()
    with open(vl_path, "w", encoding="utf-8") as f:
        json.dump(chart_json, f, ensure_ascii=False, indent=2)
    return {"html": html_path, "vegalite": vl_path}

def fmt(msg: str) -> str:
    return textwrap.fill(msg, width=100)

def append_facts_block(text: str, dataset: str, filters: Dict[str, Any], metrics: Dict[str, Any]) -> str:
    """
    Append machine-readable facts block to analysis text
    
    Args:
        text: Original text
        dataset: Dataset identifier
        filters: Applied filters
        metrics: Computed metrics
    
    Returns:
        Text with appended facts block
    """
    facts = {
        "dataset": dataset,
        "filters": filters,
        "metrics": metrics
    }
    
    facts_json = json.dumps(facts, indent=2)
    
    return f"{text}\n\n```facts\n{facts_json}\n```"

# -------------------------------
# Enhanced AI Chat Interface with Creative Responses
# -------------------------------
class CreativeDataChatBot:
    def __init__(self, salesforce_agent, amadeus_agent):
        self.salesforce_agent = salesforce_agent
        self.amadeus_agent = amadeus_agent
        self.current_dataset = "salesforce"
        
    def is_chat_query(self, query: str) -> bool:
        """Detect if a query is a natural language question"""
        query_lower = query.lower()
        
        # Chat indicators
        chat_indicators = [
            "who", "what", "when", "where", "why", "how",
            "most", "least", "active", "busy", "efficient",
            "average", "total", "count", "number", "many",
            "longest", "shortest", "highest", "lowest",
            "top", "bottom", "best", "worst", "prevalent",
            "common", "frequent", "rare", "unusual",
            "bottleneck", "bottlenecks", "some", "types",
            "insights", "analysis", "patterns", "trends",
            "recommendations", "suggestions", "improvements",
            # Comprehensive analytics keywords
            "aging", "flow efficiency", "handoff", "handoffs",
            "interaction", "interactions", "comprehensive"
        ]
        
        # Check if query contains chat indicators
        return any(indicator in query_lower for indicator in chat_indicators)
    
    def get_data_summary(self, dataset_name):
        """Get comprehensive data summary for AI context"""
        if dataset_name == "salesforce":
            agent = self.salesforce_agent
        else:
            agent = self.amadeus_agent
            
        df = agent.df
        
        summary = {
            "dataset": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(3).to_dict('records')
        }
        
        # Add specific insights
        if hasattr(agent, 'user_col') and agent.user_col:
            summary["unique_users"] = df[agent.user_col].nunique()
            summary["most_active_user"] = df[agent.user_col].value_counts().index[0]
            summary["user_activity_counts"] = df[agent.user_col].value_counts().head(5).to_dict()
            
        if hasattr(agent, 'duration_col') and agent.duration_col:
            summary["avg_duration"] = df[agent.duration_col].mean()
            summary["max_duration"] = df[agent.duration_col].max()
            summary["min_duration"] = df[agent.duration_col].min()
            
        if hasattr(agent, 'activity_col') and agent.activity_col:
            summary["unique_activities"] = df[agent.activity_col].nunique()
            summary["most_common_activity"] = df[agent.activity_col].value_counts().index[0]
            summary["activity_counts"] = df[agent.activity_col].value_counts().head(5).to_dict()
            
        if hasattr(agent, 'team_col') and agent.team_col:
            summary["unique_teams"] = df[agent.team_col].nunique()
            summary["team_counts"] = df[agent.team_col].value_counts().to_dict()
            
        return summary
    
    def identify_completed_tasks(self, df, activity_col):
        """Identify completed/closed tasks that should be excluded from bottleneck analysis"""
        if not activity_col:
            return set()
        
        # Common patterns for completed/closed tasks
        completed_patterns = [
            'complete', 'completed', 'close', 'closed', 'finish', 'finished',
            'done', 'end', 'ended', 'final', 'finalize', 'submit', 'submitted',
            'approve', 'approved', 'reject', 'rejected', 'cancel', 'cancelled',
            'archive', 'archived', 'delete', 'deleted', 'terminate', 'terminated'
        ]
        
        completed_tasks = set()
        for activity in df[activity_col].unique():
            activity_lower = str(activity).lower()
            if any(pattern in activity_lower for pattern in completed_patterns):
                completed_tasks.add(activity)
        
        return completed_tasks
    
    def chat_with_ai(self, question: str) -> str:
        """Chat with AI about the data using higher temperature for creative responses"""
        if not OPENAI_AVAILABLE:
            return "AI chat not available. Please install OpenAI: pip install openai"
        
        try:
            # Get current dataset summary
            data_summary = self.get_data_summary(self.current_dataset)
            
            # Create enhanced context for AI
            context = f"""
            You are a creative and insightful task mining analyst assistant. You have access to {self.current_dataset} dataset with the following information:
            
            Dataset: {data_summary['dataset']}
            Rows: {data_summary['rows']}
            Columns: {', '.join(data_summary['columns'][:10])}
            
            Key Insights:
            - Unique Users: {data_summary.get('unique_users', 'N/A')}
            - Most Active User: {data_summary.get('most_active_user', 'N/A')}
            - Average Duration: {data_summary.get('avg_duration', 'N/A')}
            - Unique Activities: {data_summary.get('unique_activities', 'N/A')}
            - Most Common Activity: {data_summary.get('most_common_activity', 'N/A')}
            
            User Activity Breakdown: {data_summary.get('user_activity_counts', {})}
            Activity Breakdown: {data_summary.get('activity_counts', {})}
            
            IMPORTANT: When analyzing bottlenecks, consider that completed/closed tasks are NOT bottlenecks - they are successful process completions. 
            Focus on active, ongoing, or problematic activities that cause delays in the workflow.
            
            Please provide creative, insightful, and actionable responses. Be conversational and engaging while remaining professional.
            Offer multiple perspectives and suggest innovative solutions. If you need more detailed analysis, suggest running specific commands like 'summary', 'bottlenecks', etc.
            """
            
            # Use new OpenAI API with higher temperature for creative responses
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": question}
                ],
                max_tokens=600,  # Increased for more detailed responses
                temperature=0.8,  # Higher temperature for more creative responses
                top_p=0.9,  # Higher top_p for more diverse responses
                presence_penalty=0.1,  # Slight penalty to avoid repetition
                frequency_penalty=0.1   # Slight penalty to encourage variety
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI chat error: {e}"
    
    def handle_smart_query(self, query: str) -> str:
        """Handle smart queries with automatic detection"""
        query_lower = query.lower()
        
        # Check for dataset switching
        if "switch to" in query_lower or "use" in query_lower or "change to" in query_lower:
            if "amadeus" in query_lower:
                self.current_dataset = "amadeus"
                return "Switched to Amadeus dataset. You can now ask questions about this data."
            elif "salesforce" in query_lower:
                self.current_dataset = "salesforce"
                return "Switched to Salesforce dataset. You can now ask questions about this data."
        
        # Get current agent
        agent = self.salesforce_agent if self.current_dataset == "salesforce" else self.amadeus_agent
        df = agent.df
        
        # Check for comprehensive analytics queries first
        if hasattr(agent, 'analytics_reader') and agent.analytics_reader:
            if any(word in query_lower for word in ["aging", "flow efficiency", "handoff", "handoffs", "interaction", "comprehensive"]):
                try:
                    result = agent.handle(query)
                    return result.get("text", "No analytics response available.")
                except Exception as e:
                    print(f"[ERROR] Analytics query failed: {e}")
                    # Fall through to regular handling
        
        # Handle specific question patterns
        if any(word in query_lower for word in ["who", "most active", "busiest", "active user", "prevalent"]):
            return self.answer_user_questions(query, agent, df)
        
        if any(word in query_lower for word in ["how many", "count", "total", "number", "many users"]):
            return self.answer_count_questions(query, agent, df)
        
        if any(word in query_lower for word in ["average", "mean", "duration", "time", "longest", "shortest"]):
            return self.answer_duration_questions(query, agent, df)
        
        if any(word in query_lower for word in ["activity", "activities", "common", "frequent"]):
            return self.answer_activity_questions(query, agent, df)
        
        if any(word in query_lower for word in ["team", "teams", "group"]):
            return self.answer_team_questions(query, agent, df)
        
        if any(word in query_lower for word in ["bottleneck", "bottlenecks", "some", "types"]):
            return self.answer_bottleneck_questions(query, agent, df)
        
        # Default to AI chat for creative responses
        return self.chat_with_ai(query)
    
    def answer_user_questions(self, query: str, agent, df) -> str:
        """Answer questions about users"""
        if not hasattr(agent, 'user_col') or not agent.user_col:
            return "User information not available in this dataset."
        
        user_col = agent.user_col
        user_counts = df[user_col].value_counts()
        
        if "most active" in query.lower() or "busiest" in query.lower() or "prevalent" in query.lower():
            most_active = user_counts.index[0]
            count = user_counts.iloc[0]
            return f"🎯 The most active user is '{most_active}' with {count} activities. This user is clearly the powerhouse of your team!"
        
        if "top" in query.lower() and ("user" in query.lower() or "users" in query.lower()):
            top_users = user_counts.head(5)
            result = "🏆 Top 5 users by activity:\n"
            for i, (user, count) in enumerate(top_users.items(), 1):
                result += f"{i}. {user}: {count} activities\n"
            return result
        
        if "who" in query.lower():
            return f"👤 The most active user is '{user_counts.index[0]}' with {user_counts.iloc[0]} activities."
        
        return self.chat_with_ai(query)
    
    def answer_count_questions(self, query: str, agent, df) -> str:
        """Answer questions about counts and totals"""
        if "how many users" in query.lower() or "number of users" in query.lower():
            if hasattr(agent, 'user_col') and agent.user_col:
                count = df[agent.user_col].nunique()
                return f"👥 There are {count} unique users in the {self.current_dataset} dataset. That's a {count}-person team working on these processes!"
            return "User information not available."
        
        if "how many activities" in query.lower() or "number of activities" in query.lower():
            if hasattr(agent, 'activity_col') and agent.activity_col:
                count = df[agent.activity_col].nunique()
                return f"⚡ There are {count} unique activities in the {self.current_dataset} dataset. That's quite a diverse set of tasks!"
            return "Activity information not available."
        
        if "total" in query.lower() and ("records" in query.lower() or "rows" in query.lower()):
            return f"📊 There are {len(df)} total records in the {self.current_dataset} dataset. That's a substantial amount of process data to analyze!"
        
        if "how many" in query.lower():
            if hasattr(agent, 'user_col') and agent.user_col:
                count = df[agent.user_col].nunique()
                return f"👥 There are {count} unique users in the {self.current_dataset} dataset."
        
        return self.chat_with_ai(query)
    
    def answer_duration_questions(self, query: str, agent, df) -> str:
        """Answer questions about duration and timing"""
        if not hasattr(agent, 'duration_col') or not agent.duration_col:
            return "Duration information not available in this dataset."
        
        duration_col = agent.duration_col
        
        if "average" in query.lower() and "duration" in query.lower():
            avg_duration = df[duration_col].mean()
            return f"⏱️ The average duration is {avg_duration:.2f} seconds. This gives us a baseline for process efficiency!"
        
        if "longest" in query.lower() or "maximum" in query.lower():
            max_duration = df[duration_col].max()
            return f"🐌 The longest duration is {max_duration:.2f} seconds. That's quite a marathon task!"
        
        if "shortest" in query.lower() or "minimum" in query.lower():
            min_duration = df[duration_col].min()
            return f"⚡ The shortest duration is {min_duration:.2f} seconds. Now that's efficiency!"
        
        if "duration" in query.lower():
            avg_duration = df[duration_col].mean()
            max_duration = df[duration_col].max()
            min_duration = df[duration_col].min()
            return f"⏱️ Duration stats: Average={avg_duration:.2f}s, Max={max_duration:.2f}s, Min={min_duration:.2f}s. Quite a range of process speeds!"
        
        return self.chat_with_ai(query)
    
    def answer_activity_questions(self, query: str, agent, df) -> str:
        """Answer questions about activities"""
        if not hasattr(agent, 'activity_col') or not agent.activity_col:
            return "Activity information not available in this dataset."
        
        activity_col = agent.activity_col
        activity_counts = df[activity_col].value_counts()
        
        if "most common" in query.lower() or "frequent" in query.lower():
            most_common = activity_counts.index[0]
            count = activity_counts.iloc[0]
            return f"🔥 The most common activity is '{most_common}' with {count} occurrences. This is clearly a core part of your workflow!"
        
        if "top" in query.lower() and "activity" in query.lower():
            top_activities = activity_counts.head(5)
            result = "🏆 Top 5 activities:\n"
            for i, (activity, count) in enumerate(top_activities.items(), 1):
                result += f"{i}. {activity}: {count} times\n"
            return result
        
        if "activity" in query.lower():
            most_common = activity_counts.index[0]
            count = activity_counts.iloc[0]
            return f"🔥 The most common activity is '{most_common}' with {count} occurrences."
        
        return self.chat_with_ai(query)
    
    def answer_team_questions(self, query: str, agent, df) -> str:
        """Answer questions about teams"""
        if not hasattr(agent, 'team_col') or not agent.team_col:
            return "Team information not available in this dataset."
        
        team_col = agent.team_col
        team_counts = df[team_col].value_counts()
        
        if "how many teams" in query.lower():
            count = df[team_col].nunique()
            return f"👥 There are {count} unique teams in the {self.current_dataset} dataset. Teamwork makes the dream work!"
        
        if "most active team" in query.lower() or "busiest team" in query.lower():
            most_active = team_counts.index[0]
            count = team_counts.iloc[0]
            return f"🏆 The most active team is '{most_active}' with {count} activities. They're clearly the MVPs!"
        
        if "team" in query.lower():
            count = df[team_col].nunique()
            return f"👥 There are {count} unique teams in the {self.current_dataset} dataset."
        
        return self.chat_with_ai(query)
    
    def answer_bottleneck_questions(self, query: str, agent, df) -> str:
        """Answer questions about bottlenecks with completed task filtering"""
        if not (hasattr(agent, 'activity_col') and agent.activity_col and 
                hasattr(agent, 'duration_col') and agent.duration_col):
            return "Bottleneck analysis not available (need activity and duration columns)."
        
        # Identify completed tasks to exclude from bottleneck analysis
        completed_tasks = self.identify_completed_tasks(df, agent.activity_col)
        
        # Filter out completed tasks from bottleneck analysis
        active_df = df[~df[agent.activity_col].isin(completed_tasks)]
        
        if len(active_df) == 0:
            return "All activities appear to be completed tasks. No active bottlenecks found!"
        
        # Calculate bottlenecks for active tasks only
        activity_duration = active_df.groupby(agent.activity_col)[agent.duration_col].mean().sort_values(ascending=False)
        top_bottlenecks = activity_duration.head(5)
        
        result = f"🚧 Top 5 bottlenecks in {self.current_dataset} dataset (excluding completed tasks):\n"
        for i, (activity, avg_duration) in enumerate(top_bottlenecks.items(), 1):
            result += f"{i}. {activity}: {avg_duration:.2f} seconds average\n"
        
        result += f"\n🎯 The longest active activity is '{top_bottlenecks.index[0]}' with {top_bottlenecks.iloc[0]:.2f} seconds average duration."
        
        if completed_tasks:
            result += f"\n✅ Excluded {len(completed_tasks)} completed tasks from analysis: {', '.join(list(completed_tasks)[:3])}{'...' if len(completed_tasks) > 3 else ''}"
        
        return result

# -------------------------------
# Enhanced Agent Classes (from original with completed task awareness)
# -------------------------------
class Agent:
    def __init__(self, name: str, df: pd.DataFrame):
        self.name = name
        self.df = df

    def help(self) -> str:
        return (
            "You can ask for things like:\n"
            "  - 'summary'\n"
            "  - 'top bottlenecks'\n"
            "  - 'team performance'\n"
            "  - 'app usage'\n"
            "  - 'export chart: team performance'\n"
            "  - 'recommendations for managers'\n"
            "  - 'who is the most active user?' (natural language)\n"
            "  - 'how many users are there?' (natural language)\n"
            "  - 'what are some bottlenecks?' (natural language)\n"
            "  - 'give me insights about the data' (creative AI analysis)\n"
            "Type 'switch' to switch datasets or 'exit' to quit."
        )

    def handle(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError

class SalesforceAgent(Agent):
    def __init__(self, df: pd.DataFrame):
        super().__init__("SalesforceAgent", df)
        self.user_col = find_column(df, ["user", "resource", "agent_profile_id"])
        self.team_col = find_column(df, ["team", "teams"])
        self.duration_col = find_column(df, ["duration_seconds", "duration", "task_duration", "elapsed"])
        self.activity_col = find_column(df, ["activity", "step", "original_activity"])
        self.app_col = find_column(df, ["process_name", "process", "application", "window", "process_name"])
        self.case_col = find_column(df, ["case_id", "case", "id"])
        self.start_col = find_column(df, ["start_time", "start", "timestamp"])
        self.end_col = find_column(df, ["end_time", "end"])
        
        if self.duration_col and not pd.api.types.is_numeric_dtype(self.df[self.duration_col]):
            self.df[self.duration_col] = pd.to_numeric(self.df[self.duration_col], errors="coerce")
        
        # Initialize comprehensive analytics reader
        if COMPREHENSIVE_ANALYTICS_AVAILABLE:
            try:
                self.analytics_reader = ComprehensiveAnalyticsReader()
            except Exception as e:
                print(f"[WARNING] Could not initialize analytics reader: {e}")
                self.analytics_reader = None
        else:
            self.analytics_reader = None

    def summary(self) -> Dict[str, Any]:
        n_rows = len(self.df)
        n_users = self.df[self.user_col].nunique() if self.user_col else None
        n_teams = self.df[self.team_col].nunique() if self.team_col else None
        duration_mean = self.df[self.duration_col].mean() if self.duration_col else None

        text = (
            f"Salesforce synthetic task-mining dataset summary:\n"
            f"- rows: {n_rows}\n"
            f"- unique users: {n_users}\n"
            f"- teams: {n_teams}\n"
            f"- avg duration (s): {round(duration_mean,2) if duration_mean is not None else 'n/a'}"
        )
        
        # Append facts block
        metrics = {
            "case_count": n_rows,
            "unique_users": n_users,
            "unique_teams": n_teams,
            "avg_duration_seconds": round(duration_mean, 2) if duration_mean else None
        }
        text = append_facts_block(text, "sf", {}, metrics)
        
        if self.user_col and self.duration_col:
            agg = (
                self.df.groupby(self.user_col)[self.duration_col]
                .mean()
                .reset_index()
                .sort_values(self.duration_col, ascending=False)
                .head(20)
            )
            chart = (
                alt.Chart(agg)
                .mark_bar()
                .encode(
                    x=alt.X(f"{self.duration_col}:Q", title="Avg Duration (s)"),
                    y=alt.Y(f"{self.user_col}:N", sort='-x', title="User"),
                    tooltip=[self.user_col, self.duration_col],
                )
                .properties(title="Avg Task Duration per User (Top 20)", width=600, height=400)
            )
            return {"text": text, "chart": chart}
        return {"text": text}

    def top_bottlenecks(self) -> Dict[str, Any]:
        if not (self.activity_col and self.duration_col):
            return {"text": "Cannot compute bottlenecks (need activity and duration columns)."}
        
        # Identify completed tasks to exclude
        completed_tasks = self.identify_completed_tasks(self.df, self.activity_col)
        active_df = self.df[~self.df[self.activity_col].isin(completed_tasks)]
        
        if len(active_df) == 0:
            return {"text": "All activities appear to be completed tasks. No active bottlenecks found!"}
        
        agg = (
            active_df.groupby(self.activity_col)[self.duration_col]
            .mean()
            .reset_index()
            .sort_values(self.duration_col, ascending=False)
            .head(20)
        )
        
        # Prepare metrics for facts block
        top_activity = agg.iloc[0][self.activity_col] if len(agg) > 0 else None
        top_duration = agg.iloc[0][self.duration_col] if len(agg) > 0 else None
        
        metrics = {
            "bottleneck_count": len(agg),
            "top_bottleneck_activity": str(top_activity) if top_activity else None,
            "top_bottleneck_duration": round(float(top_duration), 2) if top_duration else None,
            "excluded_completed_tasks": len(completed_tasks)
        }
        
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X(f"{self.duration_col}:Q", title="Avg Duration (s)"),
                y=alt.Y(f"{self.activity_col}:N", sort='-x', title="Activity"),
                tooltip=[self.activity_col, self.duration_col],
                color=alt.Color(f"{self.duration_col}:Q", scale=alt.Scale(scheme="reds")),
            )
            .properties(title="Top Activity Bottlenecks (Avg Duration) - Active Tasks Only", width=600, height=400)
        )
        
        text = "These activities have the highest average durations; consider standardizing steps or automating repeated inputs. (Completed tasks excluded from analysis.)"
        text = append_facts_block(text, "sf", {}, metrics)
        
        return {"text": text, "chart": chart}

    def identify_completed_tasks(self, df, activity_col):
        """Identify completed/closed tasks that should be excluded from bottleneck analysis"""
        if not activity_col:
            return set()
        
        # Common patterns for completed/closed tasks
        completed_patterns = [
            'complete', 'completed', 'close', 'closed', 'finish', 'finished',
            'done', 'end', 'ended', 'final', 'finalize', 'submit', 'submitted',
            'approve', 'approved', 'reject', 'rejected', 'cancel', 'cancelled',
            'archive', 'archived', 'delete', 'deleted', 'terminate', 'terminated'
        ]
        
        completed_tasks = set()
        for activity in df[activity_col].unique():
            activity_lower = str(activity).lower()
            if any(pattern in activity_lower for pattern in completed_patterns):
                completed_tasks.add(activity)
        
        return completed_tasks

    def team_performance(self) -> Dict[str, Any]:
        if not (self.team_col and self.duration_col):
            return {"text": "Team view unavailable (team or duration column missing)."}
        agg = (
            self.df.groupby(self.team_col)[self.duration_col]
            .mean()
            .reset_index()
            .sort_values(self.duration_col, ascending=False)
        )
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X(f"{self.duration_col}:Q", title="Avg Duration (s)"),
                y=alt.Y(f"{self.team_col}:N", sort='-x', title="Team"),
                tooltip=[self.team_col, self.duration_col],
                color=alt.Color(f"{self.duration_col}:Q", scale=alt.Scale(scheme="blues")),
            )
            .properties(title="Average Task Duration by Team", width=600, height=400)
        )
        p80 = agg[self.duration_col].quantile(0.8)
        under = agg[agg[self.duration_col] <= p80][self.team_col].tolist()
        over = agg[agg[self.duration_col] > p80][self.team_col].tolist()
        advice = (
            "Managerial guidance: teams above the 80th percentile in average duration likely face queueing or rework. "
            f"Consider short-term load balancing and targeted SOP refresh. Potential improvement pairs: "
            f"{', '.join(over)} ↔ {', '.join(under)}."
        )
        return {"text": advice, "chart": chart}

    def app_usage(self) -> Dict[str, Any]:
        if not self.app_col:
            return {"text": "Could not find application/process column to compute app usage."}
        counts = self.df[self.app_col].value_counts().reset_index()
        counts.columns = ["application", "events"]
        chart = (
            alt.Chart(counts.head(20))
            .mark_bar()
            .encode(
                x="events:Q", 
                y=alt.Y("application:N", sort='-x'), 
                tooltip=["application", "events"],
                color=alt.Color("events:Q", scale=alt.Scale(scheme="greens"))
            )
            .properties(title="Top Application Usage (events)", width=600, height=400)
        )
        text = "Application usage by event count; unusually high event volume may indicate inefficient tooling or copy/paste loops."
        return {"text": text, "chart": chart}

    def recommendations(self) -> Dict[str, Any]:
        notes = (
            "- Automate repetitive form fills (copy/paste loops) via templated inputs or small RPA scripts.\n"
            "- Standardize the longest-duration activities (top decile) with micro-guides and pre-validation checks.\n"
            "- Rebalance work between long-duration and short-duration teams for the next sprint; review after two weeks.\n"
            "- Introduce a simple escalation trigger when cases sit idle beyond the P80 activity duration for that step."
        )
        return {"text": f"Salesforce recommendations:\n{notes}"}

    def handle(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        
        # Check for comprehensive analytics queries
        if self.analytics_reader and any(word in q for word in ["aging", "flow efficiency", "handoff", "interaction", "comprehensive"]):
            try:
                analytics_response = self.analytics_reader.query_analytics(query, "salesforce")
                return {"text": analytics_response}
            except Exception as e:
                print(f"[ERROR] Comprehensive analytics query failed: {e}")
                # Fall through to regular handling
        
        if "help" in q:
            help_text = self.help()
            if self.analytics_reader:
                help_text += "\n\nAdvanced Analytics:\n  - 'case aging analysis'\n  - 'flow efficiency report'\n  - 'team handoff analysis'\n  - 'interaction patterns'\n  - 'comprehensive summary'"
            return {"text": help_text}
        if "summary" in q:
            return self.summary()
        if "bottleneck" in q:
            return self.top_bottlenecks()
        if "team" in q:
            return self.team_performance()
        if "app" in q or "application" in q:
            return self.app_usage()
        if "recommend" in q:
            return self.recommendations()
        if "export" in q:
            if "team" in q:
                result = self.team_performance()
            elif "bottleneck" in q:
                result = self.top_bottlenecks()
            else:
                result = self.summary()
            if "chart" in result:
                paths = save_chart(result["chart"], f"salesforce_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                result["text"] = f"{result.get('text','Chart saved')} | HTML: {paths['html']} | Vega-Lite JSON: {paths['vegalite']}"
            return result
        
        # Default fallback
        fallback_text = "Salesforce agent: try 'summary', 'top bottlenecks', 'team performance', 'app usage', or 'recommendations'."
        if self.analytics_reader:
            fallback_text += "\n\nOr ask about: case aging, flow efficiency, team handoffs, or interaction patterns."
        return {"text": fallback_text}

class AmadeusAgent(Agent):
    def __init__(self, df: pd.DataFrame):
        super().__init__("AmadeusAgent", df)
        self.activity_col = find_column(df, ["activity", "step"])
        self.user_col = find_column(df, ["resource", "user", "agent"])
        self.team_col = find_column(df, ["team"])
        self.duration_col = find_column(df, ["duration", "duration_seconds"])
        self.title_col = find_column(df, ["title", "window_title"])
        self.process_col = find_column(df, ["process_name", "application", "process"])
        if self.duration_col and not pd.api.types.is_numeric_dtype(self.df[self.duration_col]):
            self.df[self.duration_col] = pd.to_numeric(self.df[self.duration_col], errors="coerce")
        
        # Initialize comprehensive analytics reader
        if COMPREHENSIVE_ANALYTICS_AVAILABLE:
            try:
                self.analytics_reader = ComprehensiveAnalyticsReader()
            except Exception as e:
                print(f"[WARNING] Could not initialize analytics reader: {e}")
                self.analytics_reader = None
        else:
            self.analytics_reader = None

    def summary(self) -> Dict[str, Any]:
        n_rows = len(self.df)
        n_users = self.df[self.user_col].nunique() if self.user_col else None
        n_acts = self.df[self.activity_col].nunique() if self.activity_col else None
        text = f"Amadeus dataset summary: rows={n_rows}, users={n_users}, unique activities={n_acts}"
        if self.activity_col:
            vc = self.df[self.activity_col].value_counts().reset_index()
            vc.columns = ["activity", "events"]
            chart = (
                alt.Chart(vc.head(20))
                .mark_bar()
                .encode(
                    x="events:Q", 
                    y=alt.Y("activity:N", sort='-x'), 
                    tooltip=["activity", "events"],
                    color=alt.Color("events:Q", scale=alt.Scale(scheme="oranges"))
                )
                .properties(title="Top Activities (events)", width=600, height=400)
            )
            return {"text": text, "chart": chart}
        return {"text": text}

    def top_bottlenecks(self) -> Dict[str, Any]:
        if not (self.activity_col and self.duration_col):
            return {"text": "Cannot compute bottlenecks (need activity and duration)."}
        
        # Identify completed tasks to exclude
        completed_tasks = self.identify_completed_tasks(self.df, self.activity_col)
        active_df = self.df[~self.df[self.activity_col].isin(completed_tasks)]
        
        if len(active_df) == 0:
            return {"text": "All activities appear to be completed tasks. No active bottlenecks found!"}
        
        agg = (
            active_df.groupby(self.activity_col)[self.duration_col]
            .mean()
            .reset_index()
            .sort_values(self.duration_col, ascending=False)
            .head(20)
        )
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X(f"{self.duration_col}:Q", title="Avg Duration"),
                y=alt.Y(f"{self.activity_col}:N", sort='-x', title="Activity"),
                tooltip=[self.activity_col, self.duration_col],
                color=alt.Color(f"{self.duration_col}:Q", scale=alt.Scale(scheme="reds")),
            )
            .properties(title="Amadeus: Top Activity Bottlenecks - Active Tasks Only", width=600, height=400)
        )
        return {"text": "Activities with longest average duration are likely bottlenecks. (Completed tasks excluded from analysis.)", "chart": chart}

    def identify_completed_tasks(self, df, activity_col):
        """Identify completed/closed tasks that should be excluded from bottleneck analysis"""
        if not activity_col:
            return set()
        
        # Common patterns for completed/closed tasks
        completed_patterns = [
            'complete', 'completed', 'close', 'closed', 'finish', 'finished',
            'done', 'end', 'ended', 'final', 'finalize', 'submit', 'submitted',
            'approve', 'approved', 'reject', 'rejected', 'cancel', 'cancelled',
            'archive', 'archived', 'delete', 'deleted', 'terminate', 'terminated'
        ]
        
        completed_tasks = set()
        for activity in df[activity_col].unique():
            activity_lower = str(activity).lower()
            if any(pattern in activity_lower for pattern in completed_patterns):
                completed_tasks.add(activity)
        
        return completed_tasks

    def recommendations(self) -> Dict[str, Any]:
        notes = (
            "- Standardize the top-duration activities with concise SOPs; verify required fields before submission.\n"
            "- Where feasible, use small automations for repetitive input (templates, snippets, form-fillers).\n"
            "- If specific processes (applications) dominate event counts, review their UX friction and reduce context switching."
        )
        return {"text": f"Amadeus recommendations:\n{notes}"}

    def handle(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        
        # Check for comprehensive analytics queries
        if self.analytics_reader and any(word in q for word in ["aging", "flow efficiency", "handoff", "interaction", "comprehensive"]):
            try:
                analytics_response = self.analytics_reader.query_analytics(query, "amadeus")
                return {"text": analytics_response}
            except Exception as e:
                print(f"[ERROR] Comprehensive analytics query failed: {e}")
                # Fall through to regular handling
        
        if "help" in q:
            help_text = self.help()
            if self.analytics_reader:
                help_text += "\n\nAdvanced Analytics:\n  - 'case aging analysis'\n  - 'flow efficiency report'\n  - 'resource interaction patterns'\n  - 'comprehensive summary'"
            return {"text": help_text}
        if "summary" in q:
            return self.summary()
        if "bottleneck" in q:
            return self.top_bottlenecks()
        if "recommend" in q:
            return self.recommendations()
        if "export" in q:
            result = self.summary() if "summary" in q else self.top_bottlenecks()
            if "chart" in result:
                paths = save_chart(result["chart"], f"amadeus_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                result["text"] = f"{result.get('text','Chart saved')} | HTML: {paths['html']} | Vega-Lite JSON: {paths['vegalite']}"
            return result
        
        # Default fallback
        fallback_text = "Amadeus agent: try 'summary', 'top bottlenecks', or 'recommendations'."
        if self.analytics_reader:
            fallback_text += "\n\nOr ask about: case aging, flow efficiency, or resource interaction patterns."
        return {"text": fallback_text}

# -------------------------------
# Enhanced Orchestrator with Creative Chat
# -------------------------------
class CreativeOrchestrator:
    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.active = None
        self.chatbot = CreativeDataChatBot(agents["salesforce"], agents["amadeus"])
        
        # Router accuracy tracking
        self.router_selected = None
        self.router_should_have_selected = None

    def select_dataset(self) -> str:
        print("\nDatasets available: [salesforce] or [amadeus].")
        while True:
            ans = input("Which dataset do you want to explore first? ").strip().lower()
            if ans in self.agents:
                self.active = ans
                self.chatbot.current_dataset = ans
                self.router_selected = ans  # Track initial router selection
                return ans
            print("Please type 'salesforce' or 'amadeus'.")

    def detect_dataset_from_query(self, q: str) -> Optional[str]:
        """Detect if query explicitly mentions a dataset"""
        q_lower = q.lower()
        
        if "salesforce" in q_lower:
            return "salesforce"
        elif "amadeus" in q_lower:
            return "amadeus"
        
        return None

    def route(self, q: str) -> Dict[str, Any]:
        if q.strip().lower() == "switch":
            self.active = "amadeus" if self.active == "salesforce" else "salesforce"
            self.chatbot.current_dataset = self.active
            self.router_selected = self.active  # Update router selection
            return {"text": f"Switched to {self.active}."}
        
        if not self.active:
            self.select_dataset()
        
        # Check if query mentions specific dataset (for router accuracy)
        mentioned_dataset = self.detect_dataset_from_query(q)
        if mentioned_dataset and mentioned_dataset != self.active:
            # User explicitly requested different dataset
            self.router_should_have_selected = mentioned_dataset
        
        # Check if it's a chat query
        if self.chatbot.is_chat_query(q):
            response = self.chatbot.handle_smart_query(q)
            return {"text": f"🤖 {response}"}
        
        # Regular agent handling
        result = self.agents[self.active].handle(q)
        
        # Track router accuracy
        result["_router_selected"] = self.router_selected
        result["_router_should_have_selected"] = self.router_should_have_selected
        
        return result
    
    def get_router_accuracy(self) -> Optional[bool]:
        """Get current router accuracy status"""
        if self.router_should_have_selected is None:
            return None  # No explicit dataset mentioned
        
        return self.router_selected == self.router_should_have_selected

def main():
    print("Welcome to the Creative Task Mining Analyst with Enhanced AI Chat!")
    print("=" * 70)
    
    if OPENAI_AVAILABLE:
        print("🎨 Creative AI Chat enabled! You can ask natural questions like:")
        print("  - 'who is the most active user?'")
        print("  - 'how many users are there?'")
        print("  - 'what are some bottlenecks?'")
        print("  - 'give me insights about the data'")
        print("  - 'what patterns do you see?'")
        print("  - 'switch to amadeus dataset'")
    else:
        print("AI Chat not available. Install OpenAI: pip install openai")
    
    # Load data
    salesforce_path = os.path.join(BASE_DIR, SALESFORCE_FILE)
    amadeus_path = os.path.join(BASE_DIR, AMADEUS_FILE)

    if not os.path.exists(salesforce_path):
        print(f"[ERROR] Cannot find {salesforce_path}")
        return
    if not os.path.exists(amadeus_path):
        print(f"[ERROR] Cannot find {amadeus_path}")
        return

    salesforce_df = load_csv(salesforce_path)
    amadeus_df = load_csv(amadeus_path)

    # Instantiate agents
    agents = {
        "salesforce": SalesforceAgent(salesforce_df),
        "amadeus": AmadeusAgent(amadeus_df),
    }
    orch = CreativeOrchestrator(agents)

    print("\nType 'switch' to switch datasets; type 'exit' to quit. Type 'help' for guidance.\n")

    # Ask user to select dataset
    orch.select_dataset()

    while True:
        q = input(f"\n[{orch.active}] Your query: ").strip()
        if not q:
            continue
        if q.lower() == "exit":
            print("Goodbye!")
            break
        result = orch.route(q)
        print("\n" + fmt(result.get("text", "")))
        if "chart" in result:
            save = input("Save chart? (y/n): ").strip().lower()
            if save == "y":
                tag = agents[orch.active].name.lower()
                name = f"{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                paths = save_chart(result["chart"], name)
                print(f"Saved → HTML: {paths['html']} | Vega-Lite JSON: {paths['vegalite']}")

if __name__ == "__main__":
    main()

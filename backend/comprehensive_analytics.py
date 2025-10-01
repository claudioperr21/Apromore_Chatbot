"""
Comprehensive Analytics Data Access Layer
==========================================

Provides text-based insights from comprehensive analytics aggregates
without requiring chart visualization.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


class ComprehensiveAnalyticsReader:
    """Reader for comprehensive analytics aggregate data"""
    
    def __init__(self, base_data_dir: str = None):
        """
        Initialize reader with base data directory
        
        Args:
            base_data_dir: Base directory containing Data Source folder
        """
        if base_data_dir is None:
            # Use relative path from this file
            base_data_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_data_dir)
        self.aggregates_dir = self.base_dir / "mnt" / "data" / "aggregates"
        
        # Check if aggregates directory exists
        self.has_comprehensive_data = self.aggregates_dir.exists()
    
    def load_aggregate(self, dataset: str, aggregate_name: str) -> Optional[pd.DataFrame]:
        """
        Load a specific aggregate CSV file
        
        Args:
            dataset: 'salesforce' or 'amadeus'
            aggregate_name: Name of the aggregate file (without .csv)
        
        Returns:
            DataFrame or None if not found
        """
        if not self.has_comprehensive_data:
            return None
        
        file_path = self.aggregates_dir / dataset / f"{aggregate_name}.csv"
        
        try:
            if file_path.exists():
                return pd.read_csv(file_path)
            return None
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def get_case_aging_insights(self, dataset: str = "salesforce") -> str:
        """Get insights about case aging distribution"""
        prefix = "sf" if dataset == "salesforce" else "ama"
        
        # Try to load from case stage stack data
        stage_df = self.load_aggregate(dataset, f"{prefix}_case_stage_stack")
        
        if stage_df is None or stage_df.empty:
            return f"Case aging data not available for {dataset}."
        
        # Calculate aging buckets
        case_durations = stage_df.groupby('Case_ID')['duration_min'].sum()
        
        total_cases = len(case_durations)
        aging_0_1d = (case_durations <= 1440).sum()  # 24 hours
        aging_1_3d = ((case_durations > 1440) & (case_durations <= 4320)).sum()
        aging_3_7d = ((case_durations > 4320) & (case_durations <= 10080)).sum()
        aging_7_14d = ((case_durations > 10080) & (case_durations <= 20160)).sum()
        aging_14d_plus = (case_durations > 20160).sum()
        
        insights = f"""
Case Aging Analysis for {dataset.title()}:
• Total cases analyzed: {total_cases}
• Cases aged 0-1 days: {aging_0_1d} ({aging_0_1d/total_cases*100:.1f}%)
• Cases aged 1-3 days: {aging_1_3d} ({aging_1_3d/total_cases*100:.1f}%)
• Cases aged 3-7 days: {aging_3_7d} ({aging_3_7d/total_cases*100:.1f}%)
• Cases aged 7-14 days: {aging_7_14d} ({aging_7_14d/total_cases*100:.1f}%)
• Cases aged >14 days: {aging_14d_plus} ({aging_14d_plus/total_cases*100:.1f}%)

Key Insight: {aging_14d_plus} cases ({aging_14d_plus/total_cases*100:.1f}%) are over 14 days old, which may indicate bottlenecks or stalled processes.
"""
        
        return insights.strip()
    
    def get_flow_efficiency_insights(self, dataset: str = "salesforce") -> str:
        """Get insights about flow efficiency (touch vs wait time)"""
        prefix = "sf" if dataset == "salesforce" else "ama"
        
        waterfall_df = self.load_aggregate(dataset, f"{prefix}_case_wait_touch_waterfall")
        
        if waterfall_df is None or waterfall_df.empty:
            return f"Flow efficiency data not available for {dataset}."
        
        # Aggregate touch and wait times
        if 'segment' in waterfall_df.columns and 'seconds' in waterfall_df.columns:
            touch_time = waterfall_df[waterfall_df['segment'].str.contains('touch', case=False, na=False)]['seconds'].sum()
            wait_time = waterfall_df[waterfall_df['segment'].str.contains('wait', case=False, na=False)]['seconds'].sum()
            
            total_time = touch_time + wait_time
            flow_efficiency = (touch_time / total_time * 100) if total_time > 0 else 0
            
            insights = f"""
Flow Efficiency Analysis for {dataset.title()}:
• Total touch time: {touch_time/60:.1f} minutes ({touch_time/3600:.1f} hours)
• Total wait time: {wait_time/60:.1f} minutes ({wait_time/3600:.1f} hours)
• Flow efficiency: {flow_efficiency:.1f}%

Interpretation:
- Flow efficiency shows the ratio of value-add time to total time
- Current efficiency of {flow_efficiency:.1f}% means {100-flow_efficiency:.1f}% of time is spent waiting
- Industry benchmark for good flow efficiency is typically 15-25%
- Your current rate {'exceeds' if flow_efficiency > 25 else 'is below' if flow_efficiency < 15 else 'is within'} industry benchmarks
"""
            
            return insights.strip()
        
        return f"Flow efficiency metrics not properly formatted for {dataset}."
    
    def get_handoff_insights(self, dataset: str = "salesforce", by: str = "team") -> str:
        """Get insights about handoffs between teams or resources"""
        if dataset == "salesforce" and by == "team":
            # Load team handoff data
            timeline_df = self.load_aggregate(dataset, "sf_case_timeline_gantt")
            
            if timeline_df is None or timeline_df.empty or 'team' not in timeline_df.columns:
                return f"Team handoff data not available for {dataset}."
            
            # Calculate handoffs per case
            handoffs_per_case = []
            for case_id in timeline_df['Case_ID'].unique():
                case_data = timeline_df[timeline_df['Case_ID'] == case_id].sort_values('Start_Time')
                teams = case_data['team'].tolist()
                
                handoff_count = 0
                for i in range(1, len(teams)):
                    if teams[i] != teams[i-1]:
                        handoff_count += 1
                
                handoffs_per_case.append(handoff_count)
            
            avg_handoffs = sum(handoffs_per_case) / len(handoffs_per_case) if handoffs_per_case else 0
            max_handoffs = max(handoffs_per_case) if handoffs_per_case else 0
            
            insights = f"""
Team Handoff Analysis for {dataset.title()}:
• Average handoffs per case: {avg_handoffs:.1f}
• Maximum handoffs in a single case: {max_handoffs}
• Cases with 0 handoffs: {handoffs_per_case.count(0)} ({handoffs_per_case.count(0)/len(handoffs_per_case)*100:.1f}%)
• Cases with 3+ handoffs: {sum(1 for h in handoffs_per_case if h >= 3)} ({sum(1 for h in handoffs_per_case if h >= 3)/len(handoffs_per_case)*100:.1f}%)

Key Insight: Each handoff adds coordination overhead and potential delays. Cases with multiple handoffs may benefit from process redesign or better team coordination.
"""
            
            return insights.strip()
        
        return f"Handoff analysis not available for {dataset} by {by}."
    
    def get_interaction_insights(self, dataset: str = "salesforce", level: str = "team") -> str:
        """Get insights about user interactions (clicks, keys, copy/paste)"""
        prefix = "sf" if dataset == "salesforce" else "ama"
        
        if level == "team" and dataset == "salesforce":
            # Load team-level interaction data
            input_mix_df = self.load_aggregate(dataset, f"{prefix}_input_mix_by_team")
            effort_rate_df = self.load_aggregate(dataset, f"{prefix}_effort_rate_by_team")
            
            if input_mix_df is None or effort_rate_df is None:
                return f"Team interaction data not available for {dataset}."
            
            # Analyze input mix
            total_clicks = input_mix_df['mouse_clicks'].sum() if 'mouse_clicks' in input_mix_df.columns else 0
            total_keys = input_mix_df['keypresses'].sum() if 'keypresses' in input_mix_df.columns else 0
            total_copies = input_mix_df['copies'].sum() if 'copies' in input_mix_df.columns else 0
            total_pastes = input_mix_df['pastes'].sum() if 'pastes' in input_mix_df.columns else 0
            
            total_interactions = total_clicks + total_keys + total_copies + total_pastes
            
            avg_effort_rate = effort_rate_df['effort_per_min'].mean() if 'effort_per_min' in effort_rate_df.columns else 0
            
            insights = f"""
Interaction Analysis for {dataset.title()} Teams:
• Total mouse clicks: {total_clicks:,}
• Total keypresses: {total_keys:,}
• Total copy operations: {total_copies:,}
• Total paste operations: {total_pastes:,}
• Average effort rate: {avg_effort_rate:.1f} interactions/minute

Input Mix:
• Clicks: {total_clicks/total_interactions*100:.1f}%
• Keypresses: {total_keys/total_interactions*100:.1f}%
• Copy/Paste: {(total_copies+total_pastes)/total_interactions*100:.1f}%

Key Insight: High copy/paste rates ({(total_copies+total_pastes)/total_interactions*100:.1f}%) may indicate manual data entry that could be automated.
"""
            
            return insights.strip()
        
        elif level == "resource":
            # Load resource-level interaction data
            leaderboard_df = self.load_aggregate(dataset, f"{prefix}_resource_effort_leaderboard")
            effort_rate_df = self.load_aggregate(dataset, f"{prefix}_resource_effort_rate")
            
            if leaderboard_df is None or effort_rate_df is None:
                return f"Resource interaction data not available for {dataset}."
            
            # Get top performers
            top_5_resources = leaderboard_df.head(5) if not leaderboard_df.empty else pd.DataFrame()
            
            avg_effort = effort_rate_df['effort_per_min'].mean() if 'effort_per_min' in effort_rate_df.columns else 0
            max_effort = effort_rate_df['effort_per_min'].max() if 'effort_per_min' in effort_rate_df.columns else 0
            
            insights = f"""
Resource Interaction Analysis for {dataset.title()}:
• Average effort rate: {avg_effort:.1f} interactions/minute
• Maximum effort rate: {max_effort:.1f} interactions/minute
• Performance spread: {max_effort - avg_effort:.1f} interactions/minute

Top 5 Most Active Resources:
"""
            
            for idx, row in top_5_resources.iterrows():
                resource = row.get('Resource', 'Unknown')
                interactions = row.get('total_interactions', 0)
                insights += f"• {resource}: {interactions:,} interactions\n"
            
            insights += f"\nKey Insight: Performance variation suggests opportunities for training or process standardization."
            
            return insights.strip()
        
        return f"Interaction analysis not available for {dataset} at {level} level."
    
    def get_comprehensive_summary(self, dataset: str = "salesforce") -> str:
        """Get a comprehensive summary combining multiple analytics"""
        insights = []
        
        insights.append(f"=== Comprehensive Analytics Summary for {dataset.title()} ===\n")
        
        # Case aging
        insights.append("1. CASE AGING:")
        insights.append(self.get_case_aging_insights(dataset))
        insights.append("")
        
        # Flow efficiency
        insights.append("2. FLOW EFFICIENCY:")
        insights.append(self.get_flow_efficiency_insights(dataset))
        insights.append("")
        
        # Handoffs
        if dataset == "salesforce":
            insights.append("3. TEAM HANDOFFS:")
            insights.append(self.get_handoff_insights(dataset, "team"))
            insights.append("")
        
        # Interactions
        insights.append("4. USER INTERACTIONS:")
        insights.append(self.get_interaction_insights(dataset, "team"))
        
        return "\n".join(insights)
    
    def query_analytics(self, query: str, dataset: str = "salesforce") -> str:
        """
        Natural language query interface for analytics
        
        Args:
            query: User's question about the analytics
            dataset: 'salesforce' or 'amadeus'
        
        Returns:
            Text-based answer
        """
        query_lower = query.lower()
        
        # Route to appropriate analysis based on query
        if any(word in query_lower for word in ["aging", "age", "old", "stale"]):
            return self.get_case_aging_insights(dataset)
        
        elif any(word in query_lower for word in ["flow", "efficiency", "touch", "wait"]):
            return self.get_flow_efficiency_insights(dataset)
        
        elif any(word in query_lower for word in ["handoff", "handoffs", "transition", "transfer"]):
            return self.get_handoff_insights(dataset)
        
        elif any(word in query_lower for word in ["interaction", "clicks", "keys", "effort", "mouse", "keyboard"]):
            if any(word in query_lower for word in ["team", "teams"]):
                return self.get_interaction_insights(dataset, "team")
            elif any(word in query_lower for word in ["resource", "user", "individual", "person"]):
                return self.get_interaction_insights(dataset, "resource")
            else:
                return self.get_interaction_insights(dataset, "team")
        
        elif any(word in query_lower for word in ["comprehensive", "complete", "all", "everything", "summary"]):
            return self.get_comprehensive_summary(dataset)
        
        else:
            return f"""
I can provide comprehensive analytics insights for {dataset}. Try asking about:

• Case aging: "What is the case aging distribution?"
• Flow efficiency: "What's the flow efficiency?"
• Handoffs: "How many handoffs occur between teams?"
• Interactions: "What are the interaction patterns?"
• Complete summary: "Give me a comprehensive summary"
"""


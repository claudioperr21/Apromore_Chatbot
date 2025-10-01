"""
Pandas Metric Computation Functions
===================================

Reusable metric computation functions for task mining analysis.
These functions match the logic used by dashboards to ensure metric parity.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find column name from list of candidates"""
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    for c in df.columns:
        lc = c.lower()
        if any(cand.lower() in lc for cand in candidates):
            return c
    return None


def flow_efficiency(case_df: pd.DataFrame, dataset: str = "salesforce") -> float:
    """
    Calculate flow efficiency: ratio of value-add time to total time
    
    Flow Efficiency = (Active Work Time) / (Total Lead Time)
    
    Args:
        case_df: DataFrame with case data
        dataset: Dataset identifier for column detection
    
    Returns:
        Flow efficiency as a decimal (0.0 to 1.0)
    """
    if len(case_df) == 0:
        return 0.0
    
    # Find necessary columns
    duration_col = find_column(case_df, ["duration_seconds", "duration", "task_duration", "elapsed"])
    case_col = find_column(case_df, ["case_id", "case", "id"])
    
    if not duration_col or not case_col:
        return 0.0
    
    # Ensure duration is numeric
    if not pd.api.types.is_numeric_dtype(case_df[duration_col]):
        case_df = case_df.copy()
        case_df[duration_col] = pd.to_numeric(case_df[duration_col], errors="coerce")
    
    # Calculate per-case metrics
    case_stats = case_df.groupby(case_col).agg({
        duration_col: ['sum', 'count']
    })
    
    # Total work time (sum of all activity durations)
    total_work_time = case_stats[(duration_col, 'sum')].sum()
    
    # Estimate lead time (from first to last activity per case)
    # This is a simplified calculation - ideally we'd use actual case start/end timestamps
    try:
        start_col = find_column(case_df, ["start_time", "start", "timestamp"])
        end_col = find_column(case_df, ["end_time", "end"])
        
        if start_col and end_col:
            # Parse timestamps
            case_lead_times = []
            for case_id in case_df[case_col].unique():
                case_data = case_df[case_df[case_col] == case_id]
                if start_col in case_data.columns and end_col in case_data.columns:
                    try:
                        start_times = pd.to_datetime(case_data[start_col], errors='coerce')
                        end_times = pd.to_datetime(case_data[end_col], errors='coerce')
                        
                        if not start_times.isna().all() and not end_times.isna().all():
                            first_start = start_times.min()
                            last_end = end_times.max()
                            if pd.notna(first_start) and pd.notna(last_end):
                                lead_time = (last_end - first_start).total_seconds()
                                case_lead_times.append(lead_time)
                    except:
                        pass
            
            if case_lead_times:
                total_lead_time = sum(case_lead_times)
                if total_lead_time > 0:
                    return min(1.0, total_work_time / total_lead_time)
        
        # Fallback: use activity count as proxy for lead time
        # Assume average wait time between activities
        n_activities = len(case_df)
        avg_wait = 300  # 5 minutes default wait time between activities
        estimated_lead_time = total_work_time + (n_activities * avg_wait)
        
        if estimated_lead_time > 0:
            return min(1.0, total_work_time / estimated_lead_time)
    
    except Exception:
        pass
    
    # Default: conservative estimate
    return 0.5


def case_aging_buckets(case_df: pd.DataFrame, dataset: str = "salesforce") -> Dict[str, int]:
    """
    Calculate case aging distribution (cases by age buckets)
    
    Returns:
        Dictionary with aging buckets: {'0-7d': X, '8-14d': Y, '>14d': Z}
    """
    if len(case_df) == 0:
        return {'0-7d': 0, '8-14d': 0, '>14d': 0}
    
    case_col = find_column(case_df, ["case_id", "case", "id"])
    start_col = find_column(case_df, ["start_time", "start", "timestamp"])
    
    if not case_col or not start_col:
        return {'0-7d': 0, '8-14d': 0, '>14d': 0}
    
    try:
        # Get first activity timestamp per case
        case_starts = case_df.groupby(case_col)[start_col].min()
        case_starts = pd.to_datetime(case_starts, errors='coerce')
        
        # Calculate age from "now" (or use last activity timestamp)
        now = pd.Timestamp.now()
        last_activity = pd.to_datetime(case_df[start_col], errors='coerce').max()
        if pd.notna(last_activity):
            now = last_activity
        
        ages = (now - case_starts).dt.total_seconds() / 86400  # Convert to days
        
        buckets = {
            '0-7d': (ages <= 7).sum(),
            '8-14d': ((ages > 7) & (ages <= 14)).sum(),
            '>14d': (ages > 14).sum()
        }
        
        return buckets
    
    except Exception:
        return {'0-7d': 0, '8-14d': 0, '>14d': 0}


def throughput_minutes(case_df: pd.DataFrame, dataset: str = "salesforce") -> float:
    """
    Calculate average case throughput time in minutes
    
    Args:
        case_df: DataFrame with case data
        dataset: Dataset identifier
    
    Returns:
        Average throughput time in minutes
    """
    if len(case_df) == 0:
        return 0.0
    
    duration_col = find_column(case_df, ["duration_seconds", "duration", "task_duration", "elapsed"])
    case_col = find_column(case_df, ["case_id", "case", "id"])
    
    if not duration_col or not case_col:
        return 0.0
    
    # Ensure duration is numeric
    if not pd.api.types.is_numeric_dtype(case_df[duration_col]):
        case_df = case_df.copy()
        case_df[duration_col] = pd.to_numeric(case_df[duration_col], errors="coerce")
    
    # Sum duration per case and convert to minutes
    case_throughput = case_df.groupby(case_col)[duration_col].sum()
    avg_throughput_seconds = case_throughput.mean()
    
    return avg_throughput_seconds / 60.0  # Convert to minutes


def handoffs(case_df: pd.DataFrame, dataset: str = "salesforce") -> float:
    """
    Calculate average number of handoffs per case
    
    A handoff occurs when the user/resource changes within a case
    
    Args:
        case_df: DataFrame with case data
        dataset: Dataset identifier
    
    Returns:
        Average number of handoffs per case
    """
    if len(case_df) == 0:
        return 0.0
    
    case_col = find_column(case_df, ["case_id", "case", "id"])
    user_col = find_column(case_df, ["user", "resource", "agent_profile_id", "agent"])
    
    if not case_col or not user_col:
        return 0.0
    
    try:
        # Sort by case and time (if available)
        sort_cols = [case_col]
        time_col = find_column(case_df, ["start_time", "start", "timestamp"])
        if time_col:
            sort_cols.append(time_col)
        
        sorted_df = case_df.sort_values(sort_cols)
        
        # Count handoffs per case (transitions between different users)
        handoff_counts = []
        
        for case_id in sorted_df[case_col].unique():
            case_data = sorted_df[sorted_df[case_col] == case_id]
            users = case_data[user_col].tolist()
            
            # Count transitions where user changes
            handoff_count = 0
            for i in range(1, len(users)):
                if users[i] != users[i-1]:
                    handoff_count += 1
            
            handoff_counts.append(handoff_count)
        
        return np.mean(handoff_counts) if handoff_counts else 0.0
    
    except Exception:
        return 0.0


def compute_panel_metrics(case_df: pd.DataFrame, dataset: str = "salesforce",
                         filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Compute the standard panel of metrics for a dataset slice
    
    Args:
        case_df: DataFrame with case data
        dataset: Dataset identifier
        filters: Applied filters (for context)
    
    Returns:
        Dictionary with computed metrics
    """
    metrics = {
        "dataset": dataset,
        "filters": filters or {},
        "case_count": len(case_df),
        "flow_efficiency": flow_efficiency(case_df, dataset),
        "throughput_minutes": throughput_minutes(case_df, dataset),
        "handoffs": handoffs(case_df, dataset),
        "aging_buckets": case_aging_buckets(case_df, dataset)
    }
    
    # Add basic statistics
    duration_col = find_column(case_df, ["duration_seconds", "duration", "task_duration", "elapsed"])
    if duration_col:
        if not pd.api.types.is_numeric_dtype(case_df[duration_col]):
            case_df = case_df.copy()
            case_df[duration_col] = pd.to_numeric(case_df[duration_col], errors="coerce")
        
        metrics["avg_duration_seconds"] = case_df[duration_col].mean()
        metrics["median_duration_seconds"] = case_df[duration_col].median()
        metrics["max_duration_seconds"] = case_df[duration_col].max()
    
    # Add activity statistics
    activity_col = find_column(case_df, ["activity", "step", "original_activity"])
    if activity_col:
        metrics["unique_activities"] = case_df[activity_col].nunique()
        top_activity = case_df[activity_col].value_counts().index[0] if len(case_df) > 0 else None
        metrics["most_common_activity"] = str(top_activity) if top_activity else None
    
    # Add user statistics
    user_col = find_column(case_df, ["user", "resource", "agent_profile_id", "agent"])
    if user_col:
        metrics["unique_users"] = case_df[user_col].nunique()
    
    return metrics


def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to dataframe
    
    Args:
        df: Source dataframe
        filters: Dictionary of filters (case_id, team, resource, time_range, etc.)
    
    Returns:
        Filtered dataframe
    """
    filtered_df = df.copy()
    
    # Case ID filter
    if filters.get("case_id"):
        case_col = find_column(df, ["case_id", "case", "id"])
        if case_col:
            case_ids = filters["case_id"] if isinstance(filters["case_id"], list) else [filters["case_id"]]
            filtered_df = filtered_df[filtered_df[case_col].isin(case_ids)]
    
    # Team filter
    if filters.get("team"):
        team_col = find_column(df, ["team", "teams"])
        if team_col:
            teams = filters["team"] if isinstance(filters["team"], list) else [filters["team"]]
            filtered_df = filtered_df[filtered_df[team_col].isin(teams)]
    
    # Resource/User filter
    if filters.get("resource"):
        user_col = find_column(df, ["user", "resource", "agent_profile_id", "agent"])
        if user_col:
            resources = filters["resource"] if isinstance(filters["resource"], list) else [filters["resource"]]
            filtered_df = filtered_df[filtered_df[user_col].isin(resources)]
    
    # Time range filter
    if filters.get("time_range"):
        time_col = find_column(df, ["start_time", "start", "timestamp"])
        if time_col:
            try:
                time_range = filters["time_range"]
                if isinstance(time_range, dict):
                    start = pd.to_datetime(time_range.get("start"), errors='coerce')
                    end = pd.to_datetime(time_range.get("end"), errors='coerce')
                    
                    timestamps = pd.to_datetime(filtered_df[time_col], errors='coerce')
                    
                    if pd.notna(start):
                        filtered_df = filtered_df[timestamps >= start]
                    if pd.notna(end):
                        filtered_df = filtered_df[timestamps <= end]
            except:
                pass
    
    return filtered_df


"""
Schema Dictionary Builder for Hallucination Detection
======================================================

Builds and caches schema dictionaries from loaded datasets to detect
when AI responses reference unknown columns, teams, activities, or other entities.
"""

from typing import Dict, Set, Optional, Any
from functools import lru_cache
import pandas as pd
import time


class SchemaDict:
    """Schema dictionary for detecting hallucinations in AI responses"""
    
    def __init__(self, salesforce_df: Optional[pd.DataFrame] = None, 
                 amadeus_df: Optional[pd.DataFrame] = None):
        self.salesforce_df = salesforce_df
        self.amadeus_df = amadeus_df
        self.last_refresh = time.time()
        self.cache_ttl = 600  # 10 minutes
        
        self._schema = self._build_schema()
    
    def _build_schema(self) -> Dict[str, Dict[str, Set[str]]]:
        """Build schema dictionary from both datasets"""
        schema = {
            "salesforce": {
                "columns": set(),
                "activities": set(),
                "teams": set(),
                "users": set(),
                "processes": set(),
                "window_titles": set()
            },
            "amadeus": {
                "columns": set(),
                "activities": set(),
                "teams": set(),
                "users": set(),
                "processes": set(),
                "window_titles": set()
            }
        }
        
        # Build Salesforce schema
        if self.salesforce_df is not None:
            df = self.salesforce_df
            schema["salesforce"]["columns"] = set(df.columns)
            
            # Extract unique values for key columns
            activity_col = self._find_column(df, ["activity", "step", "original_activity"])
            if activity_col:
                schema["salesforce"]["activities"] = set(df[activity_col].dropna().unique())
            
            team_col = self._find_column(df, ["team", "teams"])
            if team_col:
                schema["salesforce"]["teams"] = set(df[team_col].dropna().unique())
            
            user_col = self._find_column(df, ["user", "resource", "agent_profile_id"])
            if user_col:
                schema["salesforce"]["users"] = set(df[user_col].dropna().unique())
            
            process_col = self._find_column(df, ["process_name", "process", "application", "window"])
            if process_col:
                schema["salesforce"]["processes"] = set(df[process_col].dropna().unique())
            
            title_col = self._find_column(df, ["window_title", "title"])
            if title_col:
                schema["salesforce"]["window_titles"] = set(df[title_col].dropna().unique())
        
        # Build Amadeus schema
        if self.amadeus_df is not None:
            df = self.amadeus_df
            schema["amadeus"]["columns"] = set(df.columns)
            
            activity_col = self._find_column(df, ["activity", "step"])
            if activity_col:
                schema["amadeus"]["activities"] = set(df[activity_col].dropna().unique())
            
            team_col = self._find_column(df, ["team"])
            if team_col:
                schema["amadeus"]["teams"] = set(df[team_col].dropna().unique())
            
            user_col = self._find_column(df, ["resource", "user", "agent"])
            if user_col:
                schema["amadeus"]["users"] = set(df[user_col].dropna().unique())
            
            process_col = self._find_column(df, ["process_name", "application", "process"])
            if process_col:
                schema["amadeus"]["processes"] = set(df[process_col].dropna().unique())
            
            title_col = self._find_column(df, ["title", "window_title"])
            if title_col:
                schema["amadeus"]["window_titles"] = set(df[title_col].dropna().unique())
        
        return schema
    
    def _find_column(self, df: pd.DataFrame, candidates: list) -> Optional[str]:
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
    
    def refresh_if_needed(self):
        """Refresh schema cache if TTL expired"""
        if time.time() - self.last_refresh > self.cache_ttl:
            self._schema = self._build_schema()
            self.last_refresh = time.time()
    
    def get_schema(self, dataset: str = None) -> Dict[str, Any]:
        """Get schema dictionary for specified dataset or all datasets"""
        self.refresh_if_needed()
        if dataset:
            return self._schema.get(dataset, {})
        return self._schema
    
    def validate_references(self, text: str, dataset: str) -> Dict[str, Any]:
        """
        Check if text references unknown entities (potential hallucinations)
        
        Returns:
            Dict with hallucination detection results
        """
        self.refresh_if_needed()
        
        if dataset not in self._schema:
            return {
                "has_hallucinations": False,
                "unknown_entities": [],
                "checked": False,
                "reason": f"Unknown dataset: {dataset}"
            }
        
        schema = self._schema[dataset]
        unknown_entities = []
        text_lower = text.lower()
        
        # Check for column references
        # Look for patterns like "column_name" or mentioned columns
        for word in text.split():
            cleaned_word = word.strip(',.!?;:"()[]{}')
            
            # Check if word matches any known column
            if cleaned_word and len(cleaned_word) > 2:
                # Check columns (case-insensitive)
                col_names_lower = {col.lower() for col in schema["columns"]}
                if cleaned_word.lower() in col_names_lower:
                    continue  # Valid column reference
                
                # Check if it's a potential column reference (contains underscore or camelCase)
                if '_' in cleaned_word or (cleaned_word[0].islower() and any(c.isupper() for c in cleaned_word)):
                    # Might be a column reference - check if it exists
                    if cleaned_word.lower() not in col_names_lower:
                        # Could be hallucinated column
                        unknown_entities.append({
                            "type": "column",
                            "value": cleaned_word,
                            "context": "potential_column_reference"
                        })
        
        # Extract quoted strings (often team names, activities, etc.)
        import re
        quoted_strings = re.findall(r'"([^"]+)"', text) + re.findall(r"'([^']+)'", text)
        
        for quoted in quoted_strings:
            # Check if it matches known teams
            if quoted not in schema["teams"] and len(schema["teams"]) > 0:
                # Check case-insensitive
                teams_lower = {str(t).lower() for t in schema["teams"]}
                if quoted.lower() not in teams_lower:
                    # Could be hallucinated team
                    if "team" in text_lower or "group" in text_lower:
                        unknown_entities.append({
                            "type": "team",
                            "value": quoted,
                            "context": "quoted_team_reference"
                        })
            
            # Check if it matches known activities
            if quoted not in schema["activities"] and len(schema["activities"]) > 0:
                activities_lower = {str(a).lower() for a in schema["activities"]}
                if quoted.lower() not in activities_lower:
                    # Could be hallucinated activity
                    if "activity" in text_lower or "step" in text_lower or "process" in text_lower:
                        unknown_entities.append({
                            "type": "activity",
                            "value": quoted,
                            "context": "quoted_activity_reference"
                        })
        
        return {
            "has_hallucinations": len(unknown_entities) > 0,
            "unknown_entities": unknown_entities,
            "checked": True,
            "dataset": dataset
        }
    
    def get_valid_values(self, dataset: str, entity_type: str) -> Set[str]:
        """Get set of valid values for a given entity type in dataset"""
        self.refresh_if_needed()
        if dataset in self._schema and entity_type in self._schema[dataset]:
            return self._schema[dataset][entity_type]
        return set()


# Global schema dictionary instance (will be initialized at app startup)
_global_schema_dict: Optional[SchemaDict] = None


def build_schema_dict(salesforce_df: Optional[pd.DataFrame] = None,
                      amadeus_df: Optional[pd.DataFrame] = None) -> SchemaDict:
    """
    Build or update the global schema dictionary
    
    Args:
        salesforce_df: Salesforce dataset
        amadeus_df: Amadeus dataset
    
    Returns:
        SchemaDict instance
    """
    global _global_schema_dict
    _global_schema_dict = SchemaDict(salesforce_df, amadeus_df)
    return _global_schema_dict


def get_schema_dict() -> Optional[SchemaDict]:
    """Get the global schema dictionary instance"""
    return _global_schema_dict


@lru_cache(maxsize=128)
def cached_validate_references(text_hash: int, dataset: str) -> Dict[str, Any]:
    """Cached validation of references (keyed by text hash)"""
    if _global_schema_dict is None:
        return {
            "has_hallucinations": False,
            "unknown_entities": [],
            "checked": False,
            "reason": "Schema dictionary not initialized"
        }
    
    # This is a simplified cache - in production you'd want better hash handling
    return _global_schema_dict.validate_references(str(text_hash), dataset)


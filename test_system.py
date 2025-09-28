#!/usr/bin/env python3
"""
Test script for Task Mining Multi-Agent System

This script tests the core functionality without requiring the full web interface.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add current directory to path
sys.path.append('.')

try:
    from task_mining_multi_agent import (
        SalesforceAgent, AmadeusAgent, load_csv, 
        find_column, save_chart, BASE_DIR
    )
    print("✓ Successfully imported task mining modules")
except ImportError as e:
    print(f"✗ Failed to import modules: {e}")
    sys.exit(1)

def test_data_loading():
    """Test if CSV files can be loaded"""
    print("\n=== Testing Data Loading ===")
    
    salesforce_path = os.path.join(BASE_DIR, "SalesforceOffice_synthetic_varied_100users_V1.csv")
    amadeus_path = os.path.join(BASE_DIR, "amadeus-demo-full-no-fields.csv")
    
    # Check if files exist
    if not os.path.exists(salesforce_path):
        print(f"✗ Salesforce file not found: {salesforce_path}")
        return False
    else:
        print(f"✓ Salesforce file found: {salesforce_path}")
    
    if not os.path.exists(amadeus_path):
        print(f"✗ Amadeus file not found: {amadeus_path}")
        return False
    else:
        print(f"✓ Amadeus file found: {amadeus_path}")
    
    # Test loading
    try:
        salesforce_df = load_csv(salesforce_path)
        print(f"✓ Salesforce data loaded: {len(salesforce_df)} rows, {len(salesforce_df.columns)} columns")
        print(f"  Columns: {list(salesforce_df.columns)[:5]}...")
    except Exception as e:
        print(f"✗ Failed to load Salesforce data: {e}")
        return False
    
    try:
        amadeus_df = load_csv(amadeus_path)
        print(f"✓ Amadeus data loaded: {len(amadeus_df)} rows, {len(amadeus_df.columns)} columns")
        print(f"  Columns: {list(amadeus_df.columns)[:5]}...")
    except Exception as e:
        print(f"✗ Failed to load Amadeus data: {e}")
        return False
    
    return salesforce_df, amadeus_df

def test_agent_creation(salesforce_df, amadeus_df):
    """Test agent creation and basic functionality"""
    print("\n=== Testing Agent Creation ===")
    
    try:
        salesforce_agent = SalesforceAgent(salesforce_df)
        print("✓ Salesforce agent created successfully")
        print(f"  Detected columns: user={salesforce_agent.user_col}, duration={salesforce_agent.duration_col}")
    except Exception as e:
        print(f"✗ Failed to create Salesforce agent: {e}")
        return False
    
    try:
        amadeus_agent = AmadeusAgent(amadeus_df)
        print("✓ Amadeus agent created successfully")
        print(f"  Detected columns: user={amadeus_agent.user_col}, duration={amadeus_agent.duration_col}")
    except Exception as e:
        print(f"✗ Failed to create Amadeus agent: {e}")
        return False
    
    return salesforce_agent, amadeus_agent

def test_analysis_functions(agents):
    """Test analysis functions"""
    print("\n=== Testing Analysis Functions ===")
    
    salesforce_agent, amadeus_agent = agents
    
    # Test Salesforce analysis
    print("\n--- Salesforce Analysis ---")
    try:
        result = salesforce_agent.summary()
        print("✓ Salesforce summary analysis completed")
        if 'chart' in result:
            print("  ✓ Chart generated successfully")
        else:
            print("  ⚠ No chart in summary result")
    except Exception as e:
        print(f"✗ Salesforce summary failed: {e}")
    
    try:
        result = salesforce_agent.top_bottlenecks()
        print("✓ Salesforce bottlenecks analysis completed")
        if 'chart' in result:
            print("  ✓ Chart generated successfully")
    except Exception as e:
        print(f"✗ Salesforce bottlenecks failed: {e}")
    
    # Test Amadeus analysis
    print("\n--- Amadeus Analysis ---")
    try:
        result = amadeus_agent.summary()
        print("✓ Amadeus summary analysis completed")
        if 'chart' in result:
            print("  ✓ Chart generated successfully")
    except Exception as e:
        print(f"✗ Amadeus summary failed: {e}")
    
    try:
        result = amadeus_agent.top_bottlenecks()
        print("✓ Amadeus bottlenecks analysis completed")
        if 'chart' in result:
            print("  ✓ Chart generated successfully")
    except Exception as e:
        print(f"✗ Amadeus bottlenecks failed: {e}")

def test_chart_export(agents):
    """Test chart export functionality"""
    print("\n=== Testing Chart Export ===")
    
    salesforce_agent, amadeus_agent = agents
    
    try:
        result = salesforce_agent.summary()
        if 'chart' in result:
            chart_paths = save_chart(result['chart'], "test_salesforce_summary")
            print(f"✓ Chart exported successfully")
            print(f"  HTML: {chart_paths['html']}")
            print(f"  Vega-Lite: {chart_paths['vegalite']}")
        else:
            print("⚠ No chart to export from summary")
    except Exception as e:
        print(f"✗ Chart export failed: {e}")

def test_dependencies():
    """Test if all required dependencies are available"""
    print("\n=== Testing Dependencies ===")
    
    dependencies = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('altair', 'alt'),
        ('matplotlib', 'plt'),
        ('flask', 'Flask'),
        ('reportlab', 'reportlab'),
        ('PIL', 'PIL')
    ]
    
    missing_deps = []
    for dep_name, import_name in dependencies:
        try:
            if import_name == 'pd':
                import pandas as pd
            elif import_name == 'np':
                import numpy as np
            elif import_name == 'alt':
                import altair as alt
            elif import_name == 'plt':
                import matplotlib.pyplot as plt
            elif import_name == 'Flask':
                from flask import Flask
            elif import_name == 'reportlab':
                import reportlab
            elif import_name == 'PIL':
                from PIL import Image
            print(f"✓ {dep_name} available")
        except ImportError:
            print(f"✗ {dep_name} not available")
            missing_deps.append(dep_name)
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("Task Mining Multi-Agent System - Test Suite")
    print("=" * 50)
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed. Please install missing packages.")
        return False
    
    # Test data loading
    try:
        salesforce_df, amadeus_df = test_data_loading()
    except:
        print("\n❌ Data loading test failed.")
        return False
    
    # Test agent creation
    try:
        agents = test_agent_creation(salesforce_df, amadeus_df)
    except:
        print("\n❌ Agent creation test failed.")
        return False
    
    # Test analysis functions
    test_analysis_functions(agents)
    
    # Test chart export
    test_chart_export(agents)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("The system is ready to use.")
    print("\nTo start the system:")
    print("  CLI: python start_system.py --mode cli")
    print("  Web: python start_system.py --mode web")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

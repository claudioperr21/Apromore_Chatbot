#!/usr/bin/env python3
"""
Task Mining Multi-Agent System - CLI Only Version
This version doesn't require Node.js and runs only the Python components.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_requirements():
    """Check if Python requirements are met"""
    print("🐍 Checking Python requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
    
    # Check required packages
    required_packages = [
        'pandas', 'altair', 'flask', 'flask_cors', 'matplotlib', 
        'reportlab', 'pillow', 'numpy', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("✅ All required packages available")
    
    return True

def check_data_files():
    """Check if data files exist"""
    print("📊 Checking data files...")
    
    data_dir = Path("Data Sources")
    if not data_dir.exists():
        print("❌ Data Sources directory not found")
        return False
    
    required_files = [
        "SalesforceOffice_synthetic_varied_100users_V1.csv",
        "amadeus-demo-full-no-fields.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Data files found")
    return True

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    template_file = Path("env.template")
    
    if not env_file.exists():
        if template_file.exists():
            print("📝 Creating .env file from template...")
            with open(template_file, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created")
        else:
            print("❌ env.template not found")
            return False
    else:
        print("✅ .env file exists")
    
    return True

def test_system():
    """Test the system"""
    print("🧪 Testing system...")
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ System test passed")
            return True
        else:
            print(f"❌ System test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False

def run_cli():
    """Run the CLI version"""
    print("🚀 Starting CLI mode...")
    print("=" * 50)
    print("Task Mining Multi-Agent System - CLI Mode")
    print("=" * 50)
    print("Available commands:")
    print("  - summary: Get dataset overview")
    print("  - bottlenecks: Find process bottlenecks")
    print("  - team performance: Analyze team efficiency")
    print("  - app usage: Analyze application usage")
    print("  - recommendations: Get managerial insights")
    print("  - help: Show this help")
    print("  - exit: Quit the system")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI failed: {e}")
    except KeyboardInterrupt:
        print("\n👋 CLI stopped by user")

def run_backend_only():
    """Run only the backend API"""
    print("🚀 Starting backend API server...")
    print("Backend will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET /api/health")
    print("  - GET /api/datasets")
    print("  - POST /api/analyze/{dataset}")
    print("  - GET /api/chart/{dataset}/{chart_type}")
    print("  - POST /api/export/pdf")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, "app.py"], cwd="backend", check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed: {e}")
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")

def main():
    """Main function"""
    print("🎯 Task Mining Multi-Agent System - CLI Only")
    print("=" * 50)
    
    # Check requirements
    if not check_python_requirements():
        return False
    
    if not check_data_files():
        return False
    
    if not setup_environment():
        return False
    
    if not test_system():
        return False
    
    print("\n✅ System ready!")
    print("\nChoose running mode:")
    print("1. CLI Mode (Interactive command line)")
    print("2. Backend API Only (REST API server)")
    print("3. Test System (Run tests and exit)")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            run_cli()
            break
        elif choice == "2":
            run_backend_only()
            break
        elif choice == "3":
            print("🧪 Running system tests...")
            test_system()
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 System completed successfully!")

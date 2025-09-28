#!/usr/bin/env python3
"""
Complete setup script for Task Mining Multi-Agent System
This script handles everything from environment setup to running the system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🎯 Task Mining Multi-Agent System Setup")
    print("=" * 50)

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    template_file = Path("env.template")
    
    if not env_file.exists():
        if template_file.exists():
            shutil.copy(template_file, env_file)
            print("✅ Created .env file from template")
            print("📝 Please edit .env file with your settings")
        else:
            print("❌ env.template not found")
            return False
    else:
        print("✅ .env file already exists")
    
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
        print(f"❌ Missing data files: {', '.join(missing_files)}")
        return False
    
    print("✅ All data files found")
    return True

def setup_frontend():
    """Setup React frontend"""
    print("⚛️ Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if Node.js is installed
    try:
        result = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ Node.js found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Node.js not found. Frontend will be skipped.")
        print("   You can still use the CLI mode or install Node.js later.")
        return True  # Don't fail the setup, just skip frontend
    
    # Check if npm is available
    try:
        result = subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ npm found: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ npm not found. Frontend setup will be skipped.")
        return True  # Don't fail the setup
    
    # Install npm dependencies
    try:
        print("📦 Installing frontend dependencies...")
        result = subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, capture_output=True, text=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to install frontend dependencies: {e}")
        print("   You can still use the CLI mode.")
        return True  # Don't fail the setup

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

def create_run_scripts():
    """Create convenient run scripts"""
    print("📝 Creating run scripts...")
    
    # Create Windows batch file
    batch_content = '''@echo off
echo Starting Task Mining System...
python run_system.py
pause
'''
    with open("start_system.bat", "w") as f:
        f.write(batch_content)
    
    # Create Unix shell script
    shell_content = '''#!/bin/bash
echo "Starting Task Mining System..."
python3 run_system.py
'''
    with open("start_system.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable
    try:
        os.chmod("start_system.sh", 0o755)
    except:
        pass
    
    print("✅ Run scripts created")
    return True

def main():
    """Main setup function"""
    print_header()
    
    steps = [
        ("Python Version", check_python),
        ("Environment Setup", setup_environment),
        ("Data Files", check_data_files),
        ("Python Dependencies", install_requirements),
        ("Frontend Setup", setup_frontend),
        ("System Test", test_system),
        ("Run Scripts", create_run_scripts)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if not step_func():
            failed_steps.append(step_name)
            print(f"❌ {step_name} failed")
        else:
            print(f"✅ {step_name} completed")
    
    print("\n" + "=" * 50)
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease fix the errors and run setup again")
        return False
    else:
        print("🎉 Setup completed successfully!")
        print("\nTo run the system:")
        print("  • Python: python run_system.py")
        print("  • Windows: start_system.bat")
        print("  • Unix/Mac: ./start_system.sh")
        print("\nThe system will be available at:")
        print("  • Web Interface: http://localhost:3000")
        print("  • Backend API: http://localhost:5000")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

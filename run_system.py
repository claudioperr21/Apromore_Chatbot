#!/usr/bin/env python3
"""
Task Mining Multi-Agent System - Main Runner
This script provides the easiest way to run the entire system.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_requirements():
    """Check if required packages are installed"""
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
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalling missing packages...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("✅ All required packages are installed")
    
    return True

def check_data_files():
    """Check if CSV data files exist"""
    data_dir = Path("Data Sources")
    
    if not data_dir.exists():
        print("❌ Data Sources directory not found")
        return False
    
    salesforce_file = data_dir / "SalesforceOffice_synthetic_varied_100users_V1.csv"
    amadeus_file = data_dir / "amadeus-demo-full-no-fields.csv"
    
    if not salesforce_file.exists():
        print(f"❌ Salesforce file not found: {salesforce_file}")
        return False
    
    if not amadeus_file.exists():
        print(f"❌ Amadeus file not found: {amadeus_file}")
        return False
    
    print("✅ Data files found")
    return True

def setup_environment():
    """Setup environment file if it doesn't exist"""
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

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting Flask backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("🚀 Starting React frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Check if Node.js is available
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js not found. Please install Node.js to use the web interface.")
        print("   You can still use the CLI mode.")
        return None
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js to use the web interface.")
        print("   You can still use the CLI mode.")
        return None
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return None
    
    try:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for frontend to start
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ Frontend started on http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def run_cli_mode():
    """Run the CLI version"""
    print("🚀 Starting CLI mode...")
    try:
        subprocess.run([sys.executable, "task_mining_multi_agent.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI mode failed: {e}")
    except KeyboardInterrupt:
        print("\n👋 CLI mode stopped by user")

def main():
    print("🎯 Task Mining Multi-Agent System")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        return
    
    if not check_requirements():
        return
    
    if not check_data_files():
        return
    
    if not setup_environment():
        return
    
    # Ask user for mode
    print("\nChoose running mode:")
    print("1. Web Interface (Backend + Frontend)")
    print("2. CLI Mode (Command Line Interface)")
    print("3. Test System")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Web Interface Mode
            print("\n🌐 Starting Web Interface...")
            
            backend_process = start_backend()
            if not backend_process:
                print("❌ Failed to start backend")
                return
            
            frontend_process = start_frontend()
            if not frontend_process:
                print("❌ Failed to start frontend")
                backend_process.terminate()
                return
            
            print("\n" + "=" * 50)
            print("🎉 Task Mining Analysis System is ready!")
            print("=" * 50)
            print("📊 Frontend: http://localhost:3000")
            print("🔧 Backend API: http://localhost:5000")
            print("📚 API Health: http://localhost:5000/api/health")
            print("\nPress Ctrl+C to stop all services")
            
            # Open browser
            try:
                webbrowser.open("http://localhost:3000")
            except:
                pass
            
            # Wait for user interruption
            try:
                while True:
                    time.sleep(1)
                    
                    if backend_process.poll() is not None:
                        print("❌ Backend process stopped unexpectedly")
                        break
                    
                    if frontend_process.poll() is not None:
                        print("❌ Frontend process stopped unexpectedly")
                        break
                        
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping services...")
                
            finally:
                if backend_process:
                    backend_process.terminate()
                    print("✅ Backend stopped")
                
                if frontend_process:
                    frontend_process.terminate()
                    print("✅ Frontend stopped")
                
                print("👋 All services stopped")
            break
            
        elif choice == "2":
            # CLI Mode
            run_cli_mode()
            break
            
        elif choice == "3":
            # Test System
            print("\n🧪 Running system tests...")
            try:
                subprocess.run([sys.executable, "test_system.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Tests failed: {e}")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

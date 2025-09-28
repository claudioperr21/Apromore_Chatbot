#!/usr/bin/env python3
"""
Task Mining Multi-Agent System Startup Script

This script provides an easy way to start the entire system:
1. CLI version for direct interaction
2. Web interface (backend + frontend)

Usage:
    python start_system.py [--mode cli|web] [--port 5000]
"""

import argparse
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'altair', 'flask', 'flask_cors', 'matplotlib', 
        'reportlab', 'pillow', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def start_cli():
    """Start the CLI version"""
    print("Starting Task Mining Multi-Agent CLI...")
    try:
        subprocess.run([sys.executable, "task_mining_multi_agent.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting CLI: {e}")
    except KeyboardInterrupt:
        print("\nCLI stopped by user")

def start_backend():
    """Start the Flask backend server"""
    print("Starting Flask backend server...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("Error: backend directory not found")
        return None
    
    try:
        # Change to backend directory and start Flask app
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ Backend server started successfully on http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Error starting backend server: {stderr}")
            return None
            
    except Exception as e:
        print(f"Error starting backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("Starting React frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("Error: frontend directory not found")
        return None
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing frontend dependencies: {e}")
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
        time.sleep(5)
        
        if process.poll() is None:
            print("✓ Frontend started successfully on http://localhost:3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"Error starting frontend: {stderr}")
            return None
            
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return None

def start_web_interface():
    """Start the complete web interface (backend + frontend)"""
    print("Starting Task Mining Multi-Agent Web Interface...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            return
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            backend_process.terminate()
            return
        
        print("\n" + "=" * 50)
        print("🎉 Task Mining Analysis System is ready!")
        print("=" * 50)
        print("📊 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:5000")
        print("📚 API Docs: http://localhost:5000/api/health")
        print("\nPress Ctrl+C to stop all services")
        
        # Open browser
        try:
            webbrowser.open("http://localhost:3000")
        except:
            pass
        
        # Wait for user interruption
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        
    finally:
        # Cleanup
        if backend_process:
            backend_process.terminate()
            print("✓ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✓ Frontend stopped")
        
        print("All services stopped.")

def main():
    parser = argparse.ArgumentParser(
        description="Task Mining Multi-Agent System Startup Script"
    )
    parser.add_argument(
        "--mode", 
        choices=["cli", "web"], 
        default="web",
        help="Startup mode: cli for command line interface, web for full web interface"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Backend server port (default: 5000)"
    )
    
    args = parser.parse_args()
    
    print("Task Mining Multi-Agent System")
    print("=" * 40)
    
    if args.mode == "cli":
        start_cli()
    else:
        start_web_interface()

if __name__ == "__main__":
    main()

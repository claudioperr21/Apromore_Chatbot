#!/usr/bin/env python3
"""
Setup script for Task Mining Chat System
Installs OpenAI and sets up the chat interface
"""

import subprocess
import sys
import os

def install_openai():
    """Install OpenAI package"""
    print("Installing OpenAI package...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
        print("✅ OpenAI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install OpenAI: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has OpenAI key"""
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Please copy env.template to .env and add your OpenAI API key")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "SECRET_KEY=sk-proj-" in content:
            print("✅ OpenAI API key found in .env file")
            return True
        else:
            print("⚠️ OpenAI API key not found in .env file")
            print("Please add your OpenAI API key to the .env file")
            return False

def main():
    print("Task Mining Chat System Setup")
    print("=" * 40)
    
    # Install OpenAI
    if not install_openai():
        return False
    
    # Check .env file
    if not check_env_file():
        print("\nTo use AI chat features:")
        print("1. Copy env.template to .env")
        print("2. Add your OpenAI API key to the .env file")
        print("3. Run: python task_mining_chat.py")
        return False
    
    print("\n✅ Setup complete!")
    print("You can now run: python task_mining_chat.py")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 Chat system ready!")

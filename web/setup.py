import os
import subprocess
import sys

def setup_project():
    print("Setting up Agentic Workflow Engine...")
    
    # Install dependencies
    print("\nInstalling dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create directories
    directories = ['screenshots', 'workflows', 'data', 'static', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created {directory}/")
    
    print("\n✅ Setup complete! Run: python app.py")

if __name__ == "__main__":
    setup_project()
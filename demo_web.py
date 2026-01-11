#!/usr/bin/env python3
"""
KGCompass Web Interface Demo
Simple demo script for testing basic web interface functionality
"""

import os
import time
import subprocess
import threading
from pathlib import Path

def check_dependencies():
    """Check required dependencies"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        try:
            version = flask.__version__
        except AttributeError:
            # Flask 3.1+ removed __version__
            import importlib.metadata
            version = importlib.metadata.version("flask")
        print(f"✅ Flask: {version}")
    except ImportError:
        print("❌ Flask is not installed")
        return False
    
    try:
        import flask_socketio
        try:
            version = flask_socketio.__version__
        except AttributeError:
            import importlib.metadata
            version = importlib.metadata.version("flask-socketio")
        print(f"✅ Flask-SocketIO: {version}")
    except ImportError:
        print("❌ Flask-SocketIO is not installed")
        return False
    
    return True

def check_files():
    """Check required files"""
    print("📁 Checking files...")
    
    required_files = [
        "app.py",
        "templates/index.html",
        "static/css/style.css",
        "static/js/app.js",
        "requirements_web.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Exists: {file_path}")
    
    return len(missing_files) == 0

def create_demo_output():
    """Create demo output directory and files"""
    print("📁 Creating demo output...")
    
    output_dir = Path("web_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Create a sample task output
    demo_task_dir = output_dir / "demo-task-123"
    demo_task_dir.mkdir(exist_ok=True)
    
    # Create sample patch file
    patch_content = """--- a/example.py
+++ b/example.py
@@ -10,6 +10,9 @@ def example_function():
     if condition:
         return True
 
+    # Fix: Add proper error handling
+    if not isinstance(data, list):
+        raise ValueError("Data must be a list")
+
     return False
"""
    
    with open(demo_task_dir / "demo_patch.diff", "w") as f:
        f.write(patch_content)
    
    print(f"✅ Created demo output: {demo_task_dir}")

def run_quick_test():
    """Run quick test"""
    print("\n🧪 Running quick test...")
    
    try:
        # Test importing app module
        import app
        print("✅ app.py can be imported normally")
        
        # Test basic configuration
        if hasattr(app, 'SUPPORTED_REPOS'):
            repo_count = len(app.SUPPORTED_REPOS)
            print(f"✅ Supports {repo_count} repositories")
        
        if hasattr(app, 'EXAMPLE_ISSUES'):
            example_count = sum(len(issues) for issues in app.EXAMPLE_ISSUES.values())
            print(f"✅ Contains {example_count} example Issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def start_demo_server():
    """Start demo server"""
    print("\n🚀 Starting demo server...")
    print("📡 Access URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop server")
    print("=" * 50)
    
    try:
        import app
        app.socketio.run(app.app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server startup failed: {e}")

def main():
    """Main function"""
    print("🎯 KGCompass Web Interface Demo")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed, please run:")
        print("pip install -r requirements_web.txt")
        return
    
    # Check files
    if not check_files():
        print("\n❌ File check failed, please ensure all required files are created")
        return
    
    # Create demo output
    create_demo_output()
    
    # Run tests
    if not run_quick_test():
        print("\n❌ Quick test failed")
        return
    
    print("\n✅ All checks passed!")
    
    # Ask if user wants to start server
    response = input("\nStart demo server? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        start_demo_server()
    else:
        print("\n💡 Manual startup commands:")
        print("python3 app.py")
        print("or:")
        print("./start_web.sh")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
KGCompass Web Interface
A web interface for displaying and executing KGCompass software repair workflows
"""

import os
import json
import subprocess
import threading
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kgcompass-web-interface'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to store task status
active_tasks: Dict[str, Dict] = {}
task_logs: Dict[str, List[str]] = {}

# Supported repository list (extracted from project)
SUPPORTED_REPOS = {
    "astropy__astropy": {
        "name": "astropy/astropy",
        "description": "Python library for astronomy and astrophysics",
        "language": "Python",
        "stars": "4.3k"
    },
    "django__django": {
        "name": "django/django", 
        "description": "High-level Python web framework",
        "language": "Python",
        "stars": "79k"
    },
    "matplotlib__matplotlib": {
        "name": "matplotlib/matplotlib",
        "description": "Python 2D plotting library",
        "language": "Python", 
        "stars": "19k"
    },
    "mwaskom__seaborn": {
        "name": "mwaskom/seaborn",
        "description": "Statistical data visualization library based on matplotlib",
        "language": "Python",
        "stars": "12k"
    },
    "psf__requests": {
        "name": "psf/requests",
        "description": "Elegant and simple Python HTTP library",
        "language": "Python",
        "stars": "52k"
    },
    "pallets__flask": {
        "name": "pallets/flask",
        "description": "Lightweight Python web framework",
        "language": "Python",
        "stars": "67k"
    },
    "pydata__xarray": {
        "name": "pydata/xarray",
        "description": "N-D labeled arrays and datasets library",
        "language": "Python",
        "stars": "3.6k"
    },
    "pylint-dev__pylint": {
        "name": "pylint-dev/pylint",
        "description": "Python code static analysis tool",
        "language": "Python",
        "stars": "5.2k"
    },
    "pytest-dev__pytest": {
        "name": "pytest-dev/pytest",
        "description": "Python testing framework",
        "language": "Python",
        "stars": "11k"
    },
    "scikit-learn__scikit-learn": {
        "name": "scikit-learn/scikit-learn", 
        "description": "Python machine learning library",
        "language": "Python",
        "stars": "59k"
    },
    "sphinx-doc__sphinx": {
        "name": "sphinx-doc/sphinx",
        "description": "Python documentation generation tool",
        "language": "Python",
        "stars": "6.4k"
    },
    "sympy__sympy": {
        "name": "sympy/sympy",
        "description": "Python symbolic mathematics library",
        "language": "Python",
        "stars": "12k"
    }
}

# Example Issue IDs
EXAMPLE_ISSUES = {
    "astropy__astropy": ["astropy__astropy-12907", "astropy__astropy-13033", "astropy__astropy-13236"],
    "django__django": ["django__django-11001", "django__django-11179", "django__django-11283"],
    "matplotlib__matplotlib": ["matplotlib__matplotlib-13989", "matplotlib__matplotlib-14471"],
    "scikit-learn__scikit-learn": ["scikit-learn__scikit-learn-13497", "scikit-learn__scikit-learn-13779"],
    "sympy__sympy": ["sympy__sympy-15308", "sympy__sympy-15346", "sympy__sympy-15678"]
}

class RepairTaskManager:
    """Repair task manager"""
    
    def __init__(self):
        self.output_dir = Path("web_outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def start_repair_task(self, task_id: str, instance_id: str, repo_key: str) -> bool:
        """Start repair task"""
        try:
            # Validate input
            if repo_key not in SUPPORTED_REPOS:
                raise ValueError(f"Unsupported repository: {repo_key}")
            
            # Create task status
            active_tasks[task_id] = {
                'instance_id': instance_id,
                'repo_key': repo_key,
                'repo_name': SUPPORTED_REPOS[repo_key]['name'],
                'status': 'initializing',
                'start_time': datetime.now().isoformat(),
                'current_step': 'prepare',
                'progress': 0,
                'output_dir': str(self.output_dir / task_id)
            }
            task_logs[task_id] = []
            
            # Create output directory
            task_output_dir = self.output_dir / task_id
            task_output_dir.mkdir(exist_ok=True)
            
            # Execute repair task in a new thread
            thread = threading.Thread(
                target=self._execute_repair_pipeline,
                args=(task_id, instance_id, repo_key, task_output_dir)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            if task_id in active_tasks:
                active_tasks[task_id]['status'] = 'error'
                active_tasks[task_id]['error'] = str(e)
            self._log_message(task_id, f"❌ Task startup failed: {str(e)}")
            return False
    
    def _execute_repair_pipeline(self, task_id: str, instance_id: str, repo_key: str, output_dir: Path):
        """Execute the actual repair pipeline in Docker container"""
        try:
            self._log_message(task_id, f"🚀 Starting repair process for {instance_id}")
            self._log_message(task_id, f"📋 Repository: {SUPPORTED_REPOS[repo_key]['name']}")
            
            # Check Docker environment
            self._update_task_status(task_id, 'checking_docker', 5, "🐳 Checking Docker environment...")
            
            # Check if docker-compose is running
            result = subprocess.run([
                "docker-compose", "ps", "-q", "app"
            ], capture_output=True, text=True, cwd=str(Path.cwd()))
            
            if result.returncode != 0 or not result.stdout.strip():
                self._log_message(task_id, "🐳 Starting Docker services...")
                # Start docker-compose services
                start_result = subprocess.run([
                    "docker-compose", "up", "-d", "--build"
                ], capture_output=True, text=True, cwd=str(Path.cwd()))
                
                if start_result.returncode != 0:
                    raise Exception(f"Docker service startup failed: {start_result.stderr}")
                
                self._log_message(task_id, "✅ Docker services started")
                
                # Wait for services to fully start
                import time
                time.sleep(10)
            else:
                self._log_message(task_id, "✅ Docker services already running")
            
            # Set output directory mapping
            # Path in Docker container should correspond to host path
            container_output_dir = f"/opt/KGCompass/web_outputs/{task_id}"
            
            # Execute repair command in container
            self._update_task_status(task_id, 'docker_repair', 10, "🚀 Executing repair in container...")
            self._log_message(task_id, f"🐳 Executing in Docker container: run_repair.sh {instance_id}")
            
            # Build docker-compose exec command
            docker_cmd = [
                "docker-compose", "exec", "-T", "app", 
                "bash", "run_repair.sh", instance_id
            ]
            
            # Set environment variables to redirect output to our web_outputs
            env = os.environ.copy()
            env['DOCKER_OUTPUT_DIR'] = container_output_dir
            
            # Execute repair command and get output in real-time
            self._log_message(task_id, "🔄 Starting repair process...")
            
            process = subprocess.Popen(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(Path.cwd()),
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read and send logs in real-time
            step_progress = {
                'KG-based Bug Location': 30,
                'LLM-based Bug Location': 50, 
                'Merge and Fix Bug Locations': 70,
                'Final Patch Generation': 90
            }
            
            current_progress = 10
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    self._log_message(task_id, line)
                    
                    # Update progress based on output content
                    for step_name, progress in step_progress.items():
                        if step_name in line and progress > current_progress:
                            current_progress = progress
                            if 'KG-based' in step_name:
                                self._update_task_status(task_id, 'kg_mining', progress, "🔍 Mining knowledge graph...")
                            elif 'LLM-based' in step_name:
                                self._update_task_status(task_id, 'fault_localization', progress, "🎯 LLM fault localization...")
                            elif 'Merge' in step_name:
                                self._update_task_status(task_id, 'merge_localization', progress, "🔗 Merging localization results...")
                            elif 'Patch Generation' in step_name:
                                self._update_task_status(task_id, 'patch_generation', progress, "⚡ Generating repair patch...")
                            break
            
            # Wait for process to complete
            return_code = process.poll()
            
            if return_code != 0:
                raise Exception(f"Repair process execution failed, return code: {return_code}")
            
            # Find generated patch file
            self._update_task_status(task_id, 'collecting_results', 95, "📁 Collecting repair results...")
            
            # Find patch file in container
            find_cmd = [
                "docker-compose", "exec", "-T", "app",
                "find", f"/opt/KGCompass/runs", "-name", f"{instance_id}.patch", "-type", "f"
            ]
            
            find_result = subprocess.run(find_cmd, capture_output=True, text=True, cwd=str(Path.cwd()))
            
            if find_result.returncode == 0 and find_result.stdout.strip():
                container_patch_path = find_result.stdout.strip()
                self._log_message(task_id, f"✅ Found patch file in container: {container_patch_path}")
                
                # Copy patch file from container to host
                host_patch_path = output_dir / f"{instance_id}_patch.diff"
                copy_cmd = [
                    "docker", "cp", 
                    f"kgcompass-app:{container_patch_path}",
                    str(host_patch_path)
                ]
                
                copy_result = subprocess.run(copy_cmd, capture_output=True, text=True)
                
                if copy_result.returncode == 0:
                    self._log_message(task_id, f"📄 Patch copied to: {host_patch_path}")
                    
                    # Read and display patch content
                    try:
                        with open(host_patch_path, 'r', encoding='utf-8') as f:
                            patch_content = f.read()
                        self._log_message(task_id, f"📄 Patch content preview:")
                        # Show first 10 lines
                        preview_lines = patch_content.split('\n')[:10]
                        for line in preview_lines:
                            self._log_message(task_id, f"  {line}")
                        patch_lines_count = len(patch_content.split('\n'))
                        if patch_lines_count > 10:
                            self._log_message(task_id, f"  ... (total {patch_lines_count} lines)")
                    except Exception as e:
                        self._log_message(task_id, f"⚠️ Unable to read patch content: {e}")
                    
                    patch_file_path = str(host_patch_path)
                else:
                    self._log_message(task_id, f"⚠️ Failed to copy patch file: {copy_result.stderr}")
                    patch_file_path = None
            else:
                self._log_message(task_id, "⚠️ Patch file not found")
                patch_file_path = None
            
            # Generate repair report
            report = {
                "instance_id": instance_id,
                "repo_identifier": repo_key,
                "repo_name": SUPPORTED_REPOS[repo_key]['name'],
                "repair_successful": patch_file_path is not None,
                "patch_file": patch_file_path,
                "docker_execution": True,
                "timestamp": datetime.now().isoformat()
            }
            
            report_file = output_dir / f"{instance_id}_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Task completed
            self._update_task_status(task_id, 'completed', 100, "✅ Repair completed!")
            self._log_message(task_id, f"🎉 {instance_id} repair completed!")
            
            active_tasks[task_id].update({
                'end_time': datetime.now().isoformat(),
                'patch_file': patch_file_path,
                'repair_report': str(report_file)
            })
            
        except Exception as e:
            self._update_task_status(task_id, 'error', 0, f"❌ Error: {str(e)}")
            self._log_message(task_id, f"❌ Repair failed: {str(e)}")
            active_tasks[task_id]['error'] = str(e)
    
    
    
    def _update_task_status(self, task_id: str, status: str, progress: int, message: str):
        """Update task status"""
        if task_id in active_tasks:
            active_tasks[task_id].update({
                'status': status,
                'progress': progress,
                'current_step': message
            })
            
            socketio.emit('task_update', {
                'task_id': task_id,
                'status': status,
                'progress': progress,
                'message': message
            })
    
    def _log_message(self, task_id: str, message: str):
        """Log a message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        if task_id not in task_logs:
            task_logs[task_id] = []
        task_logs[task_id].append(log_entry)
        
        socketio.emit('task_log', {
            'task_id': task_id,
            'message': log_entry
        })

# Global task manager
task_manager = RepairTaskManager()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', 
                         repos=SUPPORTED_REPOS,
                         examples=EXAMPLE_ISSUES)

@app.route('/api/start_repair', methods=['POST'])
def start_repair():
    """Start repair task"""
    data = request.get_json()
    instance_id = data.get('instance_id', '').strip()
    repo_key = data.get('repo_key', '').strip()
    
    if not instance_id or not repo_key:
        return jsonify({'success': False, 'error': 'Please fill in complete instance ID and repository'}), 400
    
    if repo_key not in SUPPORTED_REPOS:
        return jsonify({'success': False, 'error': f'Unsupported repository: {repo_key}'}), 400
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Start task
    success = task_manager.start_repair_task(task_id, instance_id, repo_key)
    
    if success:
        return jsonify({
            'success': True, 
            'task_id': task_id,
            'message': 'Repair task started'
        })
    else:
        return jsonify({
            'success': False, 
            'error': 'Task startup failed'
        }), 500

@app.route('/api/task_status/<task_id>')
def get_task_status(task_id: str):
    """Get task status"""
    if task_id not in active_tasks:
        return jsonify({'success': False, 'error': 'Task does not exist'}), 404
    
    task = active_tasks[task_id]
    logs = task_logs.get(task_id, [])
    
    return jsonify({
        'success': True,
        'task': task,
        'logs': logs[-50:]  # Last 50 log entries
    })

@app.route('/api/download_patch/<task_id>')
def download_patch(task_id: str):
    """Download patch file"""
    if task_id not in active_tasks:
        return jsonify({'error': 'Task does not exist'}), 404
    
    task = active_tasks[task_id]
    if 'patch_file' not in task or not task['patch_file']:
        return jsonify({'error': 'Patch file does not exist'}), 404
    
    patch_file = Path(task['patch_file'])
    if not patch_file.exists():
        return jsonify({'error': 'Patch file not found'}), 404
    
    return send_file(patch_file, as_attachment=True, download_name=f"{task['instance_id']}_patch.diff")

@app.route('/patch_view/<task_id>')
def view_patch(task_id: str):
    """View patch content"""
    if task_id not in active_tasks:
        return "Task does not exist", 404
    
    task = active_tasks[task_id]
    if 'patch_file' not in task or not task['patch_file']:
        return "Patch file does not exist", 404
    
    patch_file = Path(task['patch_file'])
    if not patch_file.exists():
        return "Patch file not found", 404
    
    # Read patch content
    try:
        with open(patch_file, 'r', encoding='utf-8') as f:
            patch_content = f.read()
    except Exception as e:
        return f"Unable to read patch file: {e}", 500
    
    # Parse patch content
    patch_lines = []
    stats = {'additions': 0, 'deletions': 0, 'files': 0}
    file_changes = []
    current_file = None
    
    for line in patch_content.split('\n'):
        line_type = 'patch-line-context'
        
        if line.startswith('---') or line.startswith('+++'):
            line_type = 'patch-line-hunk'
            if line.startswith('---'):
                # New file starts
                if current_file:
                    file_changes.append(current_file)
                current_file = {
                    'filename': line[4:].strip(),
                    'additions': 0,
                    'deletions': 0,
                    'changes': 0
                }
                stats['files'] += 1
        elif line.startswith('@@'):
            line_type = 'patch-line-hunk'
        elif line.startswith('+') and not line.startswith('+++'):
            line_type = 'patch-line-added'
            stats['additions'] += 1
            if current_file:
                current_file['additions'] += 1
                current_file['changes'] += 1
        elif line.startswith('-') and not line.startswith('---'):
            line_type = 'patch-line-removed'
            stats['deletions'] += 1
            if current_file:
                current_file['deletions'] += 1
                current_file['changes'] += 1
        
        patch_lines.append({
            'content': line,
            'type': line_type
        })
    
    if current_file:
        file_changes.append(current_file)
    
    return render_template('patch_view.html',
                         instance_id=task['instance_id'],
                         repo_name=task['repo_name'],
                         patch_content=patch_content,
                         patch_lines=patch_lines,
                         stats=stats,
                         file_changes=file_changes,
                         download_url=f'/api/download_patch/{task_id}')

@socketio.on('connect')
def handle_connect():
    """WebSocket connection handler"""
    emit('connected', {'message': 'Connected to KGCompass repair service'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket disconnection handler"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create output directory
    Path("web_outputs").mkdir(exist_ok=True)
    
    print("🚀 Starting KGCompass Web Interface...")
    print("📡 Access URL: http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 
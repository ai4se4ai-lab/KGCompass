# KGCompass Web Interface

An intuitive web interface that allows users to easily experience KGCompass software repair workflows, view the repair process in real-time, and obtain final patches.

## 🌟 Features

### 🎯 Core Features
- **Intuitive Operation**: Select repositories and enter Issue IDs through the web interface
- **Real-time Feedback**: WebSocket displays repair progress and logs in real-time
- **Process Visualization**: Clearly displays steps such as knowledge graph mining, fault localization, and patch generation
- **Patch Download**: Directly download generated patch files after repair completion
- **Multi-repository Support**: Supports 12 popular Python open-source projects

### 🛠️ Technical Features
- **Responsive Design**: Supports desktop and mobile devices
- **Modern Interface**: Uses Bootstrap 5 and Font Awesome
- **Real-time Communication**: Bidirectional communication based on Socket.IO
- **Elegant Animations**: Smooth transitions and loading animations
- **Error Handling**: Comprehensive error handling and user feedback

## 📋 Supported Repositories

| Repository | Description | Stars |
|------|------|-------|
| astropy/astropy | Python library for astronomy and astrophysics | 4.3k ⭐ |
| django/django | High-level Python web framework | 79k ⭐ |
| matplotlib/matplotlib | Python 2D plotting library | 19k ⭐ |
| mwaskom/seaborn | Statistical data visualization library based on matplotlib | 12k ⭐ |
| psf/requests | Elegant and simple Python HTTP library | 52k ⭐ |
| pallets/flask | Lightweight Python web framework | 67k ⭐ |
| pydata/xarray | N-D labeled arrays and datasets library | 3.6k ⭐ |
| pylint-dev/pylint | Python code static analysis tool | 5.2k ⭐ |
| pytest-dev/pytest | Python testing framework | 11k ⭐ |
| scikit-learn/scikit-learn | Python machine learning library | 59k ⭐ |
| sphinx-doc/sphinx | Python documentation generation tool | 6.4k ⭐ |
| sympy/sympy | Python symbolic mathematics library | 12k ⭐ |

## 🚀 Quick Start

### Method 1: Docker Mode (Recommended - Full Functionality)

Docker mode provides complete KGCompass repair functionality, including Neo4j database and GPU support.

```bash
# Add execute permission to startup script
chmod +x start_web_docker.sh

# Start Docker mode web interface
./start_web_docker.sh
```

**Prerequisites**:
- Docker and Docker Compose
- NVIDIA GPU and Container Toolkit (for GPU acceleration)
- `.env` file configuration (API keys, etc.)

### Method 2: Standalone Mode (Demo Only)

Standalone mode is only for interface demonstration and does not execute actual repair workflows.

```bash
# Add execute permission to startup script
chmod +x start_web.sh

# Start standalone mode web interface
./start_web.sh
```

### Method 3: Manual Startup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements_web.txt

# 3. Start application
python3 app.py
```

### Access Interface

Open browser and visit: **http://localhost:5000**

## 🎮 Usage Guide

### 1. Select Repository
- Select the repository to repair from the dropdown menu
- Interface will display repository description and star count

### 2. Enter Instance ID
- Enter instance ID in SWE-bench format
- Format: `repo__repo-number` (e.g., `astropy__astropy-12907`)

### 3. Use Quick Examples
- Click example buttons on the interface to quickly fill in
- After selecting a repository, relevant examples for that repository will be displayed

### 4. Start Repair
- Click "Start Repair" button to start the process
- View repair progress and detailed logs in real-time

### 5. Get Results
- Download patch files after repair completion
- View repair reports for detailed information

## 🔄 Repair Workflow

### Stage 1: Knowledge Graph Mining (0-30%)
- 📥 Clone repository
- 🔍 Analyze code structure
- 📊 Build knowledge graph
- 🔗 Link issues and code
- 💾 Save KG data

### Stage 2: LLM Fault Localization (30-60%)
- 📖 Analyze problem description
- 🤖 Call Claude model
- 🎯 Locate suspicious files
- 📍 Identify suspicious methods

### Stage 3: Result Fusion (60-80%)
- 🔗 Merge localization results from KG and LLM
- ✅ Optimize localization accuracy

### Stage 4: Patch Generation (80-100%)
- 📝 Prepare repair context
- 🤖 Call Claude API
- ⚡ Generate candidate patches
- ✅ Validate patch syntax

## 📁 Project Structure

```
KGCompass/
├── app.py                      # Flask main application
├── requirements_web.txt        # Web interface dependencies
├── start_web.sh               # Quick startup script
├── templates/
│   └── index.html             # Home page template
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   └── js/
│       └── app.js             # Frontend logic
└── web_outputs/               # Output directory
    └── [task_id]/
        ├── [instance]_patch.diff    # Patch file
        └── [instance]_report.json   # Repair report
```

## 🔧 Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket support
- **Threading**: Asynchronous task processing
- **JSON**: Data exchange format

### Frontend
- **Bootstrap 5**: UI framework
- **Font Awesome**: Icon library
- **Socket.IO**: Real-time communication
- **Vanilla JavaScript**: Frontend logic

### Core Dependencies
```python
Flask==3.0.0
Flask-SocketIO==5.3.6
python-socketio==5.10.0
```

## 📊 Example Usage

### 1. Simple Repair Task
```
Repository: matplotlib/matplotlib
Instance ID: matplotlib__matplotlib-13989
Issue: hist() function does not respect range parameter when density=True
```

### 2. Complex Repair Task
```
Repository: scikit-learn/scikit-learn
Instance ID: scikit-learn__scikit-learn-13497
Issue: Performance optimization problem in machine learning algorithm
```

## 🎯 Advanced Features

### Real-time Logs
- WebSocket connection pushes execution logs in real-time
- Auto-scroll to latest logs
- Support log search and filtering

### Task Management
- Support multiple concurrent repair tasks
- Real-time task status updates
- Task history records

### Error Handling
- Graceful error handling and user feedback
- Detailed error information and solution suggestions
- Automatic retry mechanism

## 🔍 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using the port
lsof -i :5000

# Kill the process (replace PID)
kill -9 <PID>
```

**2. Dependency Installation Failed**
```bash
# Upgrade pip
pip install --upgrade pip

# Clear cache and reinstall
pip cache purge
pip install -r requirements_web.txt
```

**3. WebSocket Connection Failed**
- Check firewall settings
- Ensure port 5000 is accessible
- Check browser WebSocket support

### Debug Mode

Enable verbose logging:
```bash
export FLASK_DEBUG=1
python3 app.py
```

## 🚧 Development Notes

### Local Development Environment

```bash
# Clone repository
git clone <repo-url>
cd KGCompass

# Install development dependencies
pip install -r requirements_web.txt

# Start development server
python3 app.py
```

### Custom Configuration

Modify configuration in `app.py`:
```python
# Change port
socketio.run(app, host='0.0.0.0', port=8080, debug=True)

# Add new repository
SUPPORTED_REPOS['new_repo'] = {
    "name": "owner/repo",
    "description": "Description",
    "language": "Python",
    "stars": "1k"
}
```

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

1. Fork the project
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project uses MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [KGCompass Paper](https://arxiv.org/abs/2503.21710) - Core algorithm
- [SWE-bench](https://www.swebench.com/) - Evaluation dataset
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Font Awesome](https://fontawesome.com/) - Icon library

---

**🚀 Start your software repair journey!**

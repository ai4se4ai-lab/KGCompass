/**
 * KGCompass Web Interface - JavaScript Logic
 * Manages frontend interactions and real-time updates for repair tasks
 */

class KGCompassApp {
    constructor() {
        this.socket = null;
        this.currentTaskId = null;
        this.currentTask = null;
        this.logBuffer = [];
        
        this.initializeApp();
    }

    /**
     * Initialize application
     */
    initializeApp() {
        this.initializeSocket();
        this.setupEventListeners();
        this.setupExampleButtons();
        this.setupRepoSelector();
        
        console.log('🚀 KGCompass App initialized');
    }

    /**
     * Initialize WebSocket connection
     */
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ WebSocket connected');
            this.showNotification('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ WebSocket disconnected');
            this.showNotification('Disconnected from server', 'warning');
        });
        
        this.socket.on('connected', (data) => {
            console.log('📡 Server message:', data.message);
        });
        
        // Task update events
        this.socket.on('task_update', (data) => {
            this.handleTaskUpdate(data);
        });
        
        // Task log events
        this.socket.on('task_log', (data) => {
            this.handleTaskLog(data);
        });
        
        // Task progress events
        this.socket.on('task_progress', (data) => {
            this.handleTaskProgress(data);
        });
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Repair form submission
        const repairForm = document.getElementById('repairForm');
        repairForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startRepairTask();
        });
        
        // Download patch button
        const downloadBtn = document.getElementById('downloadPatchBtn');
        downloadBtn.addEventListener('click', () => {
            this.downloadPatch();
        });
        
        // View report button
        const viewReportBtn = document.getElementById('viewReportBtn');
        viewReportBtn.addEventListener('click', () => {
            this.viewReport();
        });
        
        // New task button
        const newTaskBtn = document.getElementById('newTaskBtn');
        newTaskBtn.addEventListener('click', () => {
            this.resetInterface();
        });
    }

    /**
     * Setup example buttons
     */
    setupExampleButtons() {
        const exampleContainer = document.getElementById('exampleButtons');
        
        // Clear container
        exampleContainer.innerHTML = '';
        
        // Create example buttons for each repository
        Object.keys(window.exampleIssues).forEach(repoKey => {
            const examples = window.exampleIssues[repoKey];
            if (examples && examples.length > 0) {
                // Only show the first example to avoid cluttering the interface
                const exampleId = examples[0];
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-secondary btn-sm example-btn';
                button.textContent = exampleId;
                button.onclick = () => this.fillExample(repoKey, exampleId);
                
                exampleContainer.appendChild(button);
            }
        });
    }

    /**
     * Setup repository selector
     */
    setupRepoSelector() {
        const repoSelect = document.getElementById('repoSelect');
        const repoDescription = document.getElementById('repoDescription');
        
        repoSelect.addEventListener('change', (e) => {
            const selectedRepo = e.target.value;
            const option = e.target.selectedOptions[0];
            
            if (selectedRepo && option) {
                const description = option.dataset.description;
                const stars = option.dataset.stars;
                repoDescription.textContent = `${description} (${stars} ⭐)`;
                
                // Update example buttons
                this.updateExampleButtons(selectedRepo);
            } else {
                repoDescription.textContent = '';
                this.setupExampleButtons(); // Reset to all examples
            }
        });
    }

    /**
     * Update example buttons (only show examples for selected repository)
     */
    updateExampleButtons(repoKey) {
        const exampleContainer = document.getElementById('exampleButtons');
        exampleContainer.innerHTML = '';
        
        const examples = window.exampleIssues[repoKey];
        if (examples && examples.length > 0) {
            examples.forEach(exampleId => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-info btn-sm example-btn';
                button.textContent = exampleId;
                button.onclick = () => this.fillExample(repoKey, exampleId);
                
                exampleContainer.appendChild(button);
            });
        }
    }

    /**
     * Fill example data
     */
    fillExample(repoKey, instanceId) {
        document.getElementById('repoSelect').value = repoKey;
        document.getElementById('instanceId').value = instanceId;
        
        // Trigger repository selector change event
        const repoSelect = document.getElementById('repoSelect');
        const event = new Event('change');
        repoSelect.dispatchEvent(event);
        
        this.showNotification(`Filled example: ${instanceId}`, 'info');
    }

    /**
     * Start repair task
     */
    async startRepairTask() {
        const repoKey = document.getElementById('repoSelect').value;
        const instanceId = document.getElementById('instanceId').value.trim();
        
        if (!repoKey || !instanceId) {
            this.showNotification('Please select a repository and enter instance ID', 'error');
            return;
        }
        
        // Disable submit button
        const submitBtn = document.getElementById('startRepairBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Starting...';
        
        try {
            const response = await fetch('/api/start_repair', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repo_key: repoKey,
                    instance_id: instanceId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentTaskId = result.task_id;
                this.currentTask = {
                    repo_key: repoKey,
                    instance_id: instanceId,
                    repo_name: window.repoInfo[repoKey].name
                };
                
                this.showTaskInterface();
                this.showNotification(result.message, 'success');
                
                // Start polling task status
                this.startStatusPolling();
                
            } else {
                this.showNotification(result.error, 'error');
                this.resetSubmitButton();
            }
            
        } catch (error) {
            console.error('Error starting repair task:', error);
            this.showNotification('Error occurred while starting task', 'error');
            this.resetSubmitButton();
        }
    }

    /**
     * Reset submit button
     */
    resetSubmitButton() {
        const submitBtn = document.getElementById('startRepairBtn');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Start Repair';
    }

    /**
     * Show task interface
     */
    showTaskInterface() {
        document.getElementById('defaultStatus').classList.add('d-none');
        document.getElementById('taskStatus').classList.remove('d-none');
        
        // Fill task information
        document.getElementById('taskRepo').textContent = this.currentTask.repo_name;
        document.getElementById('taskInstance').textContent = this.currentTask.instance_id;
        
        // Reset progress
        this.updateProgress(0, 'Initializing...');
        
        // Clear logs
        document.getElementById('logContent').innerHTML = '';
        this.logBuffer = [];
    }

    /**
     * Start status polling
     */
    startStatusPolling() {
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
        }
        
        // Check status immediately
        this.checkTaskStatus();
        
        // Check status every 2 seconds
        this.statusPollingInterval = setInterval(() => {
            this.checkTaskStatus();
        }, 2000);
    }

    /**
     * Check task status
     */
    async checkTaskStatus() {
        if (!this.currentTaskId) return;
        
        try {
            const response = await fetch(`/api/task_status/${this.currentTaskId}`);
            const result = await response.json();
            
            if (result.success) {
                const task = result.task;
                const logs = result.logs;
                
                // Update progress
                this.updateProgress(task.progress, task.current_step);
                
                // Update logs (only add new logs)
                this.updateLogs(logs);
                
                // Check if task is completed
                if (task.status === 'completed') {
                    this.handleTaskCompletion(task);
                } else if (task.status === 'error') {
                    this.handleTaskError(task);
                }
                
            } else {
                console.error('Failed to get task status:', result.error);
            }
            
        } catch (error) {
            console.error('Error checking task status:', error);
        }
    }

    /**
     * Handle task update
     */
    handleTaskUpdate(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        this.updateProgress(data.progress, data.message);
        
        // Update progress bar color
        const progressBar = document.getElementById('progressBar');
        if (data.status === 'completed') {
            progressBar.className = 'progress-bar bg-success';
        } else if (data.status === 'error') {
            progressBar.className = 'progress-bar bg-danger';
        }
    }

    /**
     * Handle task log
     */
    handleTaskLog(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        this.addLogMessage(data.message);
    }

    /**
     * Handle task progress
     */
    handleTaskProgress(data) {
        if (data.task_id !== this.currentTaskId) return;
        
        this.updateProgress(data.progress, data.step_detail);
    }

    /**
     * Update progress
     */
    updateProgress(progress, message) {
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        const currentStep = document.getElementById('currentStep');
        
        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${progress}%`;
        currentStep.textContent = message;
    }

    /**
     * Update logs
     */
    updateLogs(logs) {
        const logContent = document.getElementById('logContent');
        
        // Check for new logs
        logs.forEach(log => {
            if (!this.logBuffer.includes(log)) {
                this.logBuffer.push(log);
                this.addLogMessage(log);
            }
        });
    }

    /**
     * Add log message
     */
    addLogMessage(message) {
        const logContent = document.getElementById('logContent');
        const logContainer = document.getElementById('logContainer');
        
        const logLine = document.createElement('div');
        logLine.textContent = message;
        logLine.className = 'fade-in';
        
        logContent.appendChild(logLine);
        
        // Auto scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    /**
     * Handle task completion
     */
    handleTaskCompletion(task) {
        // Stop status polling
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
        }
        
        // Show completion actions
        document.getElementById('completedActions').classList.remove('d-none');
        
        // Reset submit button
        this.resetSubmitButton();
        
        this.showNotification('🎉 Repair task completed!', 'success');
    }

    /**
     * Handle task error
     */
    handleTaskError(task) {
        // Stop status polling
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
        }
        
        // Reset submit button
        this.resetSubmitButton();
        
        const errorMsg = task.error || 'Repair task execution failed';
        this.showNotification(`❌ ${errorMsg}`, 'error');
    }

    /**
     * Download patch
     */
    downloadPatch() {
        if (!this.currentTaskId) return;
        
        const downloadUrl = `/api/download_patch/${this.currentTaskId}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${this.currentTask.instance_id}_patch.diff`;
        link.click();
        
        this.showNotification('Starting patch file download', 'info');
    }

    /**
     * View report
     */
    viewReport() {
        if (!this.currentTask || !this.currentTaskId) return;
        
        // Open patch preview page
        const patchViewUrl = `/patch_view/${this.currentTaskId}`;
        window.open(patchViewUrl, '_blank');
    }

    /**
     * Reset interface
     */
    resetInterface() {
        // Stop status polling
        if (this.statusPollingInterval) {
            clearInterval(this.statusPollingInterval);
        }
        
        // Reset state
        this.currentTaskId = null;
        this.currentTask = null;
        this.logBuffer = [];
        
        // Reset interface
        document.getElementById('taskStatus').classList.add('d-none');
        document.getElementById('defaultStatus').classList.remove('d-none');
        document.getElementById('completedActions').classList.add('d-none');
        
        // Clear form
        document.getElementById('repairForm').reset();
        document.getElementById('repoDescription').textContent = '';
        
        // Reset submit button
        this.resetSubmitButton();
        
        // Reset example buttons
        this.setupExampleButtons();
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${this.getNotificationIcon(type)} ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    /**
     * Get Bootstrap alert class
     */
    getBootstrapAlertClass(type) {
        const classMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return classMap[type] || 'info';
    }

    /**
     * Get notification icon
     */
    getNotificationIcon(type) {
        const iconMap = {
            'success': '<i class="fas fa-check-circle me-2"></i>',
            'error': '<i class="fas fa-exclamation-circle me-2"></i>',
            'warning': '<i class="fas fa-exclamation-triangle me-2"></i>',
            'info': '<i class="fas fa-info-circle me-2"></i>'
        };
        return iconMap[type] || iconMap['info'];
    }
}

// Initialize application after page load
document.addEventListener('DOMContentLoaded', () => {
    window.kgCompassApp = new KGCompassApp();
});

// Add some utility functions
window.KGCompassUtils = {
    /**
     * Format timestamp
     */
    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString('en-US');
    },
    
    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy text: ', err);
            return false;
        }
    }
}; 
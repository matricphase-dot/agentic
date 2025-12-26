// web/static/js/vibe_coding.js
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const vibeInput = document.getElementById('vibeInput');
    const generatedCode = document.getElementById('generatedCode');
    const executionOutput = document.getElementById('executionOutput');
    const executionStatus = document.getElementById('executionStatus');
    const executionTime = document.getElementById('executionTime');
    const executionHistory = document.getElementById('executionHistory');
    
    // Load execution history
    loadExecutionHistory();
    loadWorkflows();
    
    // WebSocket events
    socket.on('connect', function() {
        console.log('Connected to Vibe Coding Agent');
        updateStatus('🟢 Connected', 'success');
    });
    
    socket.on('vibe_result', function(data) {
        displayExecutionResult(data.result);
        addToHistory(data.command, data.result);
    });
    
    socket.on('workflow_taught', function(data) {
        showNotification(`Workflow saved: ${data.workflow_id}`, 'success');
        loadWorkflows();
    });
    
    // Functions
    function executeVibe() {
        const vibe = vibeInput.value.trim();
        if (!vibe) {
            showNotification('Please enter a vibe command', 'error');
            return;
        }
        
        // Show loading
        updateStatus('🤖 Processing vibe...', 'processing');
        
        // Send to server
        fetch('/api/vibe/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({vibe: vibe})
        })
        .then(response => response.json())
        .then(data => {
            // Display generated code
            generatedCode.textContent = data.code_generated;
            
            // Display execution result
            executionOutput.textContent = data.output;
            executionTime.textContent = `${data.execution_time}s`;
            
            if (data.success) {
                updateStatus('✅ Execution successful', 'success');
                showNotification('Vibe executed successfully!', 'success');
            } else {
                updateStatus('❌ Execution failed', 'error');
                showNotification('Execution failed: ' + data.output, 'error');
            }
            
            // Add to history
            addToHistory(vibe, data);
            
            // Emit socket event
            socket.emit('vibe_command', {
                command: vibe,
                user: 'User'
            });
        })
        .catch(error => {
            updateStatus('❌ Network error', 'error');
            showNotification('Network error: ' + error, 'error');
        });
    }
    
    function executeGeneratedCode() {
        const code = generatedCode.textContent;
        if (!code || code === '# Code will appear here...') {
            showNotification('No code to execute', 'warning');
            return;
        }
        
        updateStatus('⚡ Executing code...', 'processing');
        
        // Simulate execution (in real app, would send to server)
        setTimeout(() => {
            executionOutput.textContent = 'Simulating execution...\nCode would run here.';
            updateStatus('✅ Code executed', 'success');
            showNotification('Code execution simulated', 'info');
        }, 1000);
    }
    
    function useTemplate(template) {
        vibeInput.value = template;
    }
    
    function clearInput() {
        vibeInput.value = '';
        vibeInput.focus();
    }
    
    function copyCode() {
        const code = generatedCode.textContent;
        navigator.clipboard.writeText(code)
            .then(() => showNotification('Code copied to clipboard!', 'success'))
            .catch(() => showNotification('Failed to copy code', 'error'));
    }
    
    function saveWorkflow() {
        const vibe = vibeInput.value.trim();
        const code = generatedCode.textContent;
        
        if (!vibe || !code) {
            showNotification('No vibe or code to save', 'warning');
            return;
        }
        
        const steps = [
            {type: 'vibe_input', content: vibe},
            {type: 'code_generation', content: code}
        ];
        
        fetch('/api/vibe/teach', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({steps: steps})
        })
        .then(response => response.json())
        .then(data => {
            showNotification(data.message, 'success');
        })
        .catch(error => {
            showNotification('Failed to save workflow: ' + error, 'error');
        });
    }
    
    function optimizeCode() {
        const code = generatedCode.textContent;
        if (!code) return;
        
        // Simple optimization simulation
        const optimized = code
            .replace(/^\s+/gm, '')  // Remove leading whitespace
            .replace(/\n{3,}/g, '\n\n');  // Remove multiple blank lines
        
        generatedCode.textContent = optimized;
        showNotification('Code optimized!', 'success');
    }
    
    function startVoiceInput() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            showNotification('Voice recognition not supported in your browser', 'error');
            return;
        }
        
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            vibeInput.value = transcript;
            showNotification(`Voice input: ${transcript}`, 'info');
        };
        
        recognition.onerror = function(event) {
            showNotification('Voice recognition error: ' + event.error, 'error');
        };
        
        recognition.start();
        showNotification('Listening... Speak now!', 'info');
    }
    
    function updateStatus(text, type) {
        executionStatus.textContent = text;
        executionStatus.className = '';
        executionStatus.classList.add(type);
    }
    
    function displayExecutionResult(result) {
        executionOutput.textContent = result.output;
        executionTime.textContent = `${result.execution_time}s`;
    }
    
    function addToHistory(vibe, result) {
        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${result.success ? 'success' : 'error'}`;
        
        historyItem.innerHTML = `
            <div class="history-vibe">${vibe}</div>
            <div class="history-output">${result.success ? '✅ Success' : '❌ Error'}: ${result.output.substring(0, 100)}...</div>
            <div class="history-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        executionHistory.insertBefore(historyItem, executionHistory.firstChild);
        
        // Limit history
        if (executionHistory.children.length > 10) {
            executionHistory.removeChild(executionHistory.lastChild);
        }
    }
    
    function loadExecutionHistory() {
        fetch('/api/vibe/history')
            .then(response => response.json())
            .then(history => {
                executionHistory.innerHTML = '';
                history.slice(-10).reverse().forEach(item => {
                    const historyItem = document.createElement('div');
                    historyItem.className = `history-item ${item.result.success ? 'success' : 'error'}`;
                    
                    historyItem.innerHTML = `
                        <div class="history-vibe">${item.vibe}</div>
                        <div class="history-output">${item.result.success ? '✅' : '❌'} ${item.result.output.substring(0, 50)}...</div>
                        <div class="history-time">${new Date(item.timestamp).toLocaleTimeString()}</div>
                    `;
                    
                    executionHistory.appendChild(historyItem);
                });
            });
    }
    
    function loadWorkflows() {
        fetch('/api/vibe/workflows')
            .then(response => response.json())
            .then(workflows => {
                const workflowsList = document.getElementById('workflowsList');
                workflowsList.innerHTML = '';
                
                workflows.forEach(workflow => {
                    const workflowItem = document.createElement('div');
                    workflowItem.className = 'workflow-item';
                    workflowItem.innerHTML = `
                        <div class="workflow-name">${workflow.name}</div>
                        <div class="workflow-stats">${workflow.steps.length} steps • ${workflow.execution_count} executions</div>
                        <button class="btn-run-workflow" onclick="runWorkflow('${workflow.id}')">
                            <i class="fas fa-play"></i> Run
                        </button>
                    `;
                    workflowsList.appendChild(workflowItem);
                });
            });
    }
    
    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(`${tabName}Tab`).style.display = 'block';
        
        // Activate selected tab
        event.currentTarget.classList.add('active');
    }
    
    function showNotification(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'} ${message}
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        const container = document.getElementById('notificationContainer') || createNotificationContainer();
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    function createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notificationContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }
    
    // Global functions
    window.executeVibe = executeVibe;
    window.executeGeneratedCode = executeGeneratedCode;
    window.useTemplate = useTemplate;
    window.clearInput = clearInput;
    window.copyCode = copyCode;
    window.saveWorkflow = saveWorkflow;
    window.optimizeCode = optimizeCode;
    window.startVoiceInput = startVoiceInput;
    window.switchTab = switchTab;
    window.runWorkflow = function(workflowId) {
        showNotification(`Running workflow ${workflowId}...`, 'info');
    };
});
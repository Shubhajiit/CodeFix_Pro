import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Add CORS support

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Gemini API configuration
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def create_directories_and_files():
    """Create necessary directories and files for the application"""
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Create the HTML template
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeFix Pro | Advanced Code Debugging Platform</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <meta name="description" content="Professional AI-powered code debugging and optimization platform">
</head>
<body>
    <div class="container">
        <header class="app-header">
            <div class="logo-container">
                <div class="logo-icon"><span>&lt;/&gt;</span></div>
                <h1>CodeFix<span class="accent">Pro</span></h1>
            </div>
            <p class="tagline">Advanced AI-Powered Code Debugging & Optimization</p>
            <div class="header-decoration"></div>
        </header>
        
        <main class="workspace">
            <section class="code-container">
                <div class="code-panel input-panel">
                    <div class="panel-header">
                        <h2><span class="icon">📝</span>Source Code</h2>
                        <div class="panel-controls">
                            <button class="control-btn" id="clear-input" title="Clear code"><span>⟲</span></button>
                        </div>
                    </div>
                    <textarea id="buggy-code" placeholder="// Paste your code here for analysis and optimization..."></textarea>
                    <div class="button-group">
                        <button id="fix-code-btn" class="primary-btn"><span class="btn-icon">🔍</span>Analyze & Debug</button>
                    </div>
                </div>
                
                <div class="code-panel output-panel">
                    <div class="panel-header">
                        <h2><span class="icon">✅</span>Optimized Code</h2>
                        <div class="panel-controls">
                            <button class="control-btn" id="fullscreen-btn" title="Fullscreen"><span>⛶</span></button>
                        </div>
                    </div>
                    <div id="fixed-code-container">
                        <pre><code id="fixed-code">// Your optimized code will appear here...</code></pre>
                    </div>
                    <div class="button-group">
                        <button id="explain-code-btn" class="secondary-btn" disabled><span class="btn-icon">💡</span>Explain Changes</button>
                        <button id="copy-code-btn" class="secondary-btn" disabled><span class="btn-icon">📋</span>Copy Code</button>
                    </div>
                </div>
            </section>
            
            <section class="explanation-panel" id="explanation-panel">
                <div class="panel-header">
                    <h2><span class="icon">🧠</span>Technical Analysis</h2>
                </div>
                <div id="explanation-container" class="scrollable">
                    <p>Detailed analysis of code changes will appear here...</p>
                </div>
            </section>
        </main>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p id="loading-text">Analyzing code structure...</p>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
        
        <footer class="app-footer">
            <p>Powered by advanced AI technology</p>
        </footer>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const buggyCodeTextarea = document.getElementById('buggy-code');
            const fixedCodeElement = document.getElementById('fixed-code');
            const fixCodeBtn = document.getElementById('fix-code-btn');
            const explainCodeBtn = document.getElementById('explain-code-btn');
            const copyCodeBtn = document.getElementById('copy-code-btn');
            const loadingElement = document.getElementById('loading');
            const loadingTextElement = document.getElementById('loading-text');
            const explanationPanel = document.getElementById('explanation-panel');
            const explanationContainer = document.getElementById('explanation-container');
            const clearInputBtn = document.getElementById('clear-input');
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const progressFill = document.querySelector('.progress-fill');
            
            let originalCode = '';
            let fixedCode = '';
            
            // Initially hide the explanation panel
            explanationPanel.style.display = 'none';
            
            // Clear input button functionality
            clearInputBtn.addEventListener('click', function() {
                buggyCodeTextarea.value = '';
                buggyCodeTextarea.focus();
            });
            
            // Fullscreen functionality
            fullscreenBtn.addEventListener('click', function() {
                const codeContainer = document.querySelector('.output-panel');
                if (!document.fullscreenElement) {
                    if (codeContainer.requestFullscreen) {
                        codeContainer.requestFullscreen();
                    } else if (codeContainer.mozRequestFullScreen) {
                        codeContainer.mozRequestFullScreen();
                    } else if (codeContainer.webkitRequestFullscreen) {
                        codeContainer.webkitRequestFullscreen();
                    } else if (codeContainer.msRequestFullscreen) {
                        codeContainer.msRequestFullscreen();
                    }
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.mozCancelFullScreen) {
                        document.mozCancelFullScreen();
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen();
                    } else if (document.msExitFullscreen) {
                        document.msExitFullscreen();
                    }
                }
            });
            
            fixCodeBtn.addEventListener('click', async function() {
                originalCode = buggyCodeTextarea.value.trim();
                
                if (!originalCode) {
                    alert('Please enter some code to analyze');
                    return;
                }
                
                // Show loading
                loadingElement.style.display = 'flex';
                loadingTextElement.textContent = 'Analyzing code structure...';
                
                // Animate progress bar
                progressFill.style.width = '0%';
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += 1;
                    progressFill.style.width = `${Math.min(progress, 95)}%`;
                    
                    if (progress === 30) {
                        loadingTextElement.textContent = 'Identifying issues...';
                    } else if (progress === 60) {
                        loadingTextElement.textContent = 'Optimizing code...';
                    } else if (progress === 85) {
                        loadingTextElement.textContent = 'Finalizing solution...';
                    }
                }, 50);
                
                // Hide explanation panel when starting a new debug
                explanationPanel.style.display = 'none';
                
                // Disable explain button initially
                explainCodeBtn.disabled = true;
                copyCodeBtn.disabled = true;
                
                try {
                    const response = await fetch('/api/fix_code', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ code: originalCode })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        fixedCode = data.fixed_code;
                        fixedCodeElement.textContent = fixedCode;
                        
                        // Enable buttons after successful fix
                        explainCodeBtn.disabled = false;
                        copyCodeBtn.disabled = false;
                    } else {
                        fixedCodeElement.textContent = `Error: ${data.error || 'Unknown error'}`;
                    }
                } catch (error) {
                    fixedCodeElement.textContent = `Error: ${error.message}`;
                } finally {
                    // Complete progress bar
                    progressFill.style.width = '100%';
                    clearInterval(progressInterval);
                    
                    // Hide loading after a short delay to show completed progress
                    setTimeout(() => {
                        loadingElement.style.display = 'none';
                    }, 500);
                }
            });
            
            explainCodeBtn.addEventListener('click', async function() {
                if (!originalCode || !fixedCode) {
                    alert('Please debug the code first');
                    return;
                }
                
                // Show loading
                loadingElement.style.display = 'flex';
                loadingTextElement.textContent = 'Generating technical analysis...';
                
                // Reset and animate progress bar
                progressFill.style.width = '0%';
                let progress = 0;
                const progressInterval = setInterval(() => {
                    progress += 1;
                    progressFill.style.width = `${Math.min(progress, 95)}%`;
                }, 50);
                
                try {
                    const response = await fetch('/api/explain_changes', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ 
                            original_code: originalCode,
                            fixed_code: fixedCode
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        explanationContainer.innerHTML = data.explanation;
                        explanationPanel.style.display = 'block';
                    } else {
                        explanationContainer.innerHTML = `<p class="error">Error: ${data.error || 'Unknown error'}</p>`;
                        explanationPanel.style.display = 'block';
                    }
                } catch (error) {
                    explanationContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                    explanationPanel.style.display = 'block';
                } finally {
                    // Complete progress bar
                    progressFill.style.width = '100%';
                    clearInterval(progressInterval);
                    
                    // Hide loading after a short delay
                    setTimeout(() => {
                        loadingElement.style.display = 'none';
                    }, 500);
                }
            });
            
            copyCodeBtn.addEventListener('click', function() {
                if (!fixedCode) {
                    return;
                }
                
                // Create a temporary textarea to copy the text
                const tempTextarea = document.createElement('textarea');
                tempTextarea.value = fixedCode;
                document.body.appendChild(tempTextarea);
                tempTextarea.select();
                
                try {
                    document.execCommand('copy');
                    // Show temporary success message
                    const originalText = copyCodeBtn.textContent;
                    copyCodeBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyCodeBtn.textContent = originalText;
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy: ', err);
                } finally {
                    document.body.removeChild(tempTextarea);
                }
            });
        });
    </script>
</body>
</html>
        """)
    
    # Create the CSS file
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write("""

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
}

body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 20px;
    min-height: 100vh;
    color: #e7e7e7;
}

.container {
    max-width: 1300px;
    margin: 0 auto;
    background: rgba(26, 32, 44, 0.95);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    padding: 30px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.app-header {
    position: relative;
    margin-bottom: 40px;
    text-align: center;
}

.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
}

.logo-icon {
    background: linear-gradient(135deg, #ff6b6b, #ffa06b);
    width: 45px;
    height: 45px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    font-weight: 700;
    font-size: 1.5rem;
}

h1 {
    color: #ffffff;
    font-weight: 700;
    font-size: 2.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.accent {
    background: linear-gradient(to right, #ff6b6b, #ffa06b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.tagline {
    font-size: 1rem;
    color: #a0aec0;
    margin-bottom: 15px;
    font-weight: 300;
}

.header-decoration {
    height: 4px;
    width: 150px;
    background: linear-gradient(to right, #ff6b6b, #ffa06b, #ffd56b, #c2ff6b, #6bffd5, #6bb5ff, #a06bff);
    margin: 0 auto;
    border-radius: 2px;
}

.workspace {
    display: flex;
    flex-direction: column;
    gap: 30px;
}

h2 {
    margin-bottom: 0;
    font-size: 1.2rem;
    color: #e2e8f0;
    font-weight: 600;
    display: flex;
    align-items: center;
}

.icon {
    margin-right: 8px;
    font-size: 1.3rem;
}

.code-container {
    display: flex;
    gap: 25px;
}

@media (max-width: 992px) {
    .code-container {
        flex-direction: column;
    }
}

.code-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.code-panel:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.panel-controls {
    display: flex;
    gap: 8px;
}

.control-btn {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    width: 30px;
    height: 30px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #e2e8f0;
    transition: all 0.2s ease;
}

.control-btn:hover {
    background: rgba(255, 255, 255, 0.2);
}

.input-panel {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.output-panel {
    background: linear-gradient(135deg, #2c3e50 0%, #1a202c 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

textarea {
    width: 100%;
    height: 400px;
    padding: 15px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    resize: none;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 15px;
    background-color: rgba(0, 0, 0, 0.3);
    color: #e2e8f0;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

textarea:focus {
    outline: none;
    border-color: rgba(255, 107, 107, 0.5);
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3), 0 0 0 3px rgba(255, 107, 107, 0.2);
}

.button-group {
    display: flex;
    gap: 12px;
    margin-top: 15px;
}

button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 15px;
    transition: all 0.3s ease;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-icon {
    margin-right: 8px;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.primary-btn {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa06b 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.primary-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #ff5252 0%, #ff8a50 100%);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
}

.secondary-btn {
    background: rgba(255, 255, 255, 0.1);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.secondary-btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

#fixed-code-container {
    width: 100%;
    height: 400px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    overflow-y: auto;
    background-color: rgba(0, 0, 0, 0.3);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

pre {
    margin: 0;
    padding: 15px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
    color: #e2e8f0;
}

.explanation-panel {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    border-radius: 12px;
    padding: 25px;
    margin-top: 10px;
    border-left: 4px solid #ff6b6b;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease;
}

.explanation-panel:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}

#explanation-container {
    line-height: 1.7;
    color: #e2e8f0;
    max-height: 400px;
    overflow-y: auto;
    padding-right: 10px;
}

.scrollable::-webkit-scrollbar {
    width: 8px;
}

.scrollable::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}

.scrollable::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}

.scrollable::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

#explanation-container p {
    margin-bottom: 12px;
}

#explanation-container code {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 3px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    color: #ff6b6b;
}

.error {
    color: #ff6b6b;
    font-weight: 500;
}

.loading {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(26, 32, 44, 0.95);
    display: none;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    z-index: 1000;
    backdrop-filter: blur(8px);
}

.spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-top: 4px solid #ff6b6b;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin-bottom: 25px;
}

.progress-bar {
    width: 300px;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    margin-top: 20px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(to right, #ff6b6b, #ffa06b);
    border-radius: 3px;
    transition: width 0.3s ease;
}

#loading-text {
    font-size: 16px;
    color: white;
    font-weight: 400;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.app-footer {
    margin-top: 40px;
    text-align: center;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.9rem;
}
        """)

def fix_code_with_gemini(buggy_code):
    """Use Gemini API to fix the code"""
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Fix this code and only return the fixed code without any explanations:\n{buggy_code}"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=30  # Add timeout
        )
        
        response.raise_for_status()  # Raise exception for bad status codes
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: No response from AI model"
            
    except requests.exceptions.RequestException as e:
        return f"Error: Connection failed - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def explain_changes_with_gemini(original_code, fixed_code):
    """Use Gemini API to explain the changes made to the code"""
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""Explain the changes made to fix this code. Be detailed and technical:
Original code:
{original_code}

Fixed code:
{fixed_code}"""
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=30  # Add timeout
        )
        
        response.raise_for_status()  # Raise exception for bad status codes
        
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: No response from AI model"
            
    except requests.exceptions.RequestException as e:
        return f"Error: Connection failed - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fix_code', methods=['POST'])
def api_fix_code():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        buggy_code = data.get('code', '')
        if not buggy_code:
            return jsonify({'error': 'No code provided'}), 400
        
        fixed_code = fix_code_with_gemini(buggy_code)
        if fixed_code.startswith('Error:'):
            return jsonify({'error': fixed_code}), 500
            
        return jsonify({'fixed_code': fixed_code})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/explain_changes', methods=['POST'])
def api_explain_changes():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        original_code = data.get('original_code', '')
        fixed_code = data.get('fixed_code', '')
        
        if not original_code or not fixed_code:
            return jsonify({'error': 'Both original and fixed code are required'}), 400
        
        explanation = explain_changes_with_gemini(original_code, fixed_code)
        if explanation.startswith('Error:'):
            return jsonify({'error': explanation}), 500
            
        return jsonify({'explanation': explanation})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    create_directories_and_files()
    app.run(debug=True, port=5000)

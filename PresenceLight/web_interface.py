#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from typing import Dict, Any


class WebInterface:
    def __init__(self, presence_app=None):
        self.app = Flask(__name__)
        self.presence_app = presence_app
        self.config_file = 'config.json'
        self.load_config()
        self.setup_routes()
        
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'thresholds': {
                'idle_time': 60,
                'fragmented_window_changes': 3,
                'focused_stability': 120
            },
            'led': {
                'enabled': False,
                'port': None,
                'brightness': 0.8
            },
            'colors': {
                'focused': {'r': 0, 'g': 255, 'b': 0},
                'fragmented': {'r': 255, 'g': 165, 'b': 0},
                'absent': {'r': 100, 'g': 100, 'b': 255}
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def get_status():
            if self.presence_app:
                metrics = self.presence_app.monitor.get_activity_metrics()
                state = self.presence_app.current_state
                return jsonify({
                    'mode': state.mode,
                    'confidence': state.confidence,
                    'last_update': state.last_update.isoformat(),
                    'metrics': metrics
                })
            return jsonify({'error': 'No presence app connected'})
        
        @self.app.route('/api/config')
        def get_config():
            return jsonify(self.config)
        
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            new_config = request.json
            self.config.update(new_config)
            self.save_config()
            
            # Update presence app if connected
            if self.presence_app:
                self.presence_app.detector.thresholds = self.config['thresholds']
            
            return jsonify({'success': True})
        
        @self.app.route('/api/test_mode/<mode>')
        def test_mode(mode):
            if mode in ['focused', 'fragmented', 'absent']:
                # Simulate mode for testing
                return jsonify({'success': True, 'mode': mode})
            return jsonify({'error': 'Invalid mode'})
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        self.app.run(host=host, port=port, debug=debug)


def create_html_template():
    """Create the web interface HTML template"""
    template_dir = '/Users/tinagunnarsson/Projects/PresenceLight/templates'
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PresenceLight Control</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .status-card {
            background: #2d2d2d;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #404040;
        }
        
        .presence-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .focused { background: #00ff00; }
        .fragmented { background: #ffa500; }
        .absent { background: #6464ff; }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric {
            background: #3d3d3d;
            padding: 15px;
            border-radius: 8px;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #aaa;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .config-section {
            margin-top: 30px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            color: #ccc;
        }
        
        input[type="number"], input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #555;
            border-radius: 4px;
            background: #2d2d2d;
            color: #fff;
        }
        
        button {
            background: #007aff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 10px;
        }
        
        button:hover {
            background: #0056cc;
        }
        
        .test-buttons {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔮 PresenceLight</h1>
        <p>Ambient awareness for cognitive presence</p>
    </div>
    
    <div class="status-card">
        <h2>Current Status</h2>
        <div id="status">
            <span class="presence-indicator focused" id="indicator"></span>
            <span id="mode">Loading...</span>
            <span id="confidence"></span>
        </div>
        
        <div class="metrics-grid" id="metrics">
            <!-- Metrics will be populated by JavaScript -->
        </div>
    </div>
    
    <div class="status-card config-section">
        <h2>Configuration</h2>
        
        <div class="form-group">
            <label>Idle Time Threshold (seconds)</label>
            <input type="number" id="idle_time" value="60">
        </div>
        
        <div class="form-group">
            <label>Fragmented Window Changes (per minute)</label>
            <input type="number" id="fragmented_changes" value="3">
        </div>
        
        <div class="form-group">
            <label>LED Brightness</label>
            <input type="number" id="brightness" min="0" max="1" step="0.1" value="0.8">
        </div>
        
        <button onclick="saveConfig()">Save Settings</button>
        
        <div class="test-buttons">
            <h3>Test Modes</h3>
            <button onclick="testMode('focused')">🟢 Focused</button>
            <button onclick="testMode('fragmented')">🟡 Fragmented</button>
            <button onclick="testMode('absent')">🔴 Absent</button>
        </div>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('mode').textContent = 'Disconnected';
                        return;
                    }
                    
                    const indicator = document.getElementById('indicator');
                    const mode = document.getElementById('mode');
                    const confidence = document.getElementById('confidence');
                    
                    indicator.className = `presence-indicator ${data.mode}`;
                    mode.textContent = data.mode.charAt(0).toUpperCase() + data.mode.slice(1);
                    confidence.textContent = `(${(data.confidence * 100).toFixed(0)}%)`;
                    
                    // Update metrics
                    const metricsDiv = document.getElementById('metrics');
                    const metrics = data.metrics || {};
                    
                    metricsDiv.innerHTML = `
                        <div class="metric">
                            <div class="metric-label">Time Since Active</div>
                            <div class="metric-value">${Math.round(metrics.time_since_active || 0)}s</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Keystrokes</div>
                            <div class="metric-value">${metrics.keystroke_count || 0}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Window Changes</div>
                            <div class="metric-value">${metrics.window_changes || 0}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Current Window</div>
                            <div class="metric-value">${(metrics.current_window || 'Unknown').substring(0, 20)}</div>
                        </div>
                    `;
                })
                .catch(console.error);
        }
        
        function loadConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(config => {
                    document.getElementById('idle_time').value = config.thresholds.idle_time;
                    document.getElementById('fragmented_changes').value = config.thresholds.fragmented_window_changes;
                    document.getElementById('brightness').value = config.led.brightness;
                })
                .catch(console.error);
        }
        
        function saveConfig() {
            const config = {
                thresholds: {
                    idle_time: parseInt(document.getElementById('idle_time').value),
                    fragmented_window_changes: parseInt(document.getElementById('fragmented_changes').value),
                    focused_stability: 120
                },
                led: {
                    brightness: parseFloat(document.getElementById('brightness').value)
                }
            };
            
            fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Settings saved!');
                }
            })
            .catch(console.error);
        }
        
        function testMode(mode) {
            fetch(`/api/test_mode/${mode}`)
                .then(response => response.json())
                .then(data => {
                    console.log(`Testing ${mode} mode`);
                })
                .catch(console.error);
        }
        
        // Initialize
        loadConfig();
        updateStatus();
        setInterval(updateStatus, 2000);
    </script>
</body>
</html>'''
    
    with open(f'{template_dir}/index.html', 'w') as f:
        f.write(html_content)


if __name__ == "__main__":
    create_html_template()
    
    web = WebInterface()
    print("Starting web interface at http://127.0.0.1:5000")
    web.run(debug=True)
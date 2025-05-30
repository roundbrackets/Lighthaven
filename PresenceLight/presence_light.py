#!/usr/bin/env python3
import os
import sys
import time
import threading
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any
import psutil
import rumps
from pynput import mouse, keyboard
import subprocess


@dataclass
class PresenceState:
    mode: str  # 'focused', 'fragmented', 'absent'
    confidence: float
    last_update: datetime
    
    
class ActivityMonitor:
    def __init__(self):
        self.last_active = datetime.now()
        self.keystroke_count = 0
        self.mouse_movement_count = 0
        self.active_window_changes = 0
        self.current_window = None
        self.window_change_times = []
        self.reset_counters()
        
    def reset_counters(self):
        self.keystroke_count = 0
        self.mouse_movement_count = 0
        self.active_window_changes = 0
        self.window_change_times = []
        
    def on_key_press(self, key):
        self.keystroke_count += 1
        self.last_active = datetime.now()
        
    def on_mouse_move(self, x, y):
        self.mouse_movement_count += 1
        self.last_active = datetime.now()
        
    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.last_active = datetime.now()
            
    def get_active_window(self):
        try:
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                return frontApp
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
            
    def check_window_changes(self):
        current = self.get_active_window()
        if current and current != self.current_window:
            self.current_window = current
            self.active_window_changes += 1
            self.window_change_times.append(datetime.now())
            # Keep only last 10 window changes
            if len(self.window_change_times) > 10:
                self.window_change_times.pop(0)
                
    def get_activity_metrics(self):
        now = datetime.now()
        time_since_active = (now - self.last_active).total_seconds()
        
        # Calculate window change frequency
        recent_changes = [t for t in self.window_change_times 
                         if (now - t).total_seconds() < 300]  # Last 5 minutes
        window_change_frequency = len(recent_changes) / 5.0  # per minute
        
        return {
            'time_since_active': time_since_active,
            'keystroke_count': self.keystroke_count,
            'mouse_movement_count': self.mouse_movement_count,
            'window_changes': self.active_window_changes,
            'window_change_frequency': window_change_frequency,
            'current_window': self.current_window
        }


class PresenceDetector:
    def __init__(self):
        self.thresholds = {
            'idle_time': 60,  # seconds
            'fragmented_window_changes': 3,  # per minute
            'focused_stability': 120,  # seconds with same window
        }
        
    def analyze_presence(self, metrics: Dict[str, Any]) -> PresenceState:
        now = datetime.now()
        time_since_active = metrics['time_since_active']
        window_change_freq = metrics['window_change_frequency']
        
        # Absent: No activity for idle_time
        if time_since_active > self.thresholds['idle_time']:
            return PresenceState(
                mode='absent',
                confidence=min(1.0, time_since_active / 300),  # Max confidence at 5 min
                last_update=now
            )
            
        # Fragmented: Frequent window changes
        if window_change_freq > self.thresholds['fragmented_window_changes']:
            confidence = min(1.0, window_change_freq / 10)
            return PresenceState(
                mode='fragmented',
                confidence=confidence,
                last_update=now
            )
            
        # Focused: Stable activity
        keystroke_activity = metrics['keystroke_count'] > 0
        mouse_activity = metrics['mouse_movement_count'] > 0
        stable_window = window_change_freq < 1
        
        if (keystroke_activity or mouse_activity) and stable_window:
            return PresenceState(
                mode='focused',
                confidence=0.8,
                last_update=now
            )
            
        # Default to focused with lower confidence
        return PresenceState(
            mode='focused',
            confidence=0.3,
            last_update=now
        )


class PresenceLightApp(rumps.App):
    def __init__(self):
        super(PresenceLightApp, self).__init__("PresenceLight", "🔵")
        self.monitor = ActivityMonitor()
        self.detector = PresenceDetector()
        self.current_state = PresenceState('focused', 0.5, datetime.now())
        
        # State icons
        self.icons = {
            'focused': '🟢',
            'fragmented': '🟡', 
            'absent': '🔴'
        }
        
        # Start monitoring
        self.start_monitoring()
        
        # Update timer
        self.timer = rumps.Timer(self.update_presence, 5)
        self.timer.start()
        
    def start_monitoring(self):
        # Keyboard listener
        self.key_listener = keyboard.Listener(
            on_press=self.monitor.on_key_press
        )
        self.key_listener.start()
        
        # Mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self.monitor.on_mouse_move,
            on_click=self.monitor.on_mouse_click
        )
        self.mouse_listener.start()
        
        # Window monitoring thread
        self.window_thread = threading.Thread(
            target=self.window_monitor_loop, daemon=True
        )
        self.window_thread.start()
        
    def window_monitor_loop(self):
        while True:
            self.monitor.check_window_changes()
            time.sleep(2)
            
    def update_presence(self, _):
        metrics = self.monitor.get_activity_metrics()
        self.current_state = self.detector.analyze_presence(metrics)
        
        # Update tray icon
        icon = self.icons.get(self.current_state.mode, '🔵')
        self.title = icon
        
        # Update menu
        self.menu.clear()
        self.menu = [
            f"Mode: {self.current_state.mode.title()}",
            f"Confidence: {self.current_state.confidence:.1f}",
            f"Window: {metrics.get('current_window', 'Unknown')[:30]}",
            None,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]
        
        # Reset counters every 5 minutes
        if datetime.now().minute % 5 == 0:
            self.monitor.reset_counters()
    
    @rumps.clicked("Settings")
    def show_settings(self, _):
        rumps.alert("Settings", "Web interface coming soon!")


if __name__ == "__main__":
    app = PresenceLightApp()
    app.run()
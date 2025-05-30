# 🔮 PresenceLight

A minimal ambient awareness application that observes your computer activity and visualizes your cognitive presence through subtle lighting and interface cues.

## Features

- **🖱️ Activity Monitoring**: Tracks keyboard, mouse, and window focus changes
- **🧠 Presence Detection**: Infers three states:
  - **Focused** 🟢: Steady activity with stable window focus
  - **Fragmented** 🟡: Frequent context switching and window changes  
  - **Absent** 🔴: No activity detected
- **💡 Ambient Visualization**: 
  - macOS tray icon with live status
  - Optional RGB LED strip control via Arduino
  - Web interface for monitoring and configuration
- **⚙️ Configurable**: Adjustable thresholds and sensitivity

## Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Grant permissions**: 
   - Go to System Preferences → Security & Privacy → Privacy
   - Enable "Accessibility" and "Input Monitoring" for Terminal/Python

3. **Run PresenceLight**:
```bash
python run.py
```

4. **View web interface**: Open http://127.0.0.1:5000

## Hardware Setup (Optional)

For RGB LED feedback, connect an Arduino with LED strip:

1. Upload `arduino_sketch.ino` to your Arduino
2. Connect RGB LED strip to pins 9, 10, 11
3. PresenceLight will auto-detect the Arduino

## Presence States

- **🟢 Focused**: Sustained activity, minimal window switching
- **🟡 Fragmented**: Active but context-switching frequently  
- **🔴 Absent**: No keyboard/mouse activity for >60 seconds

## Configuration

Adjust thresholds via the web interface:
- Idle timeout
- Window change sensitivity
- LED brightness
- Color schemes

## Philosophy

PresenceLight is about awareness, not productivity gamification. It provides a gentle, ambient signal of your cognitive state—like a mood ring for focus.

## Files

- `presence_light.py` - Core monitoring and tray app
- `led_controller.py` - Arduino/LED hardware control  
- `web_interface.py` - Configuration and monitoring web UI
- `run.py` - Main application launcher
- `arduino_sketch.ino` - Arduino firmware for LED control

---

*Built for thoughtful ambient computing*
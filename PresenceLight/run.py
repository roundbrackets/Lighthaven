#!/usr/bin/env python3
import sys
import threading
import time
from presence_light import PresenceLightApp
from web_interface import WebInterface, create_html_template
from led_controller import LEDController


def main():
    print("🔮 Starting PresenceLight...")
    
    # Create HTML template
    create_html_template()
    
    # Initialize LED controller (optional)
    led_controller = LEDController()
    led_connected = led_controller.connect()
    
    if led_connected:
        print("✅ LED controller connected")
    else:
        print("⚠️  No LED device found (tray icon only)")
    
    # Create presence app
    presence_app = PresenceLightApp()
    
    # Start web interface in background thread
    web_interface = WebInterface(presence_app)
    web_thread = threading.Thread(
        target=web_interface.run,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False},
        daemon=True
    )
    web_thread.start()
    
    # Integration: Update LED based on presence state
    def update_led():
        while True:
            if led_connected and presence_app.current_state:
                led_controller.set_presence_mode(
                    presence_app.current_state.mode,
                    presence_app.current_state.confidence
                )
            time.sleep(5)
    
    if led_connected:
        led_thread = threading.Thread(target=update_led, daemon=True)
        led_thread.start()
    
    print("🌐 Web interface: http://127.0.0.1:5000")
    print("🖱️  Tray icon active")
    print("Press Ctrl+C to quit")
    
    try:
        # Run the tray app (blocks)
        presence_app.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down PresenceLight...")
        if led_connected:
            led_controller.disconnect()
        sys.exit(0)


if __name__ == "__main__":
    main()
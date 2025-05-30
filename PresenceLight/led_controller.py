#!/usr/bin/env python3
import serial
import time
import json
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class Color:
    r: int
    g: int
    b: int
    
    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class LEDController:
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.colors = {
            'focused': Color(0, 255, 0),      # Green
            'fragmented': Color(255, 165, 0), # Orange
            'absent': Color(100, 100, 255)    # Cool blue
        }
        
    def find_arduino_port(self) -> Optional[str]:
        """Auto-detect Arduino port on macOS"""
        import glob
        ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/tty.usbserial*')
        for port in ports:
            try:
                test_conn = serial.Serial(port, self.baudrate, timeout=1)
                test_conn.close()
                return port
            except:
                continue
        return None
        
    def connect(self) -> bool:
        """Connect to LED device"""
        if not self.port:
            self.port = self.find_arduino_port()
            
        if not self.port:
            print("No Arduino/LED device found")
            return False
            
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Arduino reset delay
            print(f"Connected to LED controller at {self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.port}: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from LED device"""
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
            
    def send_color(self, color: Color, brightness: float = 1.0):
        """Send RGB color to LED device"""
        if not self.serial_conn:
            return False
            
        # Adjust brightness
        r = int(color.r * brightness)
        g = int(color.g * brightness) 
        b = int(color.b * brightness)
        
        # Send as comma-separated values
        command = f"{r},{g},{b}\n"
        
        try:
            self.serial_conn.write(command.encode())
            return True
        except Exception as e:
            print(f"Failed to send color: {e}")
            return False
            
    def set_presence_mode(self, mode: str, confidence: float = 1.0):
        """Set LED based on presence mode"""
        if mode not in self.colors:
            return False
            
        color = self.colors[mode]
        brightness = confidence * 0.8 + 0.2  # Min 20% brightness
        
        # Special effects based on mode
        if mode == 'fragmented':
            self.flicker_effect(color, confidence)
        elif mode == 'absent':
            self.fade_effect(color, confidence)
        else:  # focused
            self.steady_glow(color, brightness)
            
    def steady_glow(self, color: Color, brightness: float):
        """Steady color output"""
        self.send_color(color, brightness)
        
    def flicker_effect(self, color: Color, intensity: float):
        """Gentle flicker for fragmented state"""
        base_brightness = 0.3
        flicker_amount = intensity * 0.5
        
        for i in range(3):
            brightness = base_brightness + (flicker_amount * (i % 2))
            self.send_color(color, brightness)
            time.sleep(0.2)
            
    def fade_effect(self, color: Color, intensity: float):
        """Fade to low brightness for absent state"""
        target_brightness = 0.1 + (intensity * 0.2)
        self.send_color(color, target_brightness)


def generate_arduino_sketch():
    """Generate Arduino sketch for LED control"""
    sketch = '''
/*
  PresenceLight LED Controller
  Controls RGB LED strip based on serial commands
*/

int redPin = 9;
int greenPin = 10;
int bluePin = 11;

void setup() {
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  
  // Initial state - blue
  analogWrite(redPin, 0);
  analogWrite(greenPin, 0);
  analogWrite(bluePin, 100);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\\n');
    command.trim();
    
    int firstComma = command.indexOf(',');
    int secondComma = command.indexOf(',', firstComma + 1);
    
    if (firstComma > 0 && secondComma > 0) {
      int r = command.substring(0, firstComma).toInt();
      int g = command.substring(firstComma + 1, secondComma).toInt();
      int b = command.substring(secondComma + 1).toInt();
      
      // Constrain values
      r = constrain(r, 0, 255);
      g = constrain(g, 0, 255);
      b = constrain(b, 0, 255);
      
      // Set LED colors
      analogWrite(redPin, r);
      analogWrite(greenPin, g);
      analogWrite(bluePin, b);
    }
  }
  
  delay(50);
}
'''
    
    with open('/Users/tinagunnarsson/Projects/PresenceLight/arduino_sketch.ino', 'w') as f:
        f.write(sketch)
    
    print("Arduino sketch saved to arduino_sketch.ino")


if __name__ == "__main__":
    # Generate Arduino sketch
    generate_arduino_sketch()
    
    # Test LED controller
    controller = LEDController()
    if controller.connect():
        print("Testing LED modes...")
        
        # Test each mode
        modes = ['focused', 'fragmented', 'absent']
        for mode in modes:
            print(f"Testing {mode} mode...")
            controller.set_presence_mode(mode, 0.8)
            time.sleep(3)
            
        controller.disconnect()
    else:
        print("No LED device found - generating Arduino sketch only")
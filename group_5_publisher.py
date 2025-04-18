# Group 5 COMP216 Project (Aleli, Manuel, Mayvis)
"""
IoT Data Publisher Implementation Requirements:

1. Multiple Publisher Clients:
   - Can run multiple instances to simulate different IoT devices
   - Each instance can have different base values and intervals

2. Value Generation (group_5_data_generator.py):
   - Implemented in separate class (DataGenerator)
   - Based on Week 9 Lab 8 simulator
   - Generates unlimited values
   - Flexible pattern configuration
   - Smooth transitions between values

3. Data Packaging:
   - Each value packaged as JSON object
   - Required fields:
     * timestamp (ISO format)
     * packet_id (unique identifier)
     * value (sensor reading)

4. Broker Communication:
   - Uses MQTT protocol for publishing
   - Configurable broker host and topic
   - Implements 1% random transmission loss
   
5. Extra Features:
   - Simulates corrupt data (1% chance of wild values)
   - GUI interface for easy configuration
   - Real-time status updates
   - Threaded publishing for non-blocking operation
"""

import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
import random
import time
import threading
from group_5_data_generator import DataGenerator

class PublisherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Data Publisher")
        
        self.data_generator = DataGenerator()
        self.is_running = False
        self.mqtt_client = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Publisher Controls")
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # MQTT Broker settings
        ttk.Label(control_frame, text="Broker Host:").grid(row=0, column=0, padx=5, pady=5)
        self.broker_host = ttk.Entry(control_frame)
        self.broker_host.insert(0, "localhost")
        self.broker_host.grid(row=0, column=1, padx=5, pady=5)
        
        # MQTT Topic configuration
        ttk.Label(control_frame, text="Topic:").grid(row=1, column=0, padx=5, pady=5)
        self.topic = ttk.Entry(control_frame)
        self.topic.insert(0, "iot/sound_data")
        self.topic.grid(row=1, column=1, padx=5, pady=5)
        
        # Generator settings
        ttk.Label(control_frame, text="Base Value:").grid(row=2, column=0, padx=5, pady=5)
        self.base_value = ttk.Entry(control_frame)
        self.base_value.insert(0, "20")
        self.base_value.grid(row=2, column=1, padx=5, pady=5)
        
        # Publishing interval configuration
        ttk.Label(control_frame, text="Interval (ms):").grid(row=3, column=0, padx=5, pady=5)
        self.interval = ttk.Entry(control_frame)
        self.interval.insert(0, "1000")
        self.interval.grid(row=3, column=1, padx=5, pady=5)
        
        # Control buttons
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_publishing)
        self.start_button.grid(row=4, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_publishing)
        self.stop_button.grid(row=4, column=1, padx=5, pady=5)
        
        # Status display
        self.status_text = tk.Text(self.root, height=10, width=50)
        self.status_text.grid(row=1, column=0, padx=5, pady=5)
        
    def start_publishing(self):
        """Initializes MQTT client and starts publishing thread"""
        if not self.is_running:
            self.is_running = True
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(self.broker_host.get(), 1883, 60)
            
            # Start publishing thread
            self.publish_thread = threading.Thread(target=self.publish_loop)
            self.publish_thread.daemon = True
            self.publish_thread.start()
            
            self.status_text.insert(tk.END, "Started publishing...\n")
            
    def stop_publishing(self):
        """Stops publishing and disconnects from broker"""
        self.is_running = False
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        self.status_text.insert(tk.END, "Stopped publishing...\n")
        
    def publish_loop(self):
        """Main publishing loop with error simulation features"""
        while self.is_running:
            try:
                # Simulate missing data (1% chance)
                if random.random() > 0.01:
                    data = self.data_generator.get_data_packet()
                    
                    # Simulate corrupt data (1% chance)
                    if random.random() < 0.01:
                        data["value"] *= random.uniform(10, 100)
                        
                    # Package and publish data
                    message = json.dumps(data)
                    self.mqtt_client.publish(self.topic.get(), message)
                    
                    self.root.after(0, self.update_status, f"Published: {message}\n")
                    
                time.sleep(float(self.interval.get()) / 1000)
                
            except Exception as e:
                self.root.after(0, self.update_status, f"Error: {str(e)}\n")
                
    def update_status(self, message):
        """Updates GUI status display"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PublisherGUI(root)
    root.mainloop()

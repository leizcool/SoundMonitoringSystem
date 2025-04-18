# Group 5 COMP216 Project (Aleli, Manuel, Mayvis)
"""
IoT Data Subscriber Implementation Requirements:

1. MQTT Broker Communication:
   - Listens to configured topic for IoT device data
   - Handles connection/disconnection gracefully
   - Decodes JSON messages from publishers

2. Data Processing and Validation:
   - Processes incoming sensor data in real-time
   - Validates data against defined thresholds
   - Handles three types of data scenarios:
     a) Normal data: Within expected range
     b) Erroneous data: Values outside threshold (>100)
     c) Missing data: No data received for 5+ seconds

3. Data Visualization:
   - Real-time plotting of sensor values
   - Text-based status updates
   - Visual indicators for data anomalies

4. Error Handling:
   - JSON decode errors
   - Connection issues
   - Out-of-range values
   - Missing data detection
"""

import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time

class SubscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Data Subscriber")
        
        # Initialize connection state and data storage
        self.mqtt_client = None
        self.is_connected = False
        self.data_points = []  # Stores (timestamp, value) tuples
        self.last_packet_time = None
        self.missing_data_threshold = 5  # seconds before declaring data missing
        
        self.setup_gui()
        self.setup_plot()
        
    def setup_gui(self):
        """
        Creates the GUI interface with:
        - Broker connection controls
        - Topic configuration
        - Connection status
        - Data display area
        """
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Subscriber Controls")
        control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Broker settings
        ttk.Label(control_frame, text="Broker Host:").grid(row=0, column=0, padx=5, pady=5)
        self.broker_host = ttk.Entry(control_frame)
        self.broker_host.insert(0, "localhost")
        self.broker_host.grid(row=0, column=1, padx=5, pady=5)
        
        # Topic configuration
        ttk.Label(control_frame, text="Topic:").grid(row=1, column=0, padx=5, pady=5)
        self.topic = ttk.Entry(control_frame)
        self.topic.insert(0, "iot/sound_data")
        self.topic.grid(row=1, column=1, padx=5, pady=5)
        
        # Connect/Disconnect button
        self.connect_button = ttk.Button(control_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Status display area
        self.status_text = tk.Text(self.root, height=10, width=50)
        self.status_text.grid(row=2, column=0, padx=5, pady=5)
        
    def setup_plot(self):
        """
        Initializes matplotlib plot for real-time data visualization:
        - Line plot for sensor values over time
        - Auto-updating display
        - Limited to last 50 data points for performance
        """
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=5, pady=5)
        
    def toggle_connection(self):
        """Handles connection state toggling"""
        if not self.is_connected:
            self.connect_to_broker()
        else:
            self.disconnect_from_broker()
            
    def connect_to_broker(self):
        """
        Establishes MQTT connection and starts monitoring:
        - Initializes MQTT client
        - Sets up message handlers
        - Starts monitoring thread for missing data
        """
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect
        
        try:
            self.mqtt_client.connect(self.broker_host.get(), 1883, 60)
            self.mqtt_client.loop_start()
            self.is_connected = True
            self.connect_button.config(text="Disconnect")
            self.update_status("Connected to broker\n")
            
            # Start missing data monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_missing_data)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
        except Exception as e:
            self.update_status(f"Connection error: {str(e)}\n")
            
    def disconnect_from_broker(self):
        """Cleanly disconnects from MQTT broker"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        self.is_connected = False
        self.connect_button.config(text="Connect")
        self.update_status("Disconnected from broker\n")
        
    def on_connect(self, client, userdata, flags, rc):
        """Subscribes to configured topic upon connection"""
        client.subscribe(self.topic.get())
        
    def on_message(self, client, userdata, msg):
        """
        Processes incoming MQTT messages:
        - Decodes JSON data
        - Validates value ranges
        - Updates visualization
        - Handles error conditions
        """
        try:
            data = json.loads(msg.payload)
            value = data["value"]
            timestamp = datetime.fromisoformat(data["timestamp"])
            
            # Validate data range (threshold: ±100)
            if abs(value) > 100:  # Erroneous data detection
                self.update_status(f"Warning: Erroneous data detected: {value}\n")
                return
                
            # Update data storage and timestamp
            self.data_points.append((timestamp, value))
            self.last_packet_time = time.time()
            
            # Maintain rolling window of 50 points
            if len(self.data_points) > 50:
                self.data_points.pop(0)
                
            self.update_plot()
            self.update_status(f"Received: {data}\n")
            
        except json.JSONDecodeError:
            self.update_status("Error: Invalid JSON data received\n")
        except Exception as e:
            self.update_status(f"Error processing message: {str(e)}\n")
            
    def update_plot(self):
        """
        Updates real-time data visualization:
        - Clears previous plot
        - Plots new data points
        - Updates axes and labels
        """
        self.ax.clear()
        timestamps = [d[0] for d in self.data_points]
        values = [d[1] for d in self.data_points]
        
        self.ax.plot(timestamps, values, 'b-')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.set_title('Real-time Data')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        self.canvas.draw()
        
    def monitor_missing_data(self):
        """
        Monitors for missing data:
        - Runs in separate thread
        - Checks for data gaps > 5 seconds
        - Issues warnings for missing data
        """
        while self.is_connected:
            if self.last_packet_time and time.time() - self.last_packet_time > self.missing_data_threshold:
                self.root.after(0, self.update_status, "Warning: Missing data detected!\n")
            time.sleep(1)
            
    def update_status(self, message):
        """Updates status display with new messages"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriberGUI(root)
    root.mainloop()

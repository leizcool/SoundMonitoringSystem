# Group 5 COMP216 Project (Aleli, Manuel, Mayvis)
"""
Project Requirements:
1. Generate simulated sensor data with realistic patterns
2. Include timestamp, value, and unique packet ID for each data point
3. Produce smooth transitions between values (no sudden jumps)
4. Support configurable base value and variance
5. Implement trending behavior to simulate real-world patterns
"""

import random
import time
from datetime import datetime

class DataGenerator:
    def __init__(self, base_value=20, variance=5, trend_strength=0.1):
        """
        Initialize the data generator with configurable parameters:
        - base_value: The center point around which values fluctuate (default: 20)
        - variance: Maximum deviation from base value (default: 5)
        - trend_strength: How strongly the trend can change (default: 0.1)
        """
        self.base_value = base_value
        self.variance = variance
        self.trend_strength = trend_strength
        self.current_trend = 0
        self.last_value = base_value

    def generate_value(self):
        """
        Generate a single data value with:
        - Random walk trend
        - Controlled variance
        - Smooth transitions between values
        Returns: A rounded float value
        """
        # Update trend (random walk)
        self.current_trend += random.uniform(-self.trend_strength, self.trend_strength)
        self.current_trend = max(min(self.current_trend, 1), -1)  # Keep trend between -1 and 1

        # Generate new value
        random_component = random.uniform(-self.variance, self.variance)
        trend_component = self.current_trend * self.variance
        new_value = self.base_value + random_component + trend_component

        # Ensure smooth transition (70% previous value, 30% new value)
        new_value = 0.7 * self.last_value + 0.3 * new_value
        self.last_value = new_value

        return round(new_value, 2)

    def get_data_packet(self):
        """
        Create a complete data packet containing:
        - ISO format timestamp
        - Generated sensor value
        - Unique packet ID (millisecond timestamp)
        Returns: Dictionary with data packet information
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "value": self.generate_value(),
            "packet_id": int(time.time() * 1000)  # millisecond timestamp as packet ID
        }

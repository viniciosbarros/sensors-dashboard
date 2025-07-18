#!/usr/bin/env python3
"""
Sensor Daemon for Casita
Reads temperature and humidity from SHT4x sensor every 15 seconds
and saves the data to PostgreSQL database.
"""

import time
import signal
import sys
import logging
from datetime import datetime
import board
import adafruit_sht4x
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/casita-sensor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SensorDaemon:
    def __init__(self):
        self.running = True
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'sensors_db'),
            'user': os.getenv('DB_USER', 'vini'),
            'password': os.getenv('DB_PASSWORD', 'sensors123')
        }
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
            
    def save_sensor_data(self, temperature, humidity):
        """Save sensor data to database"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Save temperature reading
                cursor.execute(
                    "INSERT INTO sensors_history (sensor_name, value, timestamp) VALUES (%s, %s, %s)",
                    ('temperature', round(temperature, 1), datetime.utcnow())
                )
                
                # Save humidity reading
                cursor.execute(
                    "INSERT INTO sensors_history (sensor_name, value, timestamp) VALUES (%s, %s, %s)",
                    ('humidity', round(humidity, 1), datetime.utcnow())
                )
                
                conn.commit()
                logger.info(f"Saved readings: T={temperature:.1f}°C, H={humidity:.1f}%")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save sensor data: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    def read_sensor(self):
        """Read sensor data"""
        try:
            i2c = board.I2C()
            sht = adafruit_sht4x.SHT4x(i2c)
            sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
            temperature, relative_humidity = sht.measurements
            return temperature, relative_humidity
        except Exception as e:
            logger.error(f"Failed to read sensor: {e}")
            return None, None
            
    def run(self):
        """Main daemon loop"""
        logger.info("Starting Casita Sensor Daemon...")
        logger.info(f"Database: {self.db_config['database']} on {self.db_config['host']}")
        
        while self.running:
            try:
                # Read sensor data
                temperature, humidity = self.read_sensor()
                
                if temperature is not None and humidity is not None:
                    # Save to database
                    success = self.save_sensor_data(temperature, humidity)
                    if success:
                        logger.info(f"Reading: {temperature:.1f}°C, {humidity:.1f}%")
                    else:
                        logger.warning("Failed to save sensor data")
                else:
                    logger.error("Failed to read sensor data")
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                
            # Wait 15 seconds before next reading
            time.sleep(15)
            
        logger.info("Casita Sensor Daemon stopped.")

def main():
    """Main entry point"""
    daemon = SensorDaemon()
    daemon.run()

if __name__ == "__main__":
    main() 
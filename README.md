# Sensor Dashboard

A Flask web application that displays real-time temperature and humidity data from an SHT4x sensor connected to a Raspberry Pi.

## Features

- Real-time sensor data display
- Modern, mobile-friendly web interface
- Auto-refresh every 30 seconds
- API endpoint for sensor data
- Error handling for sensor issues

## Requirements

- Raspberry Pi (or compatible board)
- SHT4x temperature/humidity sensor
- Python 3.11+
- Virtual environment
- PostgreSQL database server

## Installation

1. **Install PostgreSQL** (if not already installed):

Since we are using a Raspberry Pi OS we can install the database direct in the system.

   ```bash
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib
   ```

3. **Activate the virtual environment**:
   ```bash
   source bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   ```bash
   python setup_database.py
   ```

6. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit the .env file with your database credentials
   vim .env
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

   Troubleshoot: I am using Port 80. It will probably fail. So try to apt install authbind and configure it
   
   ```bash
   # Install authbind
   sudo apt-get install authbind

   # Create the permission file for port 80
   sudo touch /etc/authbind/byport/80

   # Set permissions (755 allows execution)
   sudo chmod 755 /etc/authbind/byport/80

   # Give ownership to your user
   sudo chown $USER /etc/authbind/byport/80
   
   authbind --deep python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://your-raspberry-pi-ip
   ```

3. The dashboard will display:
   - Current temperature in Celsius
   - Current humidity percentage
   - Auto-refresh every 30 seconds
   - Manual refresh button

## API Endpoints

### Current Sensor Data:
```
http://your-raspberry-pi-ip/api/sensor
```

### Sensor History:
```
http://your-raspberry-pi-ip/api/history
```
Returns the last 100 readings for each sensor type.

## Hardware Setup

Ensure your SHT4x sensor is properly connected to the Raspberry Pi via I2C:
- SDA pin
- SCL pin
- VCC (3.3V)
- GND

[Adafruit Reference Documentation here](https://learn.adafruit.com/adafruit-sht40-temperature-humidity-sensor/python-circuitpython)

## Troubleshooting

- **Always** check your sensor connections XD
- **Verify** the sensor is powered correctly XD
- Make sure I2C is enabled on your Raspberry Pi
   - [Check the documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#i2c)
- We are using http port 80, this might not work for you since linux only allow user ports above 1024, and `sudo python app.py` will not work because of pyenv. Workaround for now is to use `authbind`, check [Usage](#usage)
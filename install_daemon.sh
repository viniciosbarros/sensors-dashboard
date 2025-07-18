#!/bin/bash

# Casita Sensor Daemon Installation Script
# This script installs the sensor daemon as a systemd service

set -e

echo "🚀 Installing Casita Sensor Daemon..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Get the current user (who ran sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
PROJECT_DIR="/home/$ACTUAL_USER/sensors"

echo "📁 Project directory: $PROJECT_DIR"
echo "👤 User: $ACTUAL_USER"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Make sensor daemon executable
echo "🔧 Making sensor daemon executable..."
chmod +x "$PROJECT_DIR/sensor_daemon.py"

# Copy service file to systemd directory
echo "📋 Installing systemd service..."
cp "$PROJECT_DIR/casita-sensor.service" /etc/systemd/system/

# Update service file with correct paths
sed -i "s|User=vini|User=$ACTUAL_USER|g" /etc/systemd/system/casita-sensor.service
sed -i "s|Group=vini|Group=$ACTUAL_USER|g" /etc/systemd/system/casita-sensor.service
sed -i "s|WorkingDirectory=/home/vini/sensors|WorkingDirectory=$PROJECT_DIR|g" /etc/systemd/system/casita-sensor.service
sed -i "s|ExecStart=/home/vini/sensors/run_daemon.sh|ExecStart=$PROJECT_DIR/run_daemon.sh|g" /etc/systemd/system/casita-sensor.service

# Create log directory
echo "📝 Creating log directory..."
mkdir -p /var/log
touch /var/log/casita-sensor.log
chown $ACTUAL_USER:$ACTUAL_USER /var/log/casita-sensor.log

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
echo "🚀 Enabling and starting service..."
systemctl enable casita-sensor.service
systemctl start casita-sensor.service

# Check service status
echo "📊 Service status:"
systemctl status casita-sensor.service --no-pager -l

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Useful commands:"
echo "  Check status:    sudo systemctl status casita-sensor"
echo "  View logs:       sudo journalctl -u casita-sensor -f"
echo "  Stop service:    sudo systemctl stop casita-sensor"
echo "  Start service:   sudo systemctl start casita-sensor"
echo "  Restart service: sudo systemctl restart casita-sensor"
echo ""
echo "📝 Log file: /var/log/casita-sensor.log"
echo "🌐 Web interface: http://$(hostname -I | awk '{print $1}')" 
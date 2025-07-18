#!/bin/bash

# Wrapper script to run the sensor daemon with proper virtual environment

cd /home/vini/sensors
source bin/activate
exec python sensor_daemon.py 
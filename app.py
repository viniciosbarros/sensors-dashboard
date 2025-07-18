from flask import Flask, render_template, send_from_directory, jsonify
import time
import os
from dotenv import load_dotenv
from database import db, SensorHistory
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__, static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_latest_sensor_data():
    """Get the latest temperature and humidity readings from database"""
    try:
        with app.app_context():
            # Get latest temperature reading
            latest_temp = SensorHistory.query.filter_by(
                sensor_name='temperature'
            ).order_by(SensorHistory.timestamp.desc()).first()

            # Get latest humidity reading
            latest_humidity = SensorHistory.query.filter_by(
                sensor_name='humidity'
            ).order_by(SensorHistory.timestamp.desc()).first()

            if latest_temp and latest_humidity:
                return {
                    'temperature': latest_temp.value,
                    'humidity': latest_humidity.value,
                    'status': 'success',
                    'timestamp': latest_temp.timestamp.isoformat()
                }
            else:
                return {
                    'temperature': None,
                    'humidity': None,
                    'status': 'error',
                    'error': 'No sensor data available'
                }
    except Exception as e:
        return {
            'temperature': None,
            'humidity': None,
            'status': 'error',
            'error': str(e)
        }

@app.route('/')
def index():
    sensor_data = get_latest_sensor_data()
    return render_template('index.html', data=sensor_data)

@app.route('/api/sensor')
def api_sensor():
    return get_latest_sensor_data()

@app.route('/api/history')
def api_history():
    try:
        with app.app_context():
            from datetime import datetime, timedelta
            
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            temp_history = SensorHistory.query.filter(
                SensorHistory.sensor_name == 'temperature',
                SensorHistory.timestamp >= twenty_four_hours_ago
            ).order_by(SensorHistory.timestamp.desc()).all()
            
            humidity_history = SensorHistory.query.filter(
                SensorHistory.sensor_name == 'humidity',
                SensorHistory.timestamp >= twenty_four_hours_ago
            ).order_by(SensorHistory.timestamp.desc()).all()
            
            return jsonify({
                'temperature': [record.to_dict() for record in temp_history],
                'humidity': [record.to_dict() for record in humidity_history]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
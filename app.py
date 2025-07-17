from flask import Flask, render_template, send_from_directory, jsonify
import time
import board
import adafruit_sht4x
import os
from dotenv import load_dotenv
from database import db, SensorHistory

load_dotenv()

app = Flask(__name__, static_folder='static')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def get_sensor_data():
    """Read temperature and humidity from SHT4x sensor and save to database"""
    try:
        i2c = board.I2C()
        sht = adafruit_sht4x.SHT4x(i2c)
        sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
        temperature, relative_humidity = sht.measurements
        
        temp_rounded = round(temperature, 1)
        humidity_rounded = round(relative_humidity, 1)
        
        try:
            with app.app_context():
                temp_record = SensorHistory(sensor_name='temperature', value=temp_rounded)
                db.session.add(temp_record)
                humidity_record = SensorHistory(sensor_name='humidity', value=humidity_rounded)
                db.session.add(humidity_record)
                
                db.session.commit()
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return {
            'temperature': temp_rounded,
            'humidity': humidity_rounded,
            'status': 'success'
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
    sensor_data = get_sensor_data()
    return render_template('index.html', data=sensor_data)

@app.route('/api/sensor')
def api_sensor():
    return get_sensor_data()

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
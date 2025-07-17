from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SensorHistory(db.Model):
    """Model for storing sensor readings history"""
    __tablename__ = 'sensors_history'
    
    id = db.Column(db.Integer, primary_key=True)
    sensor_name = db.Column(db.String(50), nullable=False)  # 'temperature' or 'humidity'
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SensorHistory {self.sensor_name}: {self.value} at {self.timestamp}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'sensor_name': self.sensor_name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        } 
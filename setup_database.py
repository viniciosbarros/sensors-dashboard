#!/usr/bin/env python3
"""
Database setup script for the Casita sensor app
This script creates the database tables and can be used for initial setup
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sensors_history (
            id SERIAL PRIMARY KEY,
            sensor_name VARCHAR(50) NOT NULL,
            value FLOAT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print("Table 'sensors_history' created successfully!")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_name_timestamp ON sensors_history(sensor_name, timestamp);")
        conn.commit()
        print("Index created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\nDatabase setup completed successfully!")
        print(f"Database: {DB_NAME}")        
    except Exception as e:
        print(f"Error setting up database: {e}")
        print("\nMake sure PostgreSQL is installed and running.")
        print("You may need to update the database credentials in this script.")

if __name__ == '__main__':
    print("Setting up PostgreSQL database for Casita sensor app...")
    setup_database() 
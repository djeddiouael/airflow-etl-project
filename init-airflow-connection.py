#!/usr/bin/env python3
"""
Initialize Airflow connections for PostgreSQL databases.
This script should be run after Airflow is initialized.
"""

import os
import sys
from airflow.models import Connection
from airflow.utils.db import merge_conn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connection details
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'airflow')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'airflow')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'airflow')

def create_postgres_connections():
    """Create PostgreSQL connections in Airflow"""
    try:
        # Connection for ETL data database
        conn_etl = Connection(
            conn_id='postgres_etl',
            conn_type='postgres',
            host=POSTGRES_HOST,
            port=int(POSTGRES_PORT),
            login=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            schema='etl_data',
            description='PostgreSQL connection to ETL data database'
        )
        
        # Connection for Superset database
        conn_superset = Connection(
            conn_id='postgres_superset',
            conn_type='postgres',
            host=POSTGRES_HOST,
            port=int(POSTGRES_PORT),
            login=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            schema='superset_db',
            description='PostgreSQL connection to Superset metadata database'
        )
        
        # Merge connections (replace if exists)
        merge_conn(conn_etl)
        merge_conn(conn_superset)
        
        print("✅ PostgreSQL connections created successfully:")
        print(f"   - postgres_etl: {POSTGRES_HOST}:{POSTGRES_PORT}/{conn_etl.schema}")
        print(f"   - postgres_superset: {POSTGRES_HOST}:{POSTGRES_PORT}/{conn_superset.schema}")
        
    except Exception as e:
        print(f"❌ Error creating connections: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_postgres_connections()

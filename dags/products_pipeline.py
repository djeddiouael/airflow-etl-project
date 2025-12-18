"""
DAG ETL Pipeline pour les données de produits et inventaire
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DATA_PATH = '/opt/airflow/data'


def extract_products(**kwargs):
    """Extract: Lire les fichiers produits"""
    csv_file = os.path.join(DATA_PATH, 'products.csv')
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Fichier {csv_file} non trouvé")
    
    df = pd.read_csv(csv_file)
    print(f"✅ Extraction: {len(df)} produits lus")
    print(f"   Colonnes: {list(df.columns)}")
    df.to_json(os.path.join(DATA_PATH, 'extracted_products.json'), orient='records')
    return True


def transform_products(**kwargs):
    """Transform: Nettoyer et enrichir les données produits"""
    json_file = os.path.join(DATA_PATH, 'extracted_products.json')
    df = pd.read_json(json_file)
    
    # Nettoyage
    df = df.dropna()
    df['product_name'] = df['product_name'].str.strip().str.title()
    df['category'] = df['category'].str.strip().str.title()
    df['supplier'] = df['supplier'].str.strip().str.title()
    
    # Calculs
    df['inventory_value'] = df['stock_quantity'] * df['unit_cost']
    df['profit_margin'] = ((df['selling_price'] - df['unit_cost']) / df['selling_price'] * 100).round(2)
    df['stock_status'] = df['stock_quantity'].apply(
        lambda x: 'Critical' if x < 10 else ('Low' if x < 50 else 'OK')
    )
    
    print(f"✅ Transformation: {len(df)} produits traités")
    df.to_json(os.path.join(DATA_PATH, 'transformed_products.json'), orient='records')
    return True


def load_products(**kwargs):
    """Load: Insérer dans PostgreSQL"""
    json_file = os.path.join(DATA_PATH, 'transformed_products.json')
    df = pd.read_json(json_file)
    
    # Ajouter product_id s'il n'existe pas
    if 'product_id' not in df.columns:
        df['product_id'] = df.get('product_id', 'N/A')
    
    hook = PostgresHook(postgres_conn_id='postgres_etl')
    engine = hook.get_sqlalchemy_engine()
    
    # Mapper les colonnes au schéma de la table
    cols_to_use = ['product_id', 'product_name', 'category', 'supplier', 
                   'stock_quantity', 'unit_cost', 'selling_price', 
                   'inventory_value', 'profit_margin', 'stock_status']
    
    # Garder seulement les colonnes qui existent
    df_insert = df[[col for col in cols_to_use if col in df.columns]].copy()
    
    df_insert.to_sql('products_inventory', engine, schema='public', 
                     if_exists='append', index=False, method='multi')
    
    print(f"✅ Chargement: {len(df_insert)} produits insérés")
    return True


def generate_inventory_report(**kwargs):
    """Générer un rapport d'inventaire"""
    json_file = os.path.join(DATA_PATH, 'transformed_products.json')
    df = pd.read_json(json_file)
    
    if len(df) == 0:
        print("⚠️  Aucun produit à traiter pour le rapport")
        return True
    
    report = {
        'report_date': datetime.now().date(),
        'total_products': len(df),
        'total_inventory_value': float(df['inventory_value'].sum()),
        'avg_profit_margin': float(df['profit_margin'].mean()),
        'critical_stock_count': len(df[df['stock_status'] == 'Critical']),
        'low_stock_count': len(df[df['stock_status'] == 'Low']),
        'top_category': df.groupby('category')['inventory_value'].sum().idxmax()
    }
    
    report_df = pd.DataFrame([report])
    
    hook = PostgresHook(postgres_conn_id='postgres_etl')
    engine = hook.get_sqlalchemy_engine()
    report_df.to_sql('inventory_reports', engine, schema='public',
                     if_exists='append', index=False)
    
    print(f"✅ Rapport généré: Valeur totale = {report['total_inventory_value']:.2f}")
    return True


with DAG(
    'products_pipeline',
    default_args=default_args,
    description='Pipeline ETL pour inventaire produits',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'products', 'inventory'],
) as dag:
    
    extract_task = PythonOperator(task_id='extract_products', python_callable=extract_products)
    transform_task = PythonOperator(task_id='transform_products', python_callable=transform_products)
    load_task = PythonOperator(task_id='load_products', python_callable=load_products)
    report_task = PythonOperator(task_id='generate_report', python_callable=generate_inventory_report)
    
    extract_task >> transform_task >> load_task >> report_task


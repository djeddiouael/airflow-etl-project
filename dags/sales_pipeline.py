"""
DAG ETL Pipeline pour les données de ventes
Extract -> Transform -> Load
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import os

# Configuration par défaut du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Chemin des données
DATA_PATH = '/opt/airflow/data'


def extract_data(**kwargs):
    """
    Extract: Lire les fichiers CSV depuis le dossier data
    """
    csv_file = os.path.join(DATA_PATH, 'sales.csv')
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Ajouter une colonne id si elle n'existe pas
        if 'id' not in df.columns:
            df.insert(0, 'id', range(1, len(df) + 1))
        print(f"✅ Extraction réussie: {len(df)} lignes lues")
        # Sauvegarder en JSON pour passer entre les tâches
        df.to_json(os.path.join(DATA_PATH, 'extracted_data.json'), orient='records')
        return True
    else:
        print(f"❌ Fichier non trouvé: {csv_file}")
        raise FileNotFoundError(f"Fichier {csv_file} non trouvé")


def transform_data(**kwargs):
    """
    Transform: Nettoyer et transformer les données avec Pandas
    """
    json_file = os.path.join(DATA_PATH, 'extracted_data.json')
    df = pd.read_json(json_file)
    
    print(f"📊 Données avant transformation: {len(df)} lignes")
    
    # 1. Supprimer les valeurs nulles
    df = df.dropna()
    
    # 2. Convertir la colonne date
    df['date'] = pd.to_datetime(df['date'])
    
    # 3. Calculer le montant total
    df['total_amount'] = df['quantity'] * df['unit_price']
    
    # 4. Nettoyer les noms de produits (majuscules)
    df['product'] = df['product'].str.strip().str.title()
    df['category'] = df['category'].str.strip().str.title()
    df['region'] = df['region'].str.strip().str.title()
    
    # 5. Filtrer les valeurs négatives
    df = df[df['quantity'] > 0]
    df = df[df['unit_price'] > 0]
    
    print(f"✅ Données après transformation: {len(df)} lignes")
    
    # Sauvegarder les données transformées
    df.to_json(os.path.join(DATA_PATH, 'transformed_data.json'), orient='records', date_format='iso')
    
    return True


def load_data(**kwargs):
    """
    Load: Insérer les données transformées dans PostgreSQL
    """
    json_file = os.path.join(DATA_PATH, 'transformed_data.json')
    df = pd.read_json(json_file)
    
    # Convertir et formater la date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Sélectionner les colonnes requises
    cols_to_use = ['date', 'product', 'category', 'quantity', 'unit_price', 'total_amount', 'region']
    df_insert = df[[col for col in cols_to_use if col in df.columns]].copy()
    
    # Connexion à PostgreSQL
    hook = PostgresHook(postgres_conn_id='postgres_etl')
    engine = hook.get_sqlalchemy_engine()
    
    # Insérer les données dans la table
    df_insert.to_sql(
        'sales_transformed',
        engine,
        schema='public',
        if_exists='append',
        index=False,
        method='multi'
    )
    
    print(f"✅ Chargement réussi: {len(df_insert)} lignes insérées dans PostgreSQL")
    return True


def calculate_kpis(**kwargs):
    """
    Calculer les KPIs et les stocker dans la table sales_kpis
    """
    json_file = os.path.join(DATA_PATH, 'transformed_data.json')
    df = pd.read_json(json_file)
    
    if len(df) == 0:
        print("⚠️  Aucune donnée pour calculer les KPIs")
        return True
    
    # Calcul des KPIs
    total_sales = float(df['total_amount'].sum())
    total_quantity = int(df['quantity'].sum())
    avg_order_value = float(df['total_amount'].mean())
    top_product = df.groupby('product')['total_amount'].sum().idxmax() if len(df) > 0 else 'N/A'
    top_region = df.groupby('region')['total_amount'].sum().idxmax() if len(df) > 0 else 'N/A'
    
    kpi_data = {
        'calculation_date': datetime.now().date(),
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'avg_order_value': avg_order_value,
        'top_product': top_product,
        'top_region': top_region
    }
    
    kpi_df = pd.DataFrame([kpi_data])
    
    # Connexion à PostgreSQL
    hook = PostgresHook(postgres_conn_id='postgres_etl')
    engine = hook.get_sqlalchemy_engine()
    
    kpi_df.to_sql(
        'sales_kpis',
        engine,
        schema='public',
        if_exists='append',
        index=False
    )
    
    print(f"✅ KPIs calculés et sauvegardés:")
    print(f"   - Total Sales: {total_sales:.2f}")
    print(f"   - Total Quantity: {total_quantity}")
    print(f"   - Avg Order Value: {avg_order_value:.2f}")
    print(f"   - Top Product: {top_product}")
    print(f"   - Top Region: {top_region}")
    
    return True


# Définition du DAG
with DAG(
    'sales_pipeline',
    default_args=default_args,
    description='Pipeline ETL pour les données de ventes',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'sales'],
) as dag:
    
    # Tâche 1: Extraction
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )
    
    # Tâche 2: Transformation
    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )
    
    # Tâche 3: Chargement
    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )
    
    # Tâche 4: Calcul des KPIs
    kpi_task = PythonOperator(
        task_id='calculate_kpis',
        python_callable=calculate_kpis,
    )
    
    # Définir l'ordre d'exécution
    extract_task >> transform_task >> load_task >> kpi_task


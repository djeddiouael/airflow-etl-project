#!/usr/bin/env python3
"""
Script pour configurer Superset avec des charts et un dashboard
Crée une connexion PostgreSQL, des datasets et des visualisations
"""

import requests
import json
import time

# Configuration
SUPERSET_URL = "http://localhost:8088"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"

# Headers
headers = {
    "Content-Type": "application/json",
}

def get_csrf_token():
    """Obtenir le token CSRF pour les requêtes POST"""
    response = requests.get(f"{SUPERSET_URL}/api/v1/security/login", auth=(ADMIN_USER, ADMIN_PASSWORD))
    if response.status_code == 200:
        return response.json().get("result", {}).get("access_token")
    return None

def login():
    """Se connecter à Superset"""
    session = requests.Session()
    session.auth = (ADMIN_USER, ADMIN_PASSWORD)
    
    # Authentification
    login_data = {
        "username": ADMIN_USER,
        "password": ADMIN_PASSWORD,
        "provider": "db"
    }
    response = session.post(f"{SUPERSET_URL}/api/v1/security/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
    return None

def add_postgres_database(session):
    """Ajouter la connexion PostgreSQL à Superset"""
    print("🔧 Ajout de la connexion PostgreSQL...")
    
    db_config = {
        "database_name": "etl_data",
        "sqlalchemy_uri": "postgresql://airflow:airflow@postgres:5432/etl_data",
        "cache_timeout": 3600,
        "expose_in_sqllab": True,
    }
    
    response = session.post(
        f"{SUPERSET_URL}/api/v1/databases",
        json=db_config
    )
    
    if response.status_code in [200, 201]:
        db_id = response.json().get("id")
        print(f"✅ Database créée avec ID: {db_id}")
        return db_id
    elif response.status_code == 422:
        print("⚠️  Database déjà existante")
        # Récupérer l'ID de la database existante
        response = session.get(f"{SUPERSET_URL}/api/v1/databases")
        if response.status_code == 200:
            for db in response.json().get("result", []):
                if db.get("database_name") == "etl_data":
                    return db.get("id")
    
    print(f"❌ Erreur lors de la création: {response.status_code} - {response.text}")
    return None

def create_dataset(session, db_id, table_name):
    """Créer un dataset basé sur une table PostgreSQL"""
    print(f"📊 Création du dataset pour {table_name}...")
    
    dataset_config = {
        "table_name": table_name,
        "database": db_id,
        "schema": "public",
    }
    
    response = session.post(
        f"{SUPERSET_URL}/api/v1/datasets",
        json=dataset_config
    )
    
    if response.status_code in [200, 201]:
        dataset_id = response.json().get("id")
        print(f"✅ Dataset créé: {table_name} (ID: {dataset_id})")
        return dataset_id
    elif response.status_code == 422:
        print(f"⚠️  Dataset {table_name} déjà existant")
        # Récupérer l'ID du dataset existant
        response = session.get(f"{SUPERSET_URL}/api/v1/datasets")
        if response.status_code == 200:
            for ds in response.json().get("result", []):
                if ds.get("table_name") == table_name:
                    return ds.get("id")
    
    print(f"❌ Erreur: {response.status_code} - {response.text}")
    return None

def create_chart(session, dataset_id, chart_config):
    """Créer un chart"""
    print(f"📈 Création du chart: {chart_config['slice_name']}...")
    
    response = session.post(
        f"{SUPERSET_URL}/api/v1/charts",
        json=chart_config
    )
    
    if response.status_code in [200, 201]:
        chart_id = response.json().get("id")
        print(f"✅ Chart créé: {chart_config['slice_name']} (ID: {chart_id})")
        return chart_id
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")
        return None

def create_dashboard(session, dashboard_config):
    """Créer un dashboard"""
    print(f"🎨 Création du dashboard: {dashboard_config['dashboard_title']}...")
    
    response = session.post(
        f"{SUPERSET_URL}/api/v1/dashboards",
        json=dashboard_config
    )
    
    if response.status_code in [200, 201]:
        dashboard_id = response.json().get("id")
        print(f"✅ Dashboard créé (ID: {dashboard_id})")
        return dashboard_id
    else:
        print(f"❌ Erreur: {response.status_code} - {response.text}")
        return None

def main():
    """Fonction principale"""
    print("🚀 Configuration de Superset avec Airflow ETL\n")
    
    # Se connecter
    session = login()
    if not session:
        print("❌ Impossible de se connecter à Superset")
        return
    
    # Ajouter la database PostgreSQL
    db_id = add_postgres_database(session)
    if not db_id:
        print("❌ Impossible d'ajouter la database PostgreSQL")
        return
    
    print("\n" + "="*60)
    
    # Créer les datasets
    sales_dataset_id = create_dataset(session, db_id, "sales_transformed")
    kpis_dataset_id = create_dataset(session, db_id, "sales_kpis")
    
    print("\n" + "="*60)
    
    # Attendre un peu
    time.sleep(2)
    
    # Créer les charts pour sales_transformed
    charts = [
        {
            "slice_name": "Total Sales by Region",
            "viz_type": "pie",
            "datasource_id": sales_dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "datasource": f"table__{sales_dataset_id}",
                "viz_type": "pie",
                "groupby": ["region"],
                "metric": {"op": "sum", "col": "total_amount"},
                "row_limit": 10,
            })
        },
        {
            "slice_name": "Sales by Product",
            "viz_type": "bar",
            "datasource_id": sales_dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "datasource": f"table__{sales_dataset_id}",
                "viz_type": "bar",
                "groupby": ["product"],
                "metric": {"op": "sum", "col": "total_amount"},
                "row_limit": 10,
            })
        },
        {
            "slice_name": "Sales Trend",
            "viz_type": "line",
            "datasource_id": sales_dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "datasource": f"table__{sales_dataset_id}",
                "viz_type": "line",
                "x": "date",
                "y": ["total_amount"],
                "row_limit": 100,
            })
        },
        {
            "slice_name": "Orders by Category",
            "viz_type": "pie",
            "datasource_id": sales_dataset_id,
            "datasource_type": "table",
            "params": json.dumps({
                "datasource": f"table__{sales_dataset_id}",
                "viz_type": "pie",
                "groupby": ["category"],
                "metric": {"op": "count", "col": "id"},
                "row_limit": 10,
            })
        },
    ]
    
    chart_ids = []
    for chart_config in charts:
        chart_id = create_chart(session, sales_dataset_id, chart_config)
        if chart_id:
            chart_ids.append(chart_id)
    
    print("\n" + "="*60)
    
    # Créer le dashboard
    dashboard_config = {
        "dashboard_title": "ETL Sales Dashboard",
        "description": "Dashboard pour le pipeline ETL des ventes",
        "owners": [1],  # Admin user
    }
    
    dashboard_id = create_dashboard(session, dashboard_config)
    
    print("\n" + "="*60)
    print("\n✅ Configuration terminée!")
    print(f"\n📊 Accédez au dashboard:")
    print(f"   http://localhost:8088/dashboard/{dashboard_id}/")
    print(f"\n👤 Identifiants: admin / admin")

if __name__ == "__main__":
    main()

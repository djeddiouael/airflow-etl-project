# 🏗️ Architecture du Projet ETL

## Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   Airflow   │    │   Airflow   │    │  PostgreSQL │              │
│  │  Webserver  │    │  Scheduler  │    │    :5432    │              │
│  │   :8081     │    │             │    │             │              │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘              │
│         │                  │                   │                     │
│         └──────────────────┼───────────────────┘                     │
│                            │                                         │
│                    ┌───────▼───────┐                                │
│                    │     DAGs      │                                │
│                    │  ETL Pipeline │                                │
│                    └───────┬───────┘                                │
│                            │                                         │
│                    ┌───────▼───────┐                                │
│                    │   Superset    │                                │
│                    │    :8088      │                                │
│                    └───────────────┘                                │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Composants

### 1. Apache Airflow
- **Webserver** (port 8081): Interface utilisateur pour gérer les DAGs
- **Scheduler**: Exécute les tâches selon le planning défini
- **Executor**: LocalExecutor pour exécution locale

### 2. PostgreSQL (port 5432)
- Base `airflow`: Métadonnées Airflow
- Base `etl_data`: Données transformées
  - `sales_transformed`: Ventes nettoyées
  - `sales_kpis`: Indicateurs calculés
  - `products_inventory`: Inventaire produits
  - `inventory_reports`: Rapports inventaire

### 3. Apache Superset (port 8088)
- Visualisation des données
- Dashboards interactifs
- Connexion directe à PostgreSQL

## Flux de Données

```
CSV Files → Extract → Transform (Pandas) → Load (PostgreSQL) → Visualize (Superset)
```

### Pipeline Sales
1. **Extract**: Lecture `sales_data.csv`
2. **Transform**: Nettoyage, calcul total_amount
3. **Load**: Insertion dans `sales_transformed`
4. **KPIs**: Calcul et stockage des indicateurs

### Pipeline Products
1. **Extract**: Lecture `products_inventory.csv`
2. **Transform**: Calcul marge, statut stock
3. **Load**: Insertion dans `products_inventory`
4. **Report**: Génération rapport inventaire

## Volumes Docker

| Volume | Description |
|--------|-------------|
| `./dags` | Fichiers DAG Airflow |
| `./data` | Fichiers source CSV |
| `./logs` | Logs Airflow |
| `./plugins` | Plugins Airflow |
| `postgres-db-volume` | Données PostgreSQL |
| `superset-data` | Configuration Superset |


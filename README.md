# 🚀 AirFlow ETL : Data Pipeline Orchestration

Pipeline ETL complète pour l'ingestion et la transformation de données avec Apache Airflow, PostgreSQL et Superset.

## 📋 Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Extract   │───▶│  Transform  │───▶│    Load     │───▶│    KPIs     │
│  (CSV/Excel)│    │  (Pandas)   │    │ (PostgreSQL)│    │ (Dashboard) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🛠 Stack Technique

| Service | Port | Description |
|---------|------|-------------|
| **Airflow** | 8081 | Orchestration des workflows |
| **PostgreSQL** | 5432 | Base de données |
| **Superset** | 8088 | Visualisation |

## 📚 Documentation

## 🚀 Installation Rapide

### Prérequis
- Docker & Docker Compose installés
- 4GB RAM minimum

### Lancement

```bash
# 1. Cloner le projet
cd airflow_etl

# 2. Créer les dossiers nécessaires
mkdir -p logs plugins

# 3. Initialiser Airflow
docker-compose up airflow-init

# 4. Lancer tous les services
docker-compose up -d

# 5. Vérifier les services
docker-compose ps
```

## 🔐 Accès aux Services

| Service | URL | Login | Password |
|---------|-----|-------|----------|
| Airflow | http://localhost:8080 | admin | admin |
| Superset | http://localhost:8088 | admin | admin |
| PostgreSQL | localhost:5432 | airflow | airflow |

## 📊 Configuration de la Connexion PostgreSQL dans Airflow

1. Aller dans **Admin > Connections**
2. Créer une nouvelle connexion:
   - **Connection Id**: `postgres_etl`
   - **Connection Type**: Postgres
   - **Host**: `postgres`
   - **Schema**: `etl_data`
   - **Login**: `airflow`
   - **Password**: `airflow`
   - **Port**: `5432`

## 📈 Configuration Superset

1. Aller dans **Settings > Database Connections**
2. Ajouter PostgreSQL:
   ```
   postgresql://airflow:airflow@postgres:5432/etl_data
   ```
3. Créer des datasets sur les tables:
   - `sales_transformed`
   - `sales_kpis`

## 📁 Structure du Projet

```
airflow_etl/
├── docker-compose.yml      # Configuration Docker
├── dags/
│   └── etl_sales_pipeline.py   # DAG ETL principal
├── data/
│   └── sales_data.csv      # Données source
├── init-db/
│   └── 01-init.sql         # Script init PostgreSQL
├── logs/                   # Logs Airflow
└── plugins/                # Plugins Airflow
```

## 🔄 Pipeline ETL

Le DAG `etl_sales_pipeline` effectue:

1. **Extract**: Lecture des fichiers CSV
2. **Transform**: Nettoyage avec Pandas
   - Suppression des valeurs nulles
   - Conversion des types
   - Calcul du montant total
3. **Load**: Insertion dans PostgreSQL
4. **KPIs**: Calcul des indicateurs

## 🧪 Tester le DAG

```bash
# Tester une tâche spécifique
docker-compose exec airflow-scheduler airflow tasks test etl_sales_pipeline extract_data 2024-01-01
```

## 🛑 Arrêter les Services

```bash
docker-compose down

# Supprimer les volumes (reset complet)
docker-compose down -v

## 📤 Pousser ce projet sur GitHub

1. Créez un repository sur GitHub (vide) et copiez l'URL (SSH ou HTTPS).
2. Exécutez le script d'aide (ou les commandes manuelles ci-dessous) depuis la racine du projet:

```bash
# Avec le script helper (recommandé)
chmod +x scripts/git_init_and_push.sh
./scripts/git_init_and_push.sh git@github.com:USERNAME/REPO.git main

# OU manuellement:
git init
git add .
git commit -m "chore: initial import"
git branch -M main
git remote add origin <REMOTE_URL>
git push -u origin main
```

Remarques:
- Vérifiez le fichier `.gitignore` avant de pousser pour vous assurer qu'aucun secret n'est inclus.
- Le dépôt contient un workflow GitHub Actions `/.github/workflows/ci.yml` qui exécutera des checks de lint sur chaque push/PR.

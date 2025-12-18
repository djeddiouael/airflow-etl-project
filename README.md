# 🚀 AirFlow ETL : Data Pipeline Orchestration

Une solution complète d'orchestration de pipelines ETL (Extract-Transform-Load) utilisant **Apache Airflow**, **PostgreSQL** et **Superset** pour l'ingestion, la transformation et la visualisation des données en production.

## 📋 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
│   Extract       │───▶│   Transform      │───▶│     Load        │───▶│    KPIs &    │
│ (CSV/Excel)     │    │ (Pandas/Python)  │    │ (PostgreSQL DB) │    │  Dashboard   │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────┘
         ↓                      ↓                        ↓                    ↓
    Raw Data             Cleaned Data            Transformed Data      Visualization
```

## 🛠 Stack Technique

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **Airflow UI** | 8080 | Orchestration et monitoring des workflows | ✅ |
| **PostgreSQL** | 5432 | Base de données relationnelle | ✅ |
| **Superset** | 8088 | Visualisation et dashboards | ✅ |

## 📚 Documentation

- 📖 [Architecture Détaillée](docs/ARCHITECTURE.md) - Vue d'ensemble du système
- 🔄 [DAGs et Pipelines](docs/DAGS.md) - Description des workflows ETL

## 🚀 Installation Rapide

### Prérequis
- **Docker** & **Docker Compose** (v20.10+)
- **4GB RAM** minimum
- **5GB** espace disque disponible
- Accès Internet pour télécharger les images

### Étapes d'Installation

```bash
# 1️⃣ Cloner le projet
git clone <votre-url-repo>
cd airflow-etl-project

# 2️⃣ Créer les dossiers nécessaires
mkdir -p logs plugins

# 3️⃣ Configurer les variables d'environnement
cp env.example .env
# Éditer .env si nécessaire

# 4️⃣ Initialiser Airflow (première fois seulement)
docker-compose up airflow-init

# 5️⃣ Lancer tous les services
docker-compose up -d

# 6️⃣ Vérifier l'état des services
docker-compose ps
```

**Temps estimé :** 3-5 minutes après le téléchargement des images Docker

## 🔐 Accès aux Services

| Service | URL | Identifiant | Mot de passe | Notes |
|---------|-----|-------------|-------------|-------|
| **Airflow UI** | http://localhost:8080 | admin | admin | Orchestration des DAGs |
| **Superset** | http://localhost:8088 | admin | admin | Dashboards & Visualisation |
| **PostgreSQL** | localhost:5432 | airflow | airflow | Client: psql, DBeaver, etc. |

> ⚠️ **Production**: Changez les mots de passe par défaut dans `.env`

## 📊 Configuration de PostgreSQL dans Airflow

Airflow se configure automatiquement avec PostgreSQL lors du démarrage. Pour configurer manuellement une nouvelle connexion:

### Via l'Interface Web

1. Accédez à **Admin > Connections** dans Airflow UI
2. Cliquez sur **"+ Connexion"** (ou "Create")
3. Remplissez les détails suivants:
   - **Connection Id**: `postgres_etl`
   - **Connection Type**: `Postgres`
   - **Host**: `postgres` (nom du service Docker)
   - **Database**: `etl_data`
   - **Login**: `airflow`
   - **Password**: `airflow`
   - **Port**: `5432`
4. Cliquez sur **Save**

### Via Script

```bash
# Utiliser le script fourni (recommandé)
python init-airflow-connection.py
```

## 📈 Configuration Superset

### Connexion à la Base de Données

1. Accédez à **Settings > Database Connections** (icône engrenage)
2. Cliquez sur **"+ New"** ou **"Create"**
3. Sélectionnez **PostgreSQL** comme type
4. Entrez l'URI de connexion:
   ```
   postgresql://airflow:airflow@postgres:5432/etl_data
   ```
5. Testez la connexion et sauvegardez

### Création de Datasets et Dashboards

Les tables importantes à visualiser:
- `sales_transformed` - Données de ventes nettoyées
- `sales_kpis` - Indicateurs clés calculés
- `products` - Catalogue de produits

Utilisez l'interface Superset pour créer des datasets et des visualisations personnalisées.

> 📖 Voir la [configuration complète de Superset](superset/superset_config.py)

## 📁 Structure du Projet

```
airflow-etl-project/
├── 📄 docker-compose.yml           # Configuration Docker (services)
├── 📄 .env.example                 # Variables d'environnement (template)
├── 📄 README.md                    # Ce fichier
│
├── 📂 dags/                        # DAGs Airflow
│   ├── products_pipeline.py        # Pipeline pour les produits
│   └── sales_pipeline.py           # Pipeline pour les ventes
│
├── 📂 data/                        # Données sources
│   ├── products.csv
│   └── sales.csv
│
├── 📂 docs/                        # Documentation
│   ├── ARCHITECTURE.md             # Architecture système
│   └── DAGS.md                     # Description des DAGs
│
├── 📂 init-db/                     # Scripts d'initialisation DB
│   ├── init.sql
│   └── schema.sql
│
├── 📂 scripts/                     # Utilitaires
│   └── git_init_and_push.sh        # Initialiser GitHub
│
├── 📂 superset/                    # Configuration Superset
│   └── superset_config.py
│
├── 📂 logs/                        # Logs Airflow (généré)
└── 📂 plugins/                     # Plugins Airflow (généré)
```

## 🔄 Pipelines ETL

### Sales Pipeline (`sales_pipeline.py`)
Traite les données de ventes:

1. **Extract** 📥
   - Lecture du fichier `data/sales.csv`
   - Validation du format

2. **Transform** 🔧
   - Suppression des valeurs nulles
   - Conversion des types de données
   - Calcul du montant total (quantity × unit_price)
   - Ajout de timestamps

3. **Load** 📤
   - Insertion dans `sales_transformed` (PostgreSQL)
   - Calcul des KPIs
   - Stockage dans `sales_kpis`

### Products Pipeline (`products_pipeline.py`)
Traite le catalogue de produits:

1. Extraction depuis `data/products.csv`
2. Nettoyage et normalisation
3. Chargement dans la table `products`

## 🧪 Tester les DAGs

### Lancer un DAG complet
```bash
# Déclencher manuellement le DAG sales_pipeline
docker-compose exec airflow-scheduler airflow dags trigger sales_pipeline
```

### Tester une tâche spécifique
```bash
# Tester l'extraction de données
docker-compose exec airflow-scheduler airflow tasks test sales_pipeline extract_sales 2024-01-01
```

### Voir les logs
```bash
# Consulter les logs d'une tâche
docker-compose exec airflow-scheduler airflow tasks logs sales_pipeline extract_sales 2024-01-01
```

### Vérifier l'état des DAGs
```bash
# Lister tous les DAGs
docker-compose exec airflow-scheduler airflow dags list

# État du DAG
docker-compose exec airflow-scheduler airflow dags state sales_pipeline
```

## 🛑 Arrêter et Nettoyer

### Arrêter les Services
```bash
# Arrêter sans supprimer les volumes (données persistantes)
docker-compose stop

# Arrêter et supprimer les conteneurs
docker-compose down

# Reset complet (attention: supprime toutes les données!)
docker-compose down -v
```

### Nettoyer les Logs
```bash
# Supprimer les anciens logs Airflow
rm -rf logs/*
```

## 📤 Déployer sur GitHub

### Initialiser et Pousser le Repository

1. **Créez un nouveau repository** sur [GitHub](https://github.com/new) (vide, sans README)
2. **Copiez l'URL** (SSH recommandé si vous avez SSH keys configurées)

3. **Exécutez le script automatisé** (recommandé):
```bash
chmod +x scripts/git_init_and_push.sh
./scripts/git_init_and_push.sh git@github.com:VOTRE_USERNAME/VOTRE_REPO.git main
```

4. **OU procédez manuellement:**
```bash
git init
git add .
git commit -m "chore: initial import - Airflow ETL project"
git branch -M main
git remote add origin git@github.com:VOTRE_USERNAME/VOTRE_REPO.git
git push -u origin main
```

### Points Importants

⚠️ **Avant de pousser**:
- Vérifiez `.gitignore` pour éviter les secrets (credentials, tokens)
- Les dossiers `logs/`, `plugins/` et volumes Docker ne doivent pas être versionés
- Utilisez des variables d'environnement pour les données sensibles

✅ **Après le push**:
- Le workflow CI/CD `/.github/workflows/ci.yml` s'exécutera automatiquement
- Les checks de lint seront appliqués à chaque commit

## ❓ Dépannage

### Les services ne démarrent pas
```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Voir les logs
docker-compose logs -f

# Redémarrer les services
docker-compose restart
```

### PostgreSQL inaccessible
```bash
# Vérifier la connexion PostgreSQL
docker-compose exec postgres psql -U airflow -d etl_data -c "SELECT 1;"
```

### Réinitialiser Airflow
```bash
docker-compose down -v
docker-compose up airflow-init
docker-compose up -d
```

## 🤝 Contribution

Les contributions sont bienvenues! Pour contribuer:

1. Fork le repository
2. Créez une branche (`git checkout -b feature/amélioration`)
3. Commitez vos changements (`git commit -m 'Add: nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/amélioration`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème:
- 📖 Consultez la [documentation technique](docs/ARCHITECTURE.md)
- 🐛 Ouvrez une [issue GitHub](https://github.com/djeddiouael/airflow-etl-project/issues)
- 💬 Visitez la section [Discussions](https://github.com/djeddiouael/airflow-etl-project/discussions)

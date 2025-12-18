# 📊 Documentation des DAGs

## Vue d'ensemble

| DAG | Description | Schedule |
|-----|-------------|----------|
| `etl_sales_pipeline` | Pipeline ETL pour les ventes | Daily |
| `etl_products_pipeline` | Pipeline ETL pour l'inventaire | Daily |

---

## 1. etl_sales_pipeline

### Description
Pipeline ETL pour ingérer, transformer et charger les données de ventes.

### Tâches

```
extract_data → transform_data → load_data → calculate_kpis
```

#### extract_data
- **Source**: `data/sales_data.csv`
- **Action**: Lit le fichier CSV et sauvegarde en JSON

#### transform_data
- **Transformations**:
  - Suppression des valeurs nulles
  - Conversion des dates
  - Calcul du `total_amount = quantity × unit_price`
  - Nettoyage des noms (Title Case)
  - Filtrage des valeurs négatives

#### load_data
- **Destination**: Table `sales_transformed`
- **Mode**: Append (ajout)

#### calculate_kpis
- **KPIs calculés**:
  - Total des ventes
  - Quantité totale
  - Valeur moyenne par commande
  - Produit le plus vendu
  - Région top
- **Destination**: Table `sales_kpis`

### Schéma de données

**sales_transformed**
| Colonne | Type | Description |
|---------|------|-------------|
| date | DATE | Date de vente |
| product | VARCHAR | Nom du produit |
| category | VARCHAR | Catégorie |
| quantity | INTEGER | Quantité vendue |
| unit_price | DECIMAL | Prix unitaire |
| total_amount | DECIMAL | Montant total |
| region | VARCHAR | Région |

---

## 2. etl_products_pipeline

### Description
Pipeline ETL pour gérer l'inventaire des produits.

### Tâches

```
extract_products → transform_products → load_products → generate_report
```

#### extract_products
- **Source**: `data/products_inventory.csv`

#### transform_products
- **Transformations**:
  - Calcul `inventory_value = stock × unit_cost`
  - Calcul `profit_margin = (selling - cost) / selling × 100`
  - Attribution `stock_status`:
    - < 10: Critical
    - < 50: Low
    - ≥ 50: OK

#### load_products
- **Destination**: Table `products_inventory`

#### generate_report
- **Métriques**:
  - Nombre total de produits
  - Valeur totale de l'inventaire
  - Marge bénéficiaire moyenne
  - Produits en stock critique/faible
- **Destination**: Table `inventory_reports`

### Schéma de données

**products_inventory**
| Colonne | Type | Description |
|---------|------|-------------|
| product_id | VARCHAR | ID unique |
| product_name | VARCHAR | Nom du produit |
| category | VARCHAR | Catégorie |
| supplier | VARCHAR | Fournisseur |
| stock_quantity | INTEGER | Quantité en stock |
| unit_cost | DECIMAL | Coût unitaire |
| selling_price | DECIMAL | Prix de vente |
| inventory_value | DECIMAL | Valeur stock |
| profit_margin | DECIMAL | Marge (%) |
| stock_status | VARCHAR | Statut stock |

---

## Tester les DAGs

```bash
# Tester une tâche spécifique
docker-compose exec airflow-scheduler airflow tasks test etl_sales_pipeline extract_data 2024-01-01

# Lister tous les DAGs
docker-compose exec airflow-scheduler airflow dags list

# Déclencher un DAG manuellement
docker-compose exec airflow-scheduler airflow dags trigger etl_sales_pipeline
```


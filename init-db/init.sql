-- Créer la base de données pour les données ETL
CREATE DATABASE etl_data;

-- Créer la base de données pour Superset metadata
CREATE DATABASE superset_db;

-- Se connecter à la base etl_data et créer les tables
\c etl_data;

-- Table pour stocker les données de ventes transformées
CREATE TABLE IF NOT EXISTS sales_transformed (
    id SERIAL PRIMARY KEY,
    date DATE,
    product VARCHAR(255),
    category VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour stocker les KPIs calculés
CREATE TABLE IF NOT EXISTS sales_kpis (
    id SERIAL PRIMARY KEY,
    calculation_date DATE,
    total_sales DECIMAL(12,2),
    total_quantity INTEGER,
    avg_order_value DECIMAL(10,2),
    top_product VARCHAR(255),
    top_region VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour stocker les données de produits transformées
CREATE TABLE IF NOT EXISTS products_inventory (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(255),
    category VARCHAR(100),
    supplier VARCHAR(255),
    stock_quantity INTEGER,
    unit_cost DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    inventory_value DECIMAL(12,2),
    profit_margin DECIMAL(5,2),
    stock_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les rapports d'inventaire
CREATE TABLE IF NOT EXISTS inventory_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE,
    total_products INTEGER,
    total_inventory_value DECIMAL(12,2),
    avg_profit_margin DECIMAL(5,2),
    critical_stock_count INTEGER,
    low_stock_count INTEGER,
    top_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Donner les permissions à l'utilisateur airflow
GRANT ALL PRIVILEGES ON DATABASE etl_data TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO airflow;

-- Se connecter à superset_db et donner les permissions
\c superset_db;
GRANT ALL PRIVILEGES ON DATABASE superset_db TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO airflow;


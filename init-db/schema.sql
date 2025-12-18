-- Tables pour le pipeline produits
\c etl_data;

-- Table inventaire produits
CREATE TABLE IF NOT EXISTS products_inventory (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(20),
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

-- Table rapports inventaire
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

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_products_category ON products_inventory(category);
CREATE INDEX IF NOT EXISTS idx_products_stock_status ON products_inventory(stock_status);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales_transformed(date);
CREATE INDEX IF NOT EXISTS idx_sales_region ON sales_transformed(region);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO airflow;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO airflow;


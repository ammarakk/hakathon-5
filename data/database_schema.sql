-- Nur Scents Customer Success Agent - Database Schema
-- PostgreSQL + pgvector

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    preferred_channel VARCHAR(20) DEFAULT 'whatsapp', -- whatsapp, email, web
    language VARCHAR(10) DEFAULT 'ur', -- ur (Roman Urdu), en
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_orders INTEGER DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0,
    is_blacklisted BOOLEAN DEFAULT FALSE,
    blacklist_reason TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Products table
CREATE TABLE products (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    images JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    sizes JSONB DEFAULT '[]'::jsonb,
    bestseller BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, processing, shipped, delivered, cancelled
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending', -- pending, paid, failed, refunded
    delivery_address TEXT,
    delivery_city VARCHAR(100),
    delivery_charges DECIMAL(10, 2) DEFAULT 0,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    tracking_number VARCHAR(100),
    channel VARCHAR(20) NOT NULL, -- whatsapp, email, web
    source_message_id VARCHAR(255), -- ID from original channel message
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Order items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(20) REFERENCES products(id),
    product_name VARCHAR(255),
    quantity INTEGER NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    size VARCHAR(50),
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table (for tracking customer interactions)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    channel VARCHAR(20) NOT NULL, -- whatsapp, email, web
    channel_message_id VARCHAR(255) UNIQUE,
    direction VARCHAR(20) NOT NULL, -- inbound, outbound
    message_type VARCHAR(50), -- text, image, audio, video, document
    content TEXT NOT NULL,
    ai_generated BOOLEAN DEFAULT FALSE,
    escalated BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Knowledge base for FAQ (with vector embedding)
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    keywords JSONB DEFAULT '[]'::jsonb,
    embedding vector(1536), -- For OpenAI embeddings or similar
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Incidents/Escalations table
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    conversation_id INTEGER REFERENCES conversations(id),
    type VARCHAR(50), -- complaint, return, refund, technical, other
    severity VARCHAR(20), -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'open', -- open, in_progress, resolved, closed
    description TEXT NOT NULL,
    resolution TEXT,
    assigned_to VARCHAR(100), -- NULL = AI handled, otherwise owner name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Daily reports table
CREATE TABLE daily_reports (
    id SERIAL PRIMARY KEY,
    report_date DATE UNIQUE NOT NULL,
    total_conversations INTEGER DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    total_revenue DECIMAL(10, 2) DEFAULT 0,
    escalated_incidents INTEGER DEFAULT 0,
    resolved_incidents INTEGER DEFAULT 0,
    ai_responses_percentage DECIMAL(5, 2) DEFAULT 0,
    channel_breakdown JSONB DEFAULT '{}'::jsonb,
    top_products JSONB DEFAULT '[]'::jsonb,
    common_issues JSONB DEFAULT '[]'::jsonb,
    report_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Email queue table
CREATE TABLE email_queue (
    id SERIAL PRIMARY KEY,
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for performance
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_active ON products(is_active);

-- Function to update customer timestamp
CREATE OR REPLACE FUNCTION update_customer_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for customers table
CREATE TRIGGER customer_timestamp_update
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_timestamp();

-- Trigger for products table
CREATE TRIGGER product_timestamp_update
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_timestamp();

-- Trigger for orders table
CREATE TRIGGER order_timestamp_update
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_timestamp();

-- Database initialization script for Library Management System
-- This script creates the initial schema

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (role IN ('admin', 'user'))
);

-- Create teachers table
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    classroom VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_label VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    category_label VARCHAR(50),
    location_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_label) REFERENCES categories(category_label) ON DELETE SET NULL
);

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER,
    storage_location_id INTEGER,
    status VARCHAR(20) DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (storage_location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    CHECK (status IN ('Available', 'On Loan', 'Lost', 'Archived'))
);

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    book_id VARCHAR(50) NOT NULL,
    teacher_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    CHECK (action IN ('borrow', 'return'))
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_book ON transactions(book_id);
CREATE INDEX IF NOT EXISTS idx_transactions_teacher ON transactions(teacher_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for books table
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123 - CHANGE IN PRODUCTION!)
-- Bcrypt hash generated for 'admin123'
INSERT INTO users (username, password_hash, role) 
VALUES ('admin', '$2b$12$mWxEhTbVKcc47xuvPRIKyezqvgBtGXOMzpCuefO43T7.TYmUjxMuS', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Insert some sample data for testing (optional)
INSERT INTO teachers (name, classroom) VALUES 
    ('John Smith', 'Room 101'),
    ('Jane Doe', 'Room 102'),
    ('Bob Johnson', 'Room 103')
ON CONFLICT DO NOTHING;

INSERT INTO categories (category_name, category_label) VALUES 
    ('Fiction', 'FIC'),
    ('Non-Fiction', 'NF'),
    ('Science', 'SCI'),
    ('History', 'HIST'),
    ('Mathematics', 'MATH')
ON CONFLICT (category_label) DO NOTHING;

INSERT INTO locations (category_label, location_name) VALUES 
    ('FIC', 'Shelf A1'),
    ('NF', 'Shelf B1'),
    ('SCI', 'Shelf C1'),
    ('HIST', 'Shelf D1'),
    ('MATH', 'Shelf E1')
ON CONFLICT DO NOTHING;

#--Resturant db--
CREATE DATABASE IF NOT EXISTS bistro_db;
USE bistro_db;

-- Table for Dishes
CREATE TABLE dishes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    image_url VARCHAR(500),
    category VARCHAR(100)
);

-- Table for Customer Messages/Bot
CREATE TABLE customer_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
 USE bistro_db;
SHOW TABLES;


SELECT * FROM dishes;

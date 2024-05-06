-- Nikhil Mahalingam & Andrew Xie
DROP TABLE IF EXISTS Order_Items;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;
DROP TYPE IF EXISTS order_status;

-- CUSTOMERS
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20)
);

-- PRODUCTS
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    slug VARCHAR(255),
    price DECIMAL(10, 2),
    stock_quantity INT
);

CREATE TYPE order_status AS ENUM ('cart', 'pending', 'completed');

-- ORDERS
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10, 2),
    status order_status NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);



-- ORDER ITEMS (ITEMS IN AN ORDER)
CREATE TABLE Order_Items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
-- TODO: 
-- PAYMENTS?
-- RETURNS?
-- PRODUCT CATEGORIES?
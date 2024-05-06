CREATE OR REPLACE FUNCTION add_customers()
RETURNS void AS $$
BEGIN
    FOR i IN 1..100 LOOP
        INSERT INTO Customers (first_name, last_name, email, phone_number, address, city, state, zip_code)
        VALUES (
            'FirstName' || i, 
            'LastName' || i, 
            'user' || i || '@example.com', 
            '1234567890', 
            '123 Main St', 
            'Anytown', 
            'CA', 
            '90210'
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION add_orders()
RETURNS void AS $$
DECLARE
    selected_customer_id INT;
    selected_product_id INT;
BEGIN
    SELECT product_id INTO selected_product_id FROM Products LIMIT 1;
    
    FOR i IN 1..100 LOOP
        SELECT customer_id INTO selected_customer_id FROM Customers ORDER BY RANDOM() LIMIT 1;
        
        INSERT INTO Orders (customer_id, order_date, status)
        VALUES (
            selected_customer_id,
            CURRENT_DATE,
            'cart'
        );

        INSERT INTO Order_Items (order_id, product_id, quantity)
        VALUES (
            currval('orders_order_id_seq'), 
            selected_product_id, 
            1
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT add_orders();



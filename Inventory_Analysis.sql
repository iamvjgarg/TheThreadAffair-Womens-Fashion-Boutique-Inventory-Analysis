CREATE DATABASE thethreadaffair_inventory;
USE thethreadaffair_inventory;

-- 1. PRODUCTS TABLE

CREATE TABLE products (
    Product_ID VARCHAR(20) PRIMARY KEY,
    Product_Name VARCHAR(100),
    Category VARCHAR(50),
    Sub_Category VARCHAR(50),
    Gender VARCHAR(20),
    Size VARCHAR(20),
    Colour VARCHAR(30),
    Season VARCHAR(30),
    Cost_Price_INR DECIMAL(12,2),
    Selling_Price_INR DECIMAL(12,2),
    Launch_Date DATE,
    Product_Status VARCHAR(30)
);


-- 2. OPENING INVENTORY TABLE

CREATE TABLE opening_inventory (
    Product_ID VARCHAR(20) PRIMARY KEY,
    Opening_Stock_Quantity INT,
    Opening_Stock_Value_INR DECIMAL(12,2),

    CONSTRAINT fk_opening_product
    FOREIGN KEY (Product_ID)
    REFERENCES products(Product_ID)
);


-- 3. PURCHASES TABLE

CREATE TABLE purchases (
    Purchase_ID VARCHAR(20) PRIMARY KEY,
    Purchase_Date DATE,
    Product_ID VARCHAR(20),
    Supplier_Name VARCHAR(100),
    Quantity_Purchased INT,
    Unit_Cost_INR DECIMAL(12,2),
    Total_Purchase_Cost_INR DECIMAL(12,2),

    CONSTRAINT fk_purchase_product
    FOREIGN KEY (Product_ID)
    REFERENCES products(Product_ID)
);


-- 4. SALES TABLE

CREATE TABLE sales (
    Sale_ID VARCHAR(20) PRIMARY KEY,
    Sale_Date DATE,
    Product_ID VARCHAR(20),
    Quantity_Sold INT,
    Unit_Selling_Price_INR DECIMAL(12,2),
    Discount_Percentage DECIMAL(5,2),
    Discount_Amount_INR DECIMAL(12,2),
    Final_Unit_Price_INR DECIMAL(12,2),
    Total_Revenue_INR DECIMAL(12,2),

    CONSTRAINT fk_sales_product
    FOREIGN KEY (Product_ID)
    REFERENCES products(Product_ID)
);

SHOW TABLES;

-- Total Units Purchased
SELECT
    SUM(Quantity_Purchased) AS Total_Units_Purchased
FROM purchases;

-- Total Units Sold
SELECT
    SUM(Quantity_Sold) AS Total_Units_Sold
FROM sales;

-- Current Stock
SELECT
    (
        (SELECT SUM(Opening_Stock_Quantity)
         FROM opening_inventory)
        +
        (SELECT SUM(Quantity_Purchased)
         FROM purchases)
        -
        (SELECT SUM(Quantity_Sold)
         FROM sales)
    ) AS Current_Stock_Units;

-- Current Inventory value
SELECT
    SUM(
        (
            COALESCE(oi.Opening_Stock_Quantity, 0)
            + COALESCE(p.Total_Purchased, 0)
            - COALESCE(s.Total_Sold, 0)
        ) * pr.Cost_Price_INR
    ) AS Current_Inventory_Value_INR

FROM products pr

LEFT JOIN opening_inventory oi
    ON pr.Product_ID = oi.Product_ID

LEFT JOIN (
    SELECT
        Product_ID,
        SUM(Quantity_Purchased) AS Total_Purchased
    FROM purchases
    GROUP BY Product_ID
) p
    ON pr.Product_ID = p.Product_ID

LEFT JOIN (
    SELECT
        Product_ID,
        SUM(Quantity_Sold) AS Total_Sold
    FROM sales
    GROUP BY Product_ID
) s
    ON pr.Product_ID = s.Product_ID;
    
-- Top 4 Selling Products
SELECT
    p.Product_ID,
    p.Product_Name,
    p.Category,
    SUM(s.Quantity_Sold) AS Total_Units_Sold,
    SUM(s.Total_Revenue_INR) AS Total_Revenue_INR

FROM products p

INNER JOIN sales s
    ON p.Product_ID = s.Product_ID

GROUP BY
    p.Product_ID,
    p.Product_Name,
    p.Category

ORDER BY
    Total_Units_Sold DESC

LIMIT 4;

-- Least 4 selling products
SELECT
    p.Product_ID,
    p.Product_Name,
    p.Category,
    COALESCE(SUM(s.Quantity_Sold), 0) AS Total_Units_Sold,
    COALESCE(SUM(s.Total_Revenue_INR), 0) AS Total_Revenue_INR

FROM products p

LEFT JOIN sales s
    ON p.Product_ID = s.Product_ID

GROUP BY
    p.Product_ID,
    p.Product_Name,
    p.Category

ORDER BY
    Total_Units_Sold ASC

LIMIT 4;

-- Category wise sales analysis
SELECT
    p.Category,
    SUM(s.Quantity_Sold) AS Total_Units_Sold,
    SUM(s.Total_Revenue_INR) AS Total_Revenue_INR,
    ROUND(AVG(s.Discount_Percentage), 2) AS Average_Discount_Percentage

FROM products p

INNER JOIN sales s
    ON p.Product_ID = s.Product_ID

GROUP BY
    p.Category

ORDER BY
    Total_Revenue_INR DESC;
    
-- Products with highest current stock.
SELECT
    pr.Product_ID,
    pr.Product_Name,
    pr.Category,

    COALESCE(oi.Opening_Stock_Quantity, 0)
    + COALESCE(p.Total_Purchased, 0)
    - COALESCE(s.Total_Sold, 0) AS Current_Stock,

    ROUND(
        (
            COALESCE(oi.Opening_Stock_Quantity, 0)
            + COALESCE(p.Total_Purchased, 0)
            - COALESCE(s.Total_Sold, 0)
        ) * pr.Cost_Price_INR,
        2
    ) AS Current_Inventory_Value_INR

FROM products pr

LEFT JOIN opening_inventory oi
    ON pr.Product_ID = oi.Product_ID

LEFT JOIN (
    SELECT Product_ID, SUM(Quantity_Purchased) AS Total_Purchased
    FROM purchases
    GROUP BY Product_ID
) p ON pr.Product_ID = p.Product_ID

LEFT JOIN (
    SELECT Product_ID, SUM(Quantity_Sold) AS Total_Sold
    FROM sales
    GROUP BY Product_ID
) s ON pr.Product_ID = s.Product_ID

ORDER BY Current_Stock DESC;

-- Potential Overstock Products
SELECT
    pr.Product_ID,
    pr.Product_Name,
    pr.Category,

    COALESCE(oi.Opening_Stock_Quantity, 0) AS Opening_Stock,

    COALESCE(p.Total_Purchased, 0) AS Total_Units_Purchased,

    COALESCE(s.Total_Sold, 0) AS Total_Units_Sold,

    (
        COALESCE(oi.Opening_Stock_Quantity, 0)
        + COALESCE(p.Total_Purchased, 0)
        - COALESCE(s.Total_Sold, 0)
    ) AS Current_Stock,

    ROUND(
        (
            COALESCE(oi.Opening_Stock_Quantity, 0)
            + COALESCE(p.Total_Purchased, 0)
            - COALESCE(s.Total_Sold, 0)
        ) * pr.Cost_Price_INR,
        2
    ) AS Current_Inventory_Value_INR

FROM products pr

LEFT JOIN opening_inventory oi
    ON pr.Product_ID = oi.Product_ID

LEFT JOIN (
    SELECT
        Product_ID,
        SUM(Quantity_Purchased) AS Total_Purchased
    FROM purchases
    GROUP BY Product_ID
) p
    ON pr.Product_ID = p.Product_ID

LEFT JOIN (
    SELECT
        Product_ID,
        SUM(Quantity_Sold) AS Total_Sold
    FROM sales
    GROUP BY Product_ID
) s
    ON pr.Product_ID = s.Product_ID

WHERE
    (
        COALESCE(oi.Opening_Stock_Quantity, 0)
        + COALESCE(p.Total_Purchased, 0)
        - COALESCE(s.Total_Sold, 0)
    ) > 0

ORDER BY
    Current_Stock DESC;
    
-- Products with High Stock and Low Sales
SELECT
    pr.Product_ID,
    pr.Product_Name,
    pr.Category,

    COALESCE(p.Total_Purchased, 0) AS Total_Units_Purchased,
    COALESCE(s.Total_Sold, 0) AS Total_Units_Sold,

    (
        COALESCE(oi.Opening_Stock_Quantity, 0)
        + COALESCE(p.Total_Purchased, 0)
        - COALESCE(s.Total_Sold, 0)
    ) AS Current_Stock,

    CASE
        WHEN COALESCE(p.Total_Purchased, 0) = 0 THEN NULL
        ELSE ROUND(
            COALESCE(s.Total_Sold, 0) * 100.0
            / p.Total_Purchased,
            2
        )
    END AS Purchase_Sell_Through_Percentage

FROM products pr

LEFT JOIN opening_inventory oi
    ON pr.Product_ID = oi.Product_ID

LEFT JOIN (
    SELECT Product_ID, SUM(Quantity_Purchased) AS Total_Purchased
    FROM purchases
    GROUP BY Product_ID
) p ON pr.Product_ID = p.Product_ID

LEFT JOIN (
    SELECT Product_ID, SUM(Quantity_Sold) AS Total_Sold
    FROM sales
    GROUP BY Product_ID
) s ON pr.Product_ID = s.Product_ID

WHERE
    COALESCE(p.Total_Purchased, 0) > 0

ORDER BY
    Purchase_Sell_Through_Percentage ASC,
    Current_Stock DESC;





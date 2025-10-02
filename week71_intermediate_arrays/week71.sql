/*
FROSTY FRIDAY Week 71 – Intermediate
https://frostyfriday.org/blog/2023/11/10/week-71-intermediate/
*/

-- 自分の環境に合わせてUSEなんとかする
USE ROLE ACCOUNTADMIN; -- よいこはやっちゃダメ
USE WAREHOUSE COMPUTE_WH;
USE DATABASE FROSTYFRIDAY_DB;
-- CREATE SCHEMA WEEK71;
USE SCHEMA WEEK71;

-- ここから出題通りのセットアップコード

-- Create the Sales table
CREATE OR REPLACE TABLE Sales (
    Sale_ID INT PRIMARY KEY,
    Product_IDs VARIANT --INT
);

-- Inserting sample sales data
INSERT INTO Sales (Sale_ID, Product_IDs) SELECT 1, PARSE_JSON('[1, 3]');-- Products A and C in the same sale
INSERT INTO Sales (Sale_ID, Product_IDs) SELECT 2, PARSE_JSON('[2, 4]');-- Products B and D in the same sale

-- Create the Products table
CREATE OR REPLACE TABLE Products (
    Product_ID INT PRIMARY KEY,
    Product_Name VARCHAR,
    Product_Categories VARIANT --VARCHAR
);

-- Inserting sample data into Products
INSERT INTO Products (Product_ID, Product_Name, Product_Categories) SELECT 1, 'Product A', ARRAY_CONSTRUCT('Electronics', 'Gadgets');
INSERT INTO Products (Product_ID, Product_Name, Product_Categories) SELECT 2, 'Product B', ARRAY_CONSTRUCT('Clothing', 'Accessories');
INSERT INTO Products (Product_ID, Product_Name, Product_Categories) SELECT 3, 'Product C', ARRAY_CONSTRUCT('Electronics', 'Appliances');
INSERT INTO Products (Product_ID, Product_Name, Product_Categories) SELECT 4, 'Product D', ARRAY_CONSTRUCT('Clothing');

-- セットアップが終わったので、内容を確認する
SELECT * FROM Sales;
SELECT * FROM Products;

-- ここから解法

-- まずJSONをFLATTENして展開する
CREATE OR REPLACE TEMPORARY TABLE T1 AS (
    SELECT 
        Sale_ID,
        Product_ID_List.value::NUMBER AS Product_ID
    FROM Sales,
    LATERAL FLATTEN(Sales.Product_IDs) Product_ID_List
);
SELECT * FROM T1;

-- 同じく、配列をFLATTENして展開する
CREATE OR REPLACE TEMPORARY TABLE T2 AS (
    SELECT 
        Product_ID,
        Product_Category_List.value::STRING AS Product_Category
    FROM Products,
    LATERAL FLATTEN(Products.Product_Categories) Product_Category_List
);
SELECT * FROM T2;

-- それらを結合する
CREATE OR REPLACE TEMPORARY TABLE T3 AS (
    SELECT
        T1.Sale_ID,
        T1.Product_ID,
        T2.Product_Category
    FROM T1
    LEFT JOIN T2
    ON T1.Product_ID = T2.Product_ID
);
SELECT * FROM T3;

-- 同じSale_IDでグルーピング。グループの中でそれぞれのカテゴリの個数を数えて、2回以上なら共通のカテゴリと判断する
CREATE OR REPLACE TEMPORARY TABLE T4 AS (
    SELECT
        Sale_ID,
        Product_Category,
        COUNT(Product_Category) AS Product_Category_Count
    FROM T3
    GROUP BY Sale_ID, Product_Category
    HAVING COUNT(Product_Category) > 1
);
SELECT * FROM T4;

-- 結果を出題の指定に寄せるために、ARRAY_AGGで配列化して、表示
SELECT
    T4.Sale_ID,
    ARRAY_AGG(Product_Category) AS Common_Product_Categories
FROM T4
GROUP BY
    Sale_ID
ORDER BY 
    Sale_ID;

-- 共通のカテゴリが2つ以上でも動作するのかテストする
INSERT INTO Sales (Sale_ID, Product_IDs) SELECT 3, PARSE_JSON('[3, 3]');-- Products B and D in the same sale

-- 上記の流れをCTE(Common Table Expressions)で1つのSQLにして、再実行
WITH T1 AS (
    SELECT 
        Sale_ID,
        Product_ID_List.value::NUMBER AS Product_ID
    FROM Sales,
    LATERAL FLATTEN(Sales.Product_IDs) Product_ID_List
),
T2 AS (
    SELECT 
        Product_ID,
        Product_Category_List.value::STRING AS Product_Category
    FROM Products,
    LATERAL FLATTEN(Products.Product_Categories) Product_Category_List
),
T3 AS (
    SELECT
        T1.Sale_ID,
        T1.Product_ID,
        T2.Product_Category
    FROM T1
    LEFT JOIN T2
    ON T1.Product_ID = T2.Product_ID
),
T4 AS (
    SELECT
        Sale_ID,
        Product_Category,
        COUNT(Product_Category) AS Product_Category_Count
    FROM T3
    GROUP BY Sale_ID, Product_Category
    HAVING COUNT(Product_Category) > 1
)
SELECT
    T4.Sale_ID,
    ARRAY_AGG(Product_Category) AS Common_Product_Categories
FROM T4
GROUP BY
    Sale_ID
ORDER BY 
    Sale_ID;


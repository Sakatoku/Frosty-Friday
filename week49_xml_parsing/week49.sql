-- XMLフォーマットの対応
-- https://docs.snowflake.com/en/user-guide/semistructured-data-formats#xml
-- 2025/3/17頃にGAしている！参考：https://docs.snowflake.com/en/release-notes/2025/9_07

-- Frosty Fridayで使うデータベース/スキーマ/ウェアハウスを選択する
USE DATABASE FROSTYFRIDAY_DB;
CREATE OR REPLACE SCHEMA WEEK49;
USE SCHEMA WEEK49;
USE WAREHOUSE COMPUTE_WH;

-- サンプルデータを保存しておくテーブルを作成する
CREATE OR REPLACE TABLE WEEK49 (
    data VARIANT
);

-- WEEK49テーブルにサンプルデータをインサートする
-- COPY INTOでも可
INSERT INTO WEEK49
SELECT PARSE_XML('<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book>
        <title>The Great Gatsby</title>
        <author>F. Scott Fitzgerald</author>
        <year>1925</year>
        <publisher>Scribner</publisher>
    </book>
    <book>
        <title>To Kill a Mockingbird</title>
        <author>Harper Lee</author>
        <year>1960</year>
        <publisher>J. B. Lippincott & Co.</publisher>
    </book>
    <book>
        <title>1984</title>
        <author>George Orwell</author>
        <year>1949</year>
        <publisher>Secker & Warburg</publisher>
    </book>
</library>
');

-- どう格納されたかを確認する
SELECT * FROM WEEK49;

-- 最初の演算子：$
-- 一番最初の要素を引っ張ってくる、みたいな効果
SELECT data:"$" FROM WEEK49;

-- この最初の演算子の結果に沿ってクエリすると…
SELECT
    data:"$"[0]."$"[0]."@" AS tag_name,
    data:"$"[0]."$"[0]."$"::VARCHAR AS title,
FROM WEEK49
UNION SELECT
    data:"$"[1]."$"[0]."@",
    data:"$"[1]."$"[0]."$"::VARCHAR,
FROM WEEK49
UNION SELECT
    data:"$"[2]."$"[0]."@",
    data:"$"[2]."$"[0]."$"::VARCHAR,
FROM WEEK49;

-- これをFLATTENすると…
SELECT *
FROM WEEK49,
TABLE(FLATTEN(INPUT => WEEK49.DATA:"$"));

-- LATERAL FLATTENは半構造化データを使うときのおまじない。今回の範囲ではTABLE(FLATTEN(...))でも同じ
-- LATERALの本質的な解説は：https://zenn.dev/indigo13love/articles/450d4d58654b43
SELECT *
FROM WEEK49,
LATERAL FLATTEN(INPUT => WEEK49.DATA:"$");

-- そこから値を確認してみよう
SELECT XMLGET(book.VALUE, 'title'):"$"::VARCHAR AS title
FROM WEEK49,
LATERAL FLATTEN(INPUT => WEEK49.DATA:"$") AS book;

-- 後はコピペすれば最終的にこうなる
SELECT
    XMLGET(book.VALUE, 'title'):"$"::VARCHAR AS title,
    XMLGET(book.VALUE, 'author'):"$"::VARCHAR AS author,
    XMLGET(book.VALUE, 'year'):"$"::INTEGER AS year,
    XMLGET(book.VALUE, 'publisher'):"$"::VARCHAR AS publisher,
FROM WEEK49,
TABLE(FLATTEN(INPUT => WEEK49.DATA:"$")) AS book;

-- もう一行追加してみる
INSERT INTO WEEK49
SELECT PARSE_XML('<?xml version="1.0" encoding="UTF-8"?>
<library>
    <book>
        <title>グレート・ギャツビー</title>
        <author>野崎孝(翻訳)</author>
        <year>1974</year>
        <publisher>新潮社</publisher>
    </book>
    <book>
        <title>アラバマ物語</title>
        <author>菊池重三郎(翻訳)</author>
        <year>2016</year>
        <publisher>暮しの手帖社</publisher>
    </book>
    <book>
        <title>一九八四年</title>
        <author>高橋和久(翻訳)</author>
        <year>2009</year>
        <publisher>早川書房</publisher>
    </book>
</library>
');

-- 再度、FLATTENした結果を確認
SELECT *
FROM WEEK49,
LATERAL FLATTEN(INPUT => WEEK49.DATA:"$");

-- パースしてみる
SELECT
    SEQ,
    XMLGET(book.VALUE, 'title'):"$"::VARCHAR AS title,
    XMLGET(book.VALUE, 'author'):"$"::VARCHAR AS author,
    XMLGET(book.VALUE, 'year'):"$"::INTEGER AS year,
    XMLGET(book.VALUE, 'publisher'):"$"::VARCHAR AS publisher,
FROM WEEK49,
TABLE(FLATTEN(INPUT => WEEK49.DATA:"$")) AS book;

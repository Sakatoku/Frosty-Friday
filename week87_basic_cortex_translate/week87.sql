-- ❄️ Frosty Friday ❄️
-- Week 87: Basic Cortex Translate
-- About Frosty Friday: https://frostyfriday.org/
-- Challenge Index: https://frostyfriday.org/blog/2024/03/29/week-87-basic/

-- 課題として与えられたテーブル
-- greetingに記載されたメッセージをlanguage_codesに記載された言語コードに翻訳するのが目的
CREATE OR REPLACE TABLE WEEK_87 AS
SELECT 
    'Happy Easter' AS greeting,
    ARRAY_CONSTRUCT('DE', 'FR', 'IT', 'ES', 'PL', 'RO', 'JA', 'KO', 'PT') AS language_codes
;

-- テーブルを確認する
SELECT * FROM WEEK_87;

-- 半構造化データであるARRAYをバラバラにする(LATERAL FLATTEN)
SELECT
  WEEK_87.greeting,
  LF.VALUE AS LANGUAGE_CODE
FROM WEEK_87,
LATERAL FLATTEN(WEEK_87.language_codes) LF;

-- Cortexを使う権限の付与
-- User名がmr_frostyであるとする
USE ROLE ACCOUNTADMIN;
CREATE ROLE cortex_user_role;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE cortex_user_role;
GRANT ROLE cortex_user_role TO USER mr_frosty;

-- Cortex LLM Functionsの一つ、CORTEX.TRANSLATEを使って翻訳する
SELECT
    LF.VALUE AS LANGUAGE_CODE,
    SNOWFLAKE.CORTEX.TRANSLATE(
        WEEK_87.greeting,
        'EN',
        LF.VALUE
    ) AS TRANSLATED_GREETING
FROM
    WEEK_87,
LATERAL FLATTEN(WEEK_87.language_codes) LF;

-- おまけ：Cortex LLM Functionsの一つ、CORTEX.COMPLETEを使うとメッセージに対する応答を生成できる
-- 利用できるモデルは英語版のドキュメントを確認する
-- https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions
SELECT
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3.1-70b',
        'Hello, how are you?'
    ) AS RESPONSE;

-- CORTEX.COMPLETEとCORTEX.TRANSLATEを組み合わせて翻訳したメッセージに対する応答を生成する
WITH
    TRANSLATED AS (
        SELECT
            SNOWFLAKE.CORTEX.TRANSLATE(
                WEEK_87.greeting,
                'EN',
                LF.VALUE
            ) AS TRANSLATED_GREETING
        FROM
            WEEK_87,
        LATERAL FLATTEN(WEEK_87.language_codes) LF
    )
SELECT
    TRANSLATED_GREETING,
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3.1-70b',
        TRANSLATED_GREETING
    ) AS RESPONSE
FROM
    TRANSLATED;

-- おまじない
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;

-- https://app.snowflake.com/marketplace/listing/GZSNZ7F5UH/starschema-covid-19-epidemiological-data
-- データベース名をFFW28_COVID19に変更した想定
-- 含まれている国名、紐づけできそうなコードを確認する
SELECT * FROM FFW28_COVID19.PUBLIC.ECDC_GLOBAL LIMIT 100;
SELECT DISTINCT(COUNTRY_REGION), ISO3166_1 FROM FFW28_COVID19.PUBLIC.ECDC_GLOBAL;
-- ISO 3166-1についてはWikipediaを参照：https://en.wikipedia.org/wiki/ISO_3166-1
-- 今回はISO 3166-1 alpha-2 codeを使いたい！

-- https://app.snowflake.com/marketplace/listing/GZTSZAS2KIM/cybersyn-weather-environment
-- データベース名をFFW28_WEATHERに変更した想定
-- 気象情報
SELECT * FROM FFW28_WEATHER.CYBERSYN.NOAA_WEATHER_METRICS_TIMESERIES LIMIT 100;
SELECT DISTINCT(VARIABLE_NAME) FROM FFW28_WEATHER.CYBERSYN.NOAA_WEATHER_METRICS_TIMESERIES
WHERE VARIABLE_NAME LIKE '%Temperature%' AND VARIABLE_NAME LIKE '%Average%';
-- 観測局
SELECT * FROM FFW28_WEATHER.CYBERSYN.NOAA_WEATHER_STATION_INDEX LIMIT 100;
-- 観測局に含まれている国名を確認
SELECT DISTINCT(COUNTRY_NAME) FROM FFW28_WEATHER.CYBERSYN.NOAA_WEATHER_STATION_INDEX;

-- おまじない
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;

-- Cross-Region Inferenceを有効化する
-- 有効化すると後述するSNOWFLAKE.CORTEX.COMPLETEに与えたデータ(引数)が海外リージョンに飛ぶ可能性があるため、個人情報や会社の機密情報などを扱っている環境では注意すること
USE ROLE ACCOUNTADMIN;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';
USE ROLE SYSADMIN;

-- 試しにSnowflake Cortex LLM Functionsを呼び出してみる
SELECT SNOWFLAKE.CORTEX.COMPLETE('gemma-7b', 'Hello! How are you?');

-- 加工してみる。Cross-Region Inferenceを有効化すればすべてのLLMを利用可能
-- 使えるLLMの一覧：
-- https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions#availability
-- 国名の例：
-- French Guiana
-- Pakistan
-- Tajikistan
-- Poland
-- Wallis and Futuna
SELECT SNOWFLAKE.CORTEX.COMPLETE('gemma-7b', 'Convert following contry name to ISO 3166-1 alpha-2 code: Wallis and Futuna');
SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'Convert following contry name to ISO 3166-1 alpha-2 code: Pakistan');

-- テーブルに適用するには：
SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', CONCAT('Convert following contry name to ISO 3166-1 alpha-2 code: ', COUNTRY_NAME))
    FROM FFW28_WEATHER.CYBERSYN.NOAA_WEATHER_STATION_INDEX
    LIMIT 5;

-- プロンプトエンジニアリング！
SELECT SUBSTRING(SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'You are an assistant that converts country names to ISO 3166-1 alpha-2 codes. Follow these rules:

1. Output ONLY the ISO 3166-1 alpha-2 code (2 characters) for the input country name
2. Do not output any explanatory text or additional information
3. Output only 2 uppercase alphabetic characters
4. If the code is unknown, output "XX"

Sample format:
### Sample Input ###
Japan
### Sample Output ###
JP

### Sample Input ###
United States of America
### Sample Output ###
US

### Actual Input ###
Pakistan'), 2, 2) AS ISO3166_1;

-- データベースとスキーマを指定
USE DATABASE FROSTYFRIDAY_DB;
CREATE OR REPLACE SCHEMA WEEK136;
USE SCHEMA WEEK136;

-- セットアップ：ステップ1
-- Create the seeds table 🌸🌿
CREATE OR REPLACE TABLE seed_packs (
    gardener STRING,
    seeds ARRAY
);

-- セットアップ：ステップ2
-- Insert your spring options🌼🌼
INSERT INTO seed_packs 
SELECT 'Luna', ARRAY_CONSTRUCT(5, 10, 15)
UNION ALL
SELECT 'Sol', ARRAY_CONSTRUCT(7, 8, 9)
UNION ALL
SELECT 'Anna', ARRAY_CONSTRUCT(4, 12, 18)
UNION ALL
SELECT 'Daniel', ARRAY_CONSTRUCT(6, 8, 2);

-- 確認
SELECT * FROM seed_packs;

-- 可変長引数で渡された値をすべて足し合わせる関数
CREATE OR REPLACE PROCEDURE ARRAY_SUM(
  _a INT,
  _b INT DEFAULT 0,
  _c INT DEFAULT 0,
  _d INT DEFAULT 0,
  _e INT DEFAULT 0,
  _f INT DEFAULT 0,
  _g INT DEFAULT 0,
  _h INT DEFAULT 0,
  _i INT DEFAULT 0,
  _j INT DEFAULT 0
)
RETURNS INTEGER
LANGUAGE SQL
AS
BEGIN
    RETURN _a + _b + _c + _d + _e + _f + _g + _h + _i + _j;
END;

-- テーブルの各行にARRAY_SUMを適用するためのストアドプロシージャ
CREATE OR REPLACE PROCEDURE HELP_GARDENER(table_name VARCHAR)
RETURNS TABLE (gardener VARCHAR, total INTEGER)
LANGUAGE SQL
AS
DECLARE
    dynamic_sql VARCHAR := 'SELECT gardener, seeds FROM ' || table_name;
    input RESULTSET;
    output RESULTSET;
BEGIN
    -- 集計中のデータを格納する一時テーブルを作成
    CREATE OR REPLACE TEMP TABLE temp_result (gardener VARCHAR, total INTEGER);

    -- 入力データを取得
    input := (EXECUTE IMMEDIATE :dynamic_sql);

    -- カーソルを取得して各行に対して処理を開始
    LET c1 cursor for input;
    OPEN c1;
    FOR record IN c1 DO
        LET gardener := record.gardener;
        LET seeds := record.seeds;
        LET total;
        -- ここがチャレンジの回答
        CALL ARRAY_SUM(**:seeds) INTO total;
        -- 集計したものを一時テーブルに格納
        INSERT INTO temp_result VALUES (:gardener, :total);
    END FOR;
    CLOSE c1;

    -- 一時テーブルをすべて出力
    output := (SELECT * FROM temp_result);
    RETURN TABLE(output);
END;

-- 最終的な結果を得る
CALL HELP_GARDENER('seed_packs');

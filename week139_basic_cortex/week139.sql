-- データベースとスキーマを指定
USE DATABASE FROSTYFRIDAY_DB;
CREATE OR REPLACE SCHEMA WEEK139;
USE SCHEMA WEEK139;

-- セットアップ(1)
create or replace stage frosty_stage
    url = 's3://frostyfridaychallenges/'
    directory = ( enable = true );

-- ファイル確認
list @frosty_stage;
create or replace file format tmp_format 
    type = csv,
    FIELD_DELIMITER = NONE;
create or replace temporary table data_check
as (
    select $1 as val from @frosty_stage/challenge_139 (file_format => 'tmp_format')
);

-- 内容をチェック
select * from data_check;

-- セットアップ(2)
-- ヘッダー行付き、二重引用符ありの一般的なCSVだと確認できたはず
create or replace file format frosty_csv
    type = csv
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"';
create or replace table week_139 as 
select
    $1 as id,
    $2 as student,
    $3 as rating,
    $4 as review_text
from
    @frosty_stage/challenge_139 (
        file_format=>'frosty_csv'
    )
;

-- 内容をチェック
select * from week_139;

-- 感情分析
SELECT
    *,
    SNOWFLAKE.CORTEX.ENTITY_SENTIMENT(review_text, ['content', 'teaching']),
FROM week_139;

-- データベースとスキーマを指定
USE DATABASE FROSTYFRIDAY_DB;
CREATE OR REPLACE SCHEMA WEEK65;
USE SCHEMA WEEK65;

-- セットアップコード
-- XSウェアハウスで120秒くらいかかるため、課題の指示の通りにLIMITをかけた方がよい
CREATE TABLE PATENTS AS (
    SELECT
        patent_index.patent_id,
        invention_title,
        patent_type,
        application_date,
        document_publication_date,
    FROM US_PATENTS.cybersyn.uspto_contributor_index AS contributor_index
    INNER JOIN
        US_PATENTS.cybersyn.uspto_patent_contributor_relationships AS relationships
        ON contributor_index.contributor_id = relationships.contributor_id
    INNER JOIN
        US_PATENTS.cybersyn.uspto_patent_index AS patent_index
        ON relationships.patent_id = patent_index.patent_id
    WHERE contributor_index.contributor_name ILIKE 'NVIDIA CORPORATION'
        AND relationships.contribution_type = 'Assignee - United States Company Or Corporation'
);

-- 内容確認
SELECT COUNT(*) FROM PATENTS;
SELECT * FROM PATENTS LIMIT 100;

-- UDFを作成する
-- https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-tabular-functions
CREATE OR REPLACE FUNCTION review_patent(patent_type VARCHAR, application_date DATE, publication_date DATE)
RETURNS TABLE (thumb VARCHAR)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
HANDLER = 'Reviewer'
AS
$$
class Reviewer:
    def process(self, patent_type, application_date, publication_date):
        delta_date = publication_date - application_date
        result = '👎Thumbs down'
        if patent_type == 'Reissue':
            if delta_date.days <= 365:
                result = '👍Thumbs up'
        elif patent_type == 'Design':
            # うるう年は考慮しない
            if delta_date.days <= 365 * 2:
                result = '👍Thumbs up'
        else:
            result = '🤔Unknown'
        # 値を1行あたり1つだけ返す場合はタプルの2つ目を空にする
        yield (result,)
$$;

-- 結果を確認する
SELECT
    *
FROM
    PATENTS,
    table(review_patent(PATENTS.patent_type, PATENTS.application_date, PATENTS.document_publication_date))
ORDER BY PATENT_TYPE;

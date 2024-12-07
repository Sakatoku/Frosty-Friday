# Frosty Friday Week 87解説：SnowflakeでLLMを始めよう

この記事は[Frosty Friday Advent Calendar 2024](https://qiita.com/advent-calendar/2024/frostyfriday)の8日目です。  
みんなでFrosty Fridayをやってみよう！  

## Frosy Fridayとは

Frosty Fridayとは「**Snowflakeユーザが、Snowflakeユーザのために作成し、Snowflakeスキルの練習と開発に役立つ**」チャレンジです。  
原文：  
*to help you practice and develop your Snowflake skills, created by Snowflake users, for Snowflake users.*  

[こちらのサイト](https://frostyfriday.org/)で毎週新しいチャレンジが公開されます。簡単な問題もあるのでSnowflake初心者が練習するときにちょうどいいですよ！  

https://frostyfriday.org/

## 解説

今回はWeek 87をやっていきましょう。  
Snowflake CortexというAI/ML/LLMに関する機能群の入門編で、LLMによる翻訳をやってみよう！というチャレンジです！  
AI/ML/LLMを使うのは従来はデータサイエンティストがPythonなどでプログラムを作って…という感じでハードルが高い印象でしたが、Snowflake Cortexは代表的なAI/ML/LLMの機能をSQL文から簡単に呼び出せるようになっています。本当に簡単なのでWeek 87を通じてそれを体験してみましょう！  
もちろん、複雑な課題が対象のときやある課題に特化したいときは従来のようなやり方が必要になると思いますが、それでも色々なところで活用できるはずですよ！  

回答例は[ここ](https://github.com/Sakatoku/Frosty-Friday/tree/main/week87_basic_cortex_translate/week87.sql)にアップロードしてあります。

https://github.com/Sakatoku/Frosty-Friday/tree/main/week87_basic_cortex_translate/week87.sql

まず、テーブルを作成します。  
チャレンジの説明文そのままですね。  

```sql
-- 課題として与えられたテーブル
-- greetingに記載されたメッセージをlanguage_codesに記載された言語コードに翻訳するのが目的
CREATE OR REPLACE TABLE WEEK_87 AS
SELECT 
    'Happy Easter' AS greeting,
    ARRAY_CONSTRUCT('DE', 'FR', 'IT', 'ES', 'PL', 'RO', 'JA', 'KO', 'PT') AS language_codes
;
```

作成されたテーブルを確認してみましょう。  
ARRAYという半構造化データで言語コードが格納されているので、これが1行1行になるように```LATERAL FLATTEN```も試してみます。  

```sql
-- テーブルを確認する
SELECT * FROM WEEK_87;

-- 半構造化データであるARRAYをバラバラにする(LATERAL FLATTEN)
SELECT
  WEEK_87.greeting,
  LF.VALUE AS LANGUAGE_CODE
FROM WEEK_87,
LATERAL FLATTEN(WEEK_87.language_codes) LF;
```

ここからが回答例になります。  
まず、Snowflake Cortexを初めて使うときは権限設定が必要になります。  
データベースロールという機能で権限を取得することになります。  
データベースロールについては少し専門的ですが、[こちらの記事](https://zenn.dev/dataheroes/articles/snowflake-database-role-20240727)で解説されているので気になる方は確認してみてください。  

```sql
-- Cortexを使う権限の付与
-- User名がmr_frostyであるとする
USE ROLE ACCOUNTADMIN;
CREATE ROLE cortex_user_role;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE cortex_user_role;
GRANT ROLE cortex_user_role TO USER mr_frosty;
```

翻訳には```CORTEX.TRANSLATE```という関数を使います。  
Snowflake Cortexの関数はSQL文で使えるようになっているので、テーブルをSELECTしているときに呼び出すことができます。  

```sql
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
```

これで無事にチャレンジクリアです！  

![Challenge Clear](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2917580/937b2efb-11af-509a-d8b3-17509764ba1a.png)

## おまけ

今回のチャレンジでは```CORTEX.TRANSLATE```という翻訳してくれる関数を使うものでしたが、メッセージに対する応答を生成する、ザ・LLMな機能も用意されています。  
これは```CORTEX.COMPLETE```という関数なので、試しに使ってみましょう。  

```sql
-- おまけ：Cortex LLM Functionsの一つ、CORTEX.COMPLETEを使うとメッセージに対する応答を生成できる
-- 利用できるモデルは英語版のドキュメントを確認する
-- https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions
SELECT
    SNOWFLAKE.CORTEX.COMPLETE(
        'llama3.1-70b',
        'Hello, how are you?'
    ) AS RESPONSE;
```

もちろん、```CORTEX.TRANSLATE```と組み合わせることもできます。  
英語しか話せないモデルを使うときなどに応用できますね。  

```sql
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
```

![Combination](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/2917580/7aade74c-e8b9-5f9d-34e6-5c366f6c53b0.png)

## Frosty Fridayを始めよう！

Frosty Fridayの解法を紹介するYouTube番組をやっている[Gakuさんの記事](https://zenn.dev/churadata/articles/cb49f469dc9b56)を参考にして、ぜひチャレンジしてみてください。  

https://zenn.dev/churadata/articles/cb49f469dc9b56

こちらのYouTube番組はゲスト出演者も随時募集しているそうなので、Snowflakeに慣れてきたらぜひ出演を目指してみてくださいね！  

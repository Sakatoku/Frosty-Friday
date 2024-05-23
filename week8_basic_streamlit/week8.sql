-- 今回使うデータベース
use database frostyfriday_db;

-- テストクエリ
select * from frostyfriday_db.public.week8_tbl limit 10;

-- 集計クエリ
select
    date_trunc('week', to_date(payment_date)) as payment_date,
    sum(amount_spent) as amount_spent
from frostyfriday_db.public.week8_tbl
group by 1;

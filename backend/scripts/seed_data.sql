-- 0. 遇错即停（psql 专用）  
\set ON_ERROR_STOP on

BEGIN;

-- 1. 清空 orders、users、products 三张表，并重置所有序列
TRUNCATE TABLE orders, users, products
  RESTART IDENTITY
  CASCADE;

-- 2. 生成用户数据（user_00001 … user_10000）
INSERT INTO users (username)
SELECT
  'user_' || LPAD(generate_series::text, 5, '0')
FROM generate_series(1, 10000);

-- 3. 插入固定演唱会产品（仅 name 和 count）
INSERT INTO products (name, count)
VALUES
  ('周杰伦世界巡回演唱会·北京站', 1000),
  ('周杰伦世界巡回演唱会·上海站', 1000),
  ('周杰伦世界巡回演唱会·广州站', 1000),
  ('周杰伦世界巡回演唱会·深圳站', 1000),
  ('周杰伦世界巡回演唱会·成都站', 1000),
  ('周杰伦世界巡回演唱会·重庆站', 1000),
  ('周杰伦世界巡回演唱会·武汉站', 1000),
  ('周杰伦世界巡回演唱会·南京站', 1000),
  ('周杰伦世界巡回演唱会·杭州站', 1000),
  ('周杰伦世界巡回演唱会·西安站', 1000);

-- 4. 生成更多随机“加场”产品
INSERT INTO products (name, count)
SELECT
  '周杰伦世界巡回演唱会·' ||
  CASE floor(random()*9)
    WHEN 0 THEN '北京'
    WHEN 1 THEN '上海'
    WHEN 2 THEN '广州'
    WHEN 3 THEN '深圳'
    WHEN 4 THEN '成都'
    WHEN 5 THEN '重庆'
    WHEN 6 THEN '武汉'
    WHEN 7 THEN '南京'
    WHEN 8 THEN '杭州'
    ELSE '西安'
  END || '加场',
  (random() * 500 + 500)::int  -- 随机库存 500–1000
FROM generate_series(1, 50);

COMMIT;

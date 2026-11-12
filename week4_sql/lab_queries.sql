-- Session 4 guided lab. Four queries, ten minutes. Query 4 is the point.
-- Open the log first:   duckdb events.duckdb

-- 1. Events per day, then users per day. Write both numbers down.
SELECT occurred_ts::DATE AS day, COUNT(*) AS events
FROM events GROUP BY day ORDER BY day;

SELECT occurred_ts::DATE AS day, COUNT(DISTINCT user_id) AS users
FROM events GROUP BY day ORDER BY day;

-- 2. Every day in October, including the ones with nothing in them.
--    One day comes back 0. Find it and say why.
SELECT c.day, COUNT(DISTINCT e.user_id) AS users
FROM calendar c
LEFT JOIN events e ON e.occurred_ts::DATE = c.day
GROUP BY c.day ORDER BY c.day;

-- 3. Users with three or more applies. Run the condition in WHERE, then in
--    HAVING. One of the two is wrong.
SELECT user_id, COUNT(*) AS applies
FROM events
WHERE lower(event_type) = 'apply'
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY applies DESC;

-- 4. Users who searched but never applied.
--    Try NOT IN first and watch it return nothing.
SELECT user_id FROM users
WHERE user_id NOT IN (
  SELECT user_id FROM events WHERE lower(event_type) = 'apply'
);

--    Then the anti-join, which is the same question answered correctly.
SELECT u.user_id
FROM users u
LEFT JOIN events e
  ON e.user_id = u.user_id AND lower(e.event_type) = 'apply'
WHERE e.user_id IS NULL;

-- 5. If you finish: the same four as one CTE chain, over cleaned rows.
WITH clean AS (
  SELECT DISTINCT event_id, user_id, lower(event_type) AS event_type, occurred_ts
  FROM events
),
searchers AS (SELECT DISTINCT user_id FROM clean WHERE event_type = 'search'),
appliers  AS (SELECT DISTINCT user_id FROM clean WHERE event_type = 'apply')
SELECT s.user_id
FROM searchers s
LEFT JOIN appliers a ON a.user_id = s.user_id
WHERE a.user_id IS NULL;

-- 6. Then count the rows again. They do not match.
SELECT COUNT(*) AS rows, COUNT(DISTINCT event_id) AS distinct_ids FROM events;

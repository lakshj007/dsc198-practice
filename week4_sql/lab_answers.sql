-- Completed guided lab. Raw row counts retain the intentional duplicates.

-- 1. Events and distinct identified users per UTC day.
SELECT occurred_ts::DATE AS day, COUNT(*) AS events,
       COUNT(DISTINCT user_id) AS users
FROM events
GROUP BY day
ORDER BY day;

-- 2. Calendar preserves October 12 even though it has no matching events.
-- COUNT(e.event_id), unlike COUNT(*), counts zero for an unmatched day.
SELECT c.day, COUNT(e.event_id) AS events,
       COUNT(DISTINCT e.user_id) AS users
FROM calendar c
LEFT JOIN events e ON e.occurred_ts::DATE = c.day
GROUP BY c.day
ORDER BY c.day;

-- 3. WHERE filters input events; HAVING filters the resulting user groups.
-- Putting COUNT(*) >= 3 in WHERE fails because aggregation has not happened.
-- Exclude anonymous rows: NULL is not a user.
SELECT user_id, COUNT(*) AS applies
FROM events
WHERE lower(event_type) = 'apply' AND user_id IS NOT NULL
GROUP BY user_id
HAVING COUNT(*) >= 3
ORDER BY applies DESC, user_id;

-- 4a. The supplied NOT IN demonstration: returns nothing because the
-- subquery includes NULL. Nonmatching IDs compare UNKNOWN against that NULL.
SELECT user_id FROM users
WHERE user_id NOT IN (
  SELECT user_id FROM events WHERE lower(event_type) = 'apply'
);

-- 4b. The supplied anti-join: users with no applies, including non-searchers.
SELECT u.user_id
FROM users u
LEFT JOIN events e
  ON e.user_id = u.user_id AND lower(e.event_type) = 'apply'
WHERE e.user_id IS NULL
ORDER BY u.user_id;

-- 4c. To answer the heading literally, also require a search event.
SELECT u.user_id
FROM users u
LEFT JOIN events e
  ON e.user_id = u.user_id AND lower(e.event_type) = 'apply'
WHERE e.user_id IS NULL
  AND EXISTS (
    SELECT 1 FROM events s
    WHERE s.user_id = u.user_id AND lower(s.event_type) = 'search'
  )
ORDER BY u.user_id;

-- 5. The search-without-apply answer as a CTE chain over normalized rows.
-- DISTINCT here removes identical projected rows; it does not guarantee one
-- row per event_id when copies differ in user_id or other retained values.
WITH clean AS (
  SELECT DISTINCT event_id, user_id, lower(event_type) AS event_type, occurred_ts
  FROM events
  WHERE user_id IS NOT NULL
),
searchers AS (SELECT DISTINCT user_id FROM clean WHERE event_type = 'search'),
appliers AS (SELECT DISTINCT user_id FROM clean WHERE event_type = 'apply')
SELECT s.user_id
FROM searchers s
LEFT JOIN appliers a ON a.user_id = s.user_id
WHERE a.user_id IS NULL
ORDER BY s.user_id;

-- 6. Count physical rows versus distinct event IDs.
SELECT COUNT(*) AS rows, COUNT(DISTINCT event_id) AS distinct_ids,
       COUNT(*) - COUNT(DISTINCT event_id) AS extra_rows
FROM events;

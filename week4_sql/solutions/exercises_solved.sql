-- Session 4 suggested set, solved. Post after the session.

-- E1. Applications per campus.
SELECT u.campus,
       COUNT(*)                    AS applies,
       COUNT(DISTINCT e.user_id)   AS users
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE lower(e.event_type) = 'apply'
GROUP BY u.campus
ORDER BY users DESC;

-- E2. The first thing each user did, with a window.
WITH ranked AS (
  SELECT user_id, occurred_ts, lower(event_type) AS event_type,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY occurred_ts) AS n
  FROM events
  WHERE user_id IS NOT NULL
)
SELECT user_id, occurred_ts, event_type FROM ranked WHERE n = 1;

-- E2. The same answer without a window. Aggregate, then join back.
WITH firsts AS (
  SELECT user_id, MIN(occurred_ts) AS first_ts
  FROM events WHERE user_id IS NOT NULL GROUP BY user_id
)
SELECT e.user_id, e.occurred_ts, lower(e.event_type) AS event_type
FROM events e
JOIN firsts f ON f.user_id = e.user_id AND f.first_ts = e.occurred_ts;

-- E3. Days where applies outnumbered searches.
--     The calendar drives the query, so a day with no events appears with two
--     zeros and is excluded by the HAVING, which is the correct treatment.
SELECT c.day,
       COUNT(*) FILTER (WHERE lower(e.event_type) = 'apply')  AS applies,
       COUNT(*) FILTER (WHERE lower(e.event_type) = 'search') AS searches
FROM calendar c
LEFT JOIN events e ON e.occurred_ts::DATE = c.day
GROUP BY c.day
HAVING COUNT(*) FILTER (WHERE lower(e.event_type) = 'apply')
     > COUNT(*) FILTER (WHERE lower(e.event_type) = 'search')
ORDER BY c.day;

-- E4. Signed up in October, nothing in the seven days after.
--     occurred_ts is UTC and signup_ts is Pacific, so signup is converted to
--     UTC before the two are compared. Pacific is UTC-7 in October.
WITH s AS (
  SELECT user_id, signup_ts + INTERVAL 7 HOUR AS signup_utc FROM users
)
SELECT s.user_id
FROM s
LEFT JOIN events e
  ON e.user_id = s.user_id
 AND e.occurred_ts >= s.signup_utc
 AND e.occurred_ts <  s.signup_utc + INTERVAL 7 DAY
WHERE e.user_id IS NULL
ORDER BY s.user_id;

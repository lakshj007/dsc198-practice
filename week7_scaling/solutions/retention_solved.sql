-- Session 7 afternoon query, solved. Run in week4_sql on events.duckdb.

-- Day-1 retention by signup week.
--     occurred_ts is UTC and signup_ts is Pacific. UTC is 7 hours ahead of
--     Pacific in October, so active converts occurred_ts to Pacific before
--     taking the day. DISTINCT drops the repeated rows, and a NULL user_id
--     joins no signup. Days 0 to 6 after October 1 are week 1, 7 to 13 week 2,
--     and 14 to 20 week 3.
WITH signups AS (
  SELECT user_id,
         signup_ts::DATE AS signup_day
  FROM users
),
active AS (
  SELECT DISTINCT user_id,
    (occurred_ts AT TIME ZONE 'UTC'
     AT TIME ZONE 'America/Los_Angeles')
     ::DATE AS day
  FROM events
)
SELECT (s.signup_day - DATE '2026-10-01')
         // 7 + 1 AS signup_week,
       COUNT(*) AS signups,
       COUNT(a.user_id) AS retained,
       ROUND(COUNT(a.user_id) / COUNT(*), 3)
         AS day1_retention
FROM signups s
LEFT JOIN active a
  ON a.user_id = s.user_id
 AND a.day = s.signup_day + 1
GROUP BY signup_week
ORDER BY signup_week;

-- The result.
--     signup_week  signups  retained  day1_retention
--     1            143      67        0.469            67 / 143 = 0.469
--     2            142      60        0.423            60 / 142 = 0.423
--     3            115      54        0.47             54 / 115 = 0.470

-- The same query with occurred_ts::DATE in place of the conversion takes the
-- UTC date, and an event at 5 p.m. Pacific or later carries the next UTC date.
-- That query finds 46, 39, and 36 retained.
--     week 1   67 - 22 missed + 1 false = 46
--     week 2   60 - 22 missed + 1 false = 39
--     week 3   54 - 20 missed + 2 false = 36
-- A missed user has every day-after event at 5 p.m. Pacific or later, and no
-- signup-day event at 5 p.m. or later. A false user has no day-after event,
-- and a signup-day event at 5 p.m. Pacific or later.

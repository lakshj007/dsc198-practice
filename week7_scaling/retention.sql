-- Session 7 afternoon query. The one required query of the quarter, logged
-- like a problem. The answer is in solutions/retention_solved.sql. Write yours
-- first.
-- Open the log in week4_sql first:   duckdb events.duckdb

-- Day-1 retention by signup week.
--     A user is retained on day 1 when the user has at least one event on the
--     Pacific calendar day after the signup day. day1_retention is retained
--     divided by signups, rounded to three places.
--     Week 1 is October 1 to 7, week 2 is October 8 to 14, and week 3 is
--     October 15 to 21. Every signup falls between October 1 and October 20.
--     One row per signup week, with signup_week, signups, retained, and
--     day1_retention.
--     signup_ts is Pacific and occurred_ts is UTC. Some events have no
--     user_id, and some rows repeat. Say in a comment what you did about each
--     before you wrote the query.

-- signup_ts already records Pacific local time. Interpret occurred_ts as UTC,
-- convert it to America/Los_Angeles, then take the date before testing day 1.
-- NULL event user IDs do not match a signup. EXISTS counts each signed-up
-- user at most once, so repeat events cannot inflate the retained count.
-- All event types count; event_type casing does not affect this query.
-- The three signup weeks are fixed October date ranges, not calendar weeks.
WITH signups AS (
  SELECT user_id, signup_ts::DATE AS signup_day,
         CASE
           WHEN signup_ts < TIMESTAMP '2026-10-08' THEN 1
           WHEN signup_ts < TIMESTAMP '2026-10-15' THEN 2
           ELSE 3
         END AS signup_week
  FROM users
  WHERE signup_ts >= TIMESTAMP '2026-10-01'
    AND signup_ts < TIMESTAMP '2026-10-22'
),
retention AS (
  SELECT s.signup_week,
         EXISTS (
           SELECT 1
           FROM events e
           WHERE e.user_id = s.user_id
             AND ((e.occurred_ts AT TIME ZONE 'UTC')
                   AT TIME ZONE 'America/Los_Angeles')::DATE = s.signup_day + 1
         ) AS retained
  FROM signups s
)
SELECT signup_week,
       COUNT(*) AS signups,
       COUNT(*) FILTER (WHERE retained) AS retained,
       ROUND((COUNT(*) FILTER (WHERE retained))::DOUBLE / COUNT(*), 3)
         AS day1_retention
FROM retention
GROUP BY signup_week
ORDER BY signup_week;

-- Recorded result from week4_sql/events.duckdb (DuckDB 1.5.6):
-- signup_week | signups | retained | day1_retention
--           1 |     143 |       67 |          0.469
--           2 |     142 |       60 |          0.423
--           3 |     115 |       54 |          0.470

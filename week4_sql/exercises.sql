-- Session 4 suggested set. Four exercises, not logged and not required.
-- Answers are in solutions/exercises_solved.sql. Write yours first.
-- Counts use the supplied raw log, including duplicate event IDs. Casing is
-- normalized when comparing event types; the source data is left intact.

-- E1. Applications per campus.
--     For each campus, how many apply events and how many distinct users
--     applied. Handle the casing flaw. Sort by users, most first.
SELECT u.campus,
       COUNT(*) AS applies,
       COUNT(DISTINCT e.user_id) AS users
FROM events e
JOIN users u ON u.user_id = e.user_id
WHERE lower(e.event_type) = 'apply'
GROUP BY u.campus
ORDER BY users DESC, u.campus;

-- E2. The first thing each user did.
--     One row per user: user_id, the timestamp of their earliest event, and
--     what type it was. Do it with a window function, then again without one.
-- Anonymous events cannot identify a user. For tied timestamps, choose the
-- smallest event_id, then event_type, so both versions return one row per user.
WITH ranked AS (
  SELECT user_id, occurred_ts, lower(event_type) AS event_type,
         ROW_NUMBER() OVER (
           PARTITION BY user_id
           ORDER BY occurred_ts, event_id, lower(event_type)
         ) AS n
  FROM events
  WHERE user_id IS NOT NULL
)
SELECT user_id, occurred_ts, event_type
FROM ranked
WHERE n = 1
ORDER BY user_id;

-- Without a window: keep events with no earlier event for the same user.
-- DISTINCT collapses repeated copies of the selected event.
SELECT DISTINCT e.user_id, e.occurred_ts, lower(e.event_type) AS event_type
FROM events e
WHERE e.user_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM events earlier
    WHERE earlier.user_id = e.user_id
      AND (earlier.occurred_ts, earlier.event_id, lower(earlier.event_type))
        < (e.occurred_ts, e.event_id, lower(e.event_type))
  )
ORDER BY e.user_id;

-- E3. Days on which applies outnumbered searches.
--     One row per day where the apply count is greater than the search count.
--     Include days with no events at all and say what your query does with them.
-- Calendar days are included before filtering. A day with no events has zero
-- applies and zero searches, so it does not satisfy applies > searches.
-- Days follow the UTC dates of occurred_ts, as in the guided lab.
SELECT c.day,
       COUNT(*) FILTER (WHERE lower(e.event_type) = 'apply') AS applies,
       COUNT(*) FILTER (WHERE lower(e.event_type) = 'search') AS searches
FROM calendar c
LEFT JOIN events e ON e.occurred_ts::DATE = c.day
GROUP BY c.day
HAVING COUNT(*) FILTER (WHERE lower(e.event_type) = 'apply')
     > COUNT(*) FILTER (WHERE lower(e.event_type) = 'search')
ORDER BY c.day;

-- E4. Users who signed up in October and did nothing in the same week.
--     signup_ts is Pacific and occurred_ts is UTC. Say in a comment what you
--     did about that before you wrote the query.
-- Interpret "same week" as the first seven days after signup, following the
-- supplied reference. Use [signup, signup + 7 days), not a calendar week.
-- Interpret signup_ts in America/Los_Angeles and convert it to a naive UTC
-- timestamp before comparing it with the UTC occurred_ts. Filter October
-- using the original local signup date. Events before signup do not count.
WITH signups AS (
  SELECT user_id,
         (signup_ts AT TIME ZONE 'America/Los_Angeles')
           AT TIME ZONE 'UTC' AS signup_utc
  FROM users
  WHERE signup_ts >= TIMESTAMP '2026-10-01'
    AND signup_ts < TIMESTAMP '2026-11-01'
)
SELECT s.user_id
FROM signups s
WHERE NOT EXISTS (
  SELECT 1 FROM events e
  WHERE e.user_id = s.user_id
    AND e.occurred_ts >= s.signup_utc
    AND e.occurred_ts < s.signup_utc + INTERVAL 7 DAY
)
ORDER BY s.user_id;

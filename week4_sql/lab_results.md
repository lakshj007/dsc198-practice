# Week 4 SQL lab results

Validated against the supplied `events.duckdb` using DuckDB 1.5.6. All three
CSV files contain the same rows as their corresponding database tables.
The generator and source data are unchanged.

## Guided lab

1. **Events versus users:** 12,316 event rows across 30 active days. Each active
   day has 135 distinct identified users, giving an overall ratio of about
   3.04 events per daily user. `COUNT(*)` includes anonymous and repeated rows;
   `COUNT(DISTINCT user_id)` ignores NULLs and repeat visits by a user.
2. **Every October day:** the calendar join returns 31 days. October 12 has
   zero events and zero users because the generator intentionally skips it.
3. **Three or more applies:** 232 identified users qualify after normalizing
   event type casing. The original lab also returns a NULL group with 18
   apply rows; anonymous events do not identify a user. `WHERE` filters
   individual rows before grouping, while `HAVING COUNT(*) >= 3` filters
   groups. Putting that aggregate in `WHERE` is invalid.
4. **Search without applying:** the supplied `NOT IN` query returns 0 rows
   because its subquery contains NULL. The anti-join returns 103 users with
   no applications. It does not explicitly require a search, although all
   103 happen to have searched in this dataset. `lab_answers.sql` also gives
   the literal search-without-apply query, which returns those same 103 users.
5. **CTE version:** also returns the same 103 identified users. The original
   CTE query can include a NULL searcher, producing 104 rows; the completed
   query excludes anonymous sessions before joining.
6. **Rows versus events:** 12,316 rows and 12,136 distinct event IDs, a
   difference of 180. `SELECT DISTINCT *` still leaves 12,150 rows because
   some copies differ after casing changes or replacement of user IDs with
   NULL. Removing identical rows alone does not yield one row per event ID.

### Recorded daily counts (UTC)

| Day | Event rows | Distinct identified users |
|---|---:|---:|
| 2026-10-01 | 408 | 135 |
| 2026-10-02 | 415 | 135 |
| 2026-10-03 | 416 | 135 |
| 2026-10-04 | 406 | 135 |
| 2026-10-05 | 419 | 135 |
| 2026-10-06 | 402 | 135 |
| 2026-10-07 | 405 | 135 |
| 2026-10-08 | 402 | 135 |
| 2026-10-09 | 408 | 135 |
| 2026-10-10 | 419 | 135 |
| 2026-10-11 | 419 | 135 |
| 2026-10-12 | 0 | 0 |
| 2026-10-13 | 413 | 135 |
| 2026-10-14 | 415 | 135 |
| 2026-10-15 | 405 | 135 |
| 2026-10-16 | 412 | 135 |
| 2026-10-17 | 416 | 135 |
| 2026-10-18 | 410 | 135 |
| 2026-10-19 | 414 | 135 |
| 2026-10-20 | 419 | 135 |
| 2026-10-21 | 415 | 135 |
| 2026-10-22 | 424 | 135 |
| 2026-10-23 | 405 | 135 |
| 2026-10-24 | 408 | 135 |
| 2026-10-25 | 403 | 135 |
| 2026-10-26 | 404 | 135 |
| 2026-10-27 | 403 | 135 |
| 2026-10-28 | 407 | 135 |
| 2026-10-29 | 411 | 135 |
| 2026-10-30 | 409 | 135 |
| 2026-10-31 | 404 | 135 |

## Exercises

**E1: Applications per campus.** Counts retain raw duplicate rows, normalize
application casing, and exclude anonymous applications through the user join.

| Campus | Application rows | Distinct applicants |
|---|---:|---:|
| UCI | 438 | 87 |
| UCLA | 337 | 77 |
| UCSD | 319 | 76 |
| UCD | 240 | 57 |

**E2: First event per user.** Both implementations return identical results:
400 rows, one per identified user. Ties use timestamp, event ID, then normalized
event type. The version without a window also collapses repeated copies.
The supplied aggregate-and-join reference returns 404 rows because some first
events occur more than once in the raw data.

**E3: Applies outnumber searches.** No days qualify. All 31 calendar days
participate in the aggregation, including October 12 with 0 applies and
0 searches. The final condition excludes that day because 0 is not greater
than 0. Dates follow the lab's UTC convention.

**E4: No activity in the signup week.** 27 users qualify. Following the supplied
reference, "same week" means the seven-day interval starting at signup,
including its start and excluding its end. Signup is interpreted in
`America/Los_Angeles` and converted to UTC before comparison with events.
The October signup filter uses local signup timestamps. A calendar-week
interpretation would answer a different question. Events before signup do not
count, and the query requires no events of any type in the interval.

## Four intentional flaws

- **Repeated event IDs:** 180 extra rows inflate event counts.
- **Mixed casing:** seven raw event-type spellings represent four event types;
  `lower(event_type)` fixes comparisons in queries.
- **Mixed time zones:** signup timestamps are Pacific and event timestamps
  are UTC, so direct comparisons can shift the activity window.
- **Missing user IDs:** 240 rows represent anonymous sessions. NULL affects
  `NOT IN`, joins, and distinct-user counts.

## Verification

All statements in the original lab, completed lab, completed exercises, and
reference solutions execute successfully against the supplied database. The two
completed E2 queries agree exactly, the completed lab anti-join and CTE answers
agree, and the CSV contents match the database, including repeated rows.
Small in-memory fixtures also check E2 timestamp ties, repeated and anonymous
events, and E4 timezone conversion, October filtering, and interval boundaries.

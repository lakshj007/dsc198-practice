# Session 4 lab, instructor copy

Do not upload this folder to Canvas until after the session.

## The four flaws, and what each one does to a query

| Flaw | How it shows | Number in the seeded log |
|---|---|---|
| Rows loaded twice, same `event_id` | `COUNT(*)` exceeds `COUNT(DISTINCT event_id)` | 180 duplicated rows |
| Mixed casing in `event_type` | `GROUP BY event_type` returns seven rows for four values | `Apply`, `APPLY`, `Save` present |
| `occurred_ts` UTC, `signup_ts` Pacific | Any day-to-day comparison is off by up to eight hours | all rows |
| Events with no `user_id` | `NOT IN` returns nothing | 240 rows |

## The numbers the deck and the handbook promise

Checked against the seeded log. If you regenerate with a different seed, check
these again before teaching from them.

| Claim | Where | Value in the log |
|---|---|---|
| Events per day are about three times users per day | slide 9, handbook 3.3 | 3.04 |
| October 12 has no events | slide 10 | 0 events, and the day is in `calendar` |
| The left join returns a row for every October day | slide 10 | 31 rows, with 0 on the 12th |
| `NOT IN` returns nothing | slide 15, handbook 5.5 | 0 rows |
| The anti-join answers the same question correctly | slide 8 | 103 users |
| `COUNT(*)` exceeds `COUNT(DISTINCT event_id)` | slide 19, handbook 8.2 | 12,316 against 12,136 |

## Lab query 4 is the one to arrive at

Students run `NOT IN` first and watch it return nothing, then the anti-join and
get 103. Both queries ask the same question. One of them is defeated by 240
NULLs. That contrast is the lesson and it is worth the last four minutes.

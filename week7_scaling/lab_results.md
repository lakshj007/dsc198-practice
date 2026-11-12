# Week 7 lab progress and retention results

## Day-1 retention: completed

The query in [retention.sql](retention.sql) was written and run against the
supplied Week 4 database before opening the reference solution. The query and
its three output rows are logged together in that file.

| signup_week | signups | retained | day1_retention |
|---|---:|---:|---:|
| 1 | 143 | 67 | 0.469 |
| 2 | 142 | 60 | 0.423 |
| 3 | 115 | 54 | 0.470 |

Week 1 is October 1–7, week 2 is October 8–14, and week 3 is October 15–21.
All 400 signups fall into these cohorts. Retention counts users with any event
on the next Pacific calendar date, rather than within 24 hours after signup.

Signup timestamps already represent Pacific local time. Event timestamps are
interpreted as UTC, converted to `America/Los_Angeles`, and then reduced to
dates. Anonymous events match no signup, and `EXISTS` prevents duplicate
events or multiple visits from counting a user more than once. All event
types count, so mixed event-type casing does not affect retention.

Validation used Python 3.12.9 and DuckDB 1.5.6. Results match the supplied
reference solution exactly. Small in-memory fixtures additionally check the
October 7/8 and 14/15 cohort boundaries, Pacific midnight boundaries, a late
signup followed by an event shortly after midnight, duplicate and anonymous
events, users with no activity, and signups outside the three cohort ranges.
The Week 4 database was opened read-only.

To rerun from the repository root using an environment with the Week 4
requirements installed:

```sh
python - <<'PY'
from pathlib import Path
import duckdb

with duckdb.connect("week4_sql/events.duckdb", read_only=True) as con:
    con.sql(Path("week7_scaling/retention.sql").read_text()).show()
PY
```

## Scaling and Failure modes: completed with labeled assumptions

The parking-permit draft and System Design Handbook were subsequently located
in Downloads. A completed copy of the design is now in
[week6_design/parking_permit_lookup.md](../week6_design/parking_permit_lookup.md),
with the source Downloads files preserved. Its original Capacity and Proposed
design sections were blank, so the added capacity numbers and architecture
are explicitly labeled planning assumptions.

The design uses the draft's 500 requests/second upper bound and assumes a
99:1 read/write ratio, a five-times peak factor, and 400 stored bytes per new
permit. At 100 times growth, the exercise yields 50,000 requests/second and
1.26144 TB of annual storage. The first fixed bottleneck is database reads
(49,500/second against a 10,000/second practice limit); six authoritative shards
address that bottleneck, with the active load balancer next at its 50,000
requests/second limit. The document includes one failure-table row for each
of the three proposed components and states what staff see during an outage.

[scaling_calculations.md](scaling_calculations.md) records the inputs, load/limit
shares, minimum and selected machine counts, storage horizons, and answers to
the four review questions. Machine limits come from handbook Section 10.3;
Parts 10–15 were read for the scaling method, failures, and worked example.
The separate template/example files were not supplied, but their required
headings and table columns are present in the draft and the worked example is
in handbook Part 15.

The review-question answers are a self-check. A human partner exchange and
bringing the document to Session 8 remain classroom activities, and no partner
review is claimed. The new traffic, storage, and architecture assumptions
still need validation against the pair's actual intended workload.

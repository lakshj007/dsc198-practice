# Session 7 lab: scaling, failure modes, and the retention query

Two parts, both in pairs, in the two tutor groups. In the morning each pair
adds two sections to its Session 6 design document. In the afternoon each pair
writes the day-1 retention query against the Session 4 event log.

## Current progress

The retention query is completed in `retention.sql`, with its three output rows
logged below the query. See [lab_results.md](lab_results.md) for results,
verification, and a command to rerun it.

The Scaling and Failure modes sections are completed in
[Parking Permit Lookup](../week6_design/parking_permit_lookup.md), using the
draft and System Design Handbook found in Downloads. The draft's blank Capacity
and Proposed design sections were filled with explicitly labeled assumptions;
[scaling_calculations.md](scaling_calculations.md) records the inputs, arithmetic,
component limits, machine counts, and a self-check against the review questions.
The original Downloads files are unchanged. The paired document swap remains
a classroom activity; no peer review is claimed here.

## Scaling and Failure modes, from 10:25 to 10:50

Each pair adds the Scaling and Failure modes sections to its Session 6
document, under the two headings at the bottom of the document. The template
with those headings is `../week6_design/design_doc_template.md`. Parts 10 to 15
of the System Design Handbook in Tutorials are the reading.

1. Multiply the peak requests per second and the bytes per year in the capacity
   section by 100. The ratio of reads to writes stays the same.
2. For each component named in the proposed design, write the load at a hundred
   times and the limit of one machine. Use the limits in 10.3 of the handbook
   where you have no better number.
3. Divide each load by its limit, a number called the share of the limit. A
   component that can take more machines needs as many machines as its share,
   rounded up. Any other component with a share above 1 breaks, and the
   component with the largest share breaks first.
4. Write the Scaling section, with the component that breaks first, the change
   that fixes that component, and the component that breaks next. If no
   component breaks, write the component with the largest share among the
   components that cannot take more machines, and the growth at which that
   component breaks, which is 100 / share times the current load.
5. Write the Failure modes section, one row for each named component, in the
   four columns of the template.
6. Stop at 10:50 wherever you are.

Read the Scaling and Failure modes sections at the end of
`../week6_design/example_url_shortener.md` after you draft yours.

### The swap, at 10:50

Two pairs exchange documents and mark each other against four questions, until
11:00. Write the answers on the page and hand the page back.

| Section | Question |
|---|---|
| Scaling | Does the section name the component that breaks first, with the load and the limit written as numbers? |
| Scaling | Does the section say what changes in the design, and what breaks next? |
| Failure modes | Is there a row for every component named in the proposed design? |
| Failure modes | Does every row say what the user sees? |

When nothing breaks at a hundred times, the two Scaling questions ask instead
whether the section names the component and the growth from step 4.

## The day-1 retention query, from 12:20 to 1:35

`retention.sql` states the question. The query runs on the Session 4 event log,
opened the same way as in Session 4.

    cd ../week4_sql
    duckdb events.duckdb

Or from Python, `duckdb.connect("events.duckdb")` inside `week4_sql/`. If
`events.duckdb` is gone, `python make_event_log.py` in `week4_sql/` builds the
same log again, because the generator is seeded.

Write the query under the question, run it, and log the query with the three
rows it returns, the same way a problem is logged.

## Files

| File | What it is |
|---|---|
| `retention.sql` | The completed day-1 retention query and its three output rows |
| `solutions/retention_solved.sql` | The answer and the three rows. Open it after you have written your own |
| `lab_results.md` | Retention results, verification, and design-work status |
| `scaling_calculations.md` | Parking-permit scaling inputs, arithmetic, and self-review |

The completed design is in `../week6_design/parking_permit_lookup.md`. The
separate official template and example were not supplied; the downloaded draft
provided their headings and failure-table columns, and the System Design
Handbook's Part 15 provided the reference URL-shortener sections.

## Session 8

The system design mock in Session 8 draws on the design document. Bring the
document.

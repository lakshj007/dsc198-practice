# Session 5 lab, instructor copy

## What each step is for

| Step | What they see | What it teaches |
|---|---|---|
| 1 | Three tasks run in dependency order | Nothing in the file states an order |
| 2 | The run stops, `load` never starts | A failed task blocks what depends on it and nothing else |
| 3 | One failure, then `attempt 2`, then `success` | A retry fixes a transient failure |
| 4 | 15 rows where 5 are correct, run `success` | A retry on a task that appends corrupts data silently |
| 5 | 5 rows, after the same three attempts | Replacing a partition makes the retry harmless |
| 6 | Two clean tasks, in an order nobody wrote | Independent tasks have no order to state, and a scheduler is free to overlap them |

Step 4 is the one to arrive at. If the room gets to five, the lab worked.

`airflow dags test` runs a whole dag in one process, one task at a time, so step 6 shows an order rather than overlap. The order it shows is not the order the file lists, which is the point of the step.

## What goes wrong in the room

- **The retry is on the wrong task.** The log names the task that raised. Point
  at it rather than at their code.
- **Step 4 shows no duplication.** They raised before the write. The task has to
  fail after it has written something.
- **Somebody asks whether this is what companies use.** Yes. Airflow appeared in
  29 per cent of 6,877 data engineer postings surveyed in 2026. What they will
  not have seen is a scheduler in front of it, which Part 1.4 of the handbook
  covers.
- **Somebody asks why the log is filtered.** `run_step.py` drops framework
  traceback and nothing else. `python run_step.py 4 --full` prints Airflow's
  own 225 lines. Show it once.

## The storage numbers, measured

On one million rows of six columns, in the course container.

| Measurement | CSV | Parquet |
|---|---|---|
| One column of six | 0.20 s | 0.003 s |
| All six columns | 0.21 s | 0.04 s |
| File size | 91.6 MB | 56.6 MB |

The size ratio is data dependent. This table has a hash column and a random
float in it. The same measurement on three low-cardinality columns compressed
about two hundred times. Both are Parquet.

## One correction worth knowing before you teach it

Wrapping the partition column in functions does not defeat partition pruning in
DuckDB. It prunes through `year()`, `month()`, `strftime()` and a cast. What
defeats pruning is naming a different column that happens to encode the same
information, which is what S3 does. Other engines differ, so the honest sentence
is that the filter has to reference the partition column and that you should
check your engine.

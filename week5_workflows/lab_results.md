# Week 5 workflow and storage lab results

Completed October 26, 2026 on macOS (Apple Silicon), using Python 3.12.15,
Apache Airflow 3.3.2, and DuckDB 2.0.0 in an isolated virtual environment.
Dependencies were installed from the supplied `requirements.txt`.
The Python scripts and Dockerfile are preserved from the archive. The native
Python setup was used for these runs; the alternative Docker image was not built.

## Six pipeline steps

Each command ran in its own Python process, as directed by the lab. This
resets the in-memory `TABLE` and `ATTEMPTS` between steps. The observations
below come from the captured output in [results/](results/).

| Step | Observed task order and attempts | Final state | Output |
|---|---|---|---|
| 1 | `extract` → `clean` → `load`, once each | success | 5 rows |
| 2 | `extract` → `clean_that_fails`; `load` never starts | failed | `RuntimeError: api down` |
| 3 | `extract` → `clean_flaky` twice → `load` | success | 5 rows |
| 4 | `extract` → `clean` → `load_append_flaky` three times | success | 15 rows; expected 5 |
| 5 | `extract` → `clean` → `load_replace_flaky` three times | success | 5 rows; expected 5 |
| 6 | `extract` → `clean_users` → `clean_events` → `report` | success | 5 events, 5 users |

### 1. Dependency order

`load(clean(extract()))` supplies task outputs as inputs to the next task.
Airflow records those dependencies and runs extract before clean, then load.
The cleaned events use lowercase `apply`, and the destination has five rows.

### 2. A failed task blocks its dependent task

`extract` succeeds, but `clean_that_fails` raises `RuntimeError("api down")`.
There is no retry configured on that task, so `load` never starts and the DAG
run fails. The successful upstream extraction is not undone.

### 3. A retry recovers a transient failure

`clean_flaky` fails on attempt 1 and succeeds on attempt 2. Only that task is
retried; extract runs once and load runs once after clean succeeds. `retries=2`
allows two additional attempts after the first, although this step needs only
one retry. Load reports five rows.

### 4. A successful retry can corrupt the destination

`load_append_flaky` appends five rows **before** raising on each of its first
two attempts. The third attempt appends another five rows and succeeds, leaving
15 rows. A successful DAG means the tasks finished successfully; it does not
prove the destination contains the right data. Retrying an append repeats its
side effect.

I also ran `python run_step.py 4 --full` and inspected all 174 lines of that
run's output. The traceback ends at the deliberate `RuntimeError` in
`load_append_flaky`, after `TABLE.extend(rows)`. The log records two
`up_for_retry` transitions, a third load attempt, 15 rows, and the final
`DagRun Finished ... state=success`. Filtering this full log with the supplied
`readable()` function produces the same step 4 transcript in `results/step4.txt`.

### 5. Replacing the day makes the retry idempotent

`load_replace_flaky` removes rows for `2026-10-24` before writing that day's
five rows. Each retry replaces that same partition, so the final attempt leaves
five rows rather than 15. Rows from other days are retained by the filter.
The desired destination state is the same after one successful write or
several repeated writes of the same input.

This is an in-memory teaching example. A persistent implementation would need
an atomic partition replacement or transaction; the list and counter here
demonstrate behavior within the lab's single-process DAG test.

### 6. Independent tasks have no required order

Both cleaning tasks depend on extract, and report depends on both cleaners.
There is no dependency from one cleaner to the other. In this run,
`clean_users` ran first even though `clean_events(rows)` appears first in the
report call. `airflow dags test` runs these tasks sequentially; this log
demonstrates an allowed order, not actual concurrency. A scheduler with
available worker capacity could overlap the two independent tasks.

## Storage exercises

`python storage_lab.py` generated 1,000,000 rows with six columns. Timings
below are the script's best of three measurements, rounded to milliseconds.
They are local measurements and can vary with hardware, caching, versions,
and the generator's unseeded random score column.

| Measurement | Parquet | CSV |
|---|---:|---:|
| S1: distinct event types, one column | 0.001 s | 0.050 s |
| S1: `COUNT(*), MAX(score), MAX(session_id)` | 0.000 s | 0.053 s |
| File size, decimal MB | 56.2 MB | 91.6 MB |

Parquet occupies about 61% of the CSV size for this generated dataset.
The script labels its second query "all six columns," but that query only
references `score` and `session_id` plus a row count. It is not a benchmark
forcing all six columns to be read. The displayed 0.000 s is a rounded time,
not literally zero work; optimizations can also avoid a full scan.

### S2–S4. Partition pruning

There are 31 day partitions with one Parquet file per day. Each query returns
**32,166 rows** for October 24, 2026.

| Exercise | Filter | Files read |
|---|---|---:|
| S2 | `day = DATE '2026-10-24'` | 1 of 31 |
| S3 | `occurred_ts::DATE = DATE '2026-10-24'` | 31 of 31 |
| S4 | `year(day) = 2026 AND month(day) = 10 AND day(day) = 24` | 1 of 31 |

The directory partition key is `day`. S2 uses that key directly, allowing
DuckDB to skip 30 files. S3 references the timestamp column inside the files;
it returns the same rows but does not prune the directory partitions in this
run. S4 still references `day`, and DuckDB can evaluate the date functions
against the partition values to prune those files. The query plans show why
the amount of work differs even when the answers agree.

## Verification

- All six DAGs ran through Airflow, with the expected intentional failure in
  step 2, retry counts, final states, and printed row counts checked.
- The full step 4 log agrees with the readable transcript.
- Both storage formats contain 1,000,000 rows and have matching aggregate
  hashes over all six columns, checking that the benchmark uses equivalent data.
- All three partition queries return the same 32,166-row count; their
  `EXPLAIN ANALYZE` output confirms file counts of 1, 31, and 1.

The supplied `run_step.py` reports the DAG state in its output but does not
propagate a failed DAG as a nonzero process exit. These checks inspect the
reported state rather than treating the wrapper's exit status as success.
Generated CSV/Parquet data, Airflow databases and configuration, and runtime
logs stay local; the committed results are the small readable transcripts.

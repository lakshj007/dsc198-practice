# Session 4 lab: the event log

Ten minutes in class. Everything else here is the suggested set.

## Completed work

- `lab_answers.sql`: completed lab queries, including the NULL demonstration
  and the search-without-apply answer.
- `exercises.sql`: answers to all four exercises, with both versions of E2.
- [Lab results](lab_results.md): recorded counts, explanations, and assumptions.

The original `lab_queries.sql`, generator, datasets, and instructor reference
files in `solutions/` are preserved from the supplied archive.

To run the completed queries from the repository root using Python:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r week4_sql/requirements.txt
cd week4_sql
python - <<'PY'
from pathlib import Path
import duckdb

with duckdb.connect("events.duckdb", read_only=True) as con:
    for filename in ("lab_answers.sql", "exercises.sql"):
        print(f"\n{filename}")
        for number, statement in enumerate(
            con.extract_statements(Path(filename).read_text()), start=1
        ):
            print(f"Query {number}")
            con.sql(statement.query).show()
PY
```

The database is already included; rebuilding it is optional. The `duckdb`
terminal commands below require the DuckDB CLI installed separately from its
Python package. Run the generator from this directory if rebuilding, because
it writes its outputs in the current working directory.

## Build the log

    pip install duckdb
    python make_event_log.py

That writes `events.duckdb` and three CSVs beside it. The generator is seeded,
so everybody in the room gets the same log.

| Table | One row is | Columns |
|---|---|---|
| `users` | A person who signed up | `user_id`, `signup_ts`, `campus`, `program` |
| `events` | One thing a person did | `event_id`, `user_id`, `event_type`, `occurred_ts`, `platform` |
| `calendar` | One day in October, whether or not anything happened | `day` |

400 users and about 12,000 events across October 2026.

## Open it

    duckdb events.duckdb

Or from Python:

    import duckdb
    con = duckdb.connect("events.duckdb")
    con.sql("SELECT COUNT(*) FROM events").show()

If you were given the CSVs instead, DuckDB reads them where they sit:

    SELECT COUNT(*) FROM 'events.csv';

## Files

| File | What it is |
|---|---|
| `make_event_log.py` | Builds the log. Run once |
| `lab_queries.sql` | The six lab queries. Query 4 is the point |
| `exercises.sql` | The suggested set, four completed exercises |
| `lab_answers.sql` | Completed guided lab with explanatory comments |
| `lab_results.md` | Recorded results and data-quality observations |
| `requirements.txt` | Python dependency used to validate the queries |
| `solutions/` | Answers. Open after you have written your own |

## The log is deliberately flawed

Four things are wrong with it, and finding them is Part 8 of the SQL handbook.
Do not fix the generator. These flaws are the material.

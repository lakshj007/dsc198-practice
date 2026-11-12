"""Session 5 lab. A three-task pipeline, and the two ways it goes wrong.

Run one step:      python run_step.py 1
                   python run_step.py 4
See the real log:  python run_step.py 4 --full

Step 1 is the pipeline working. Steps 2 to 6 are the lab.
"""
from datetime import timedelta
from airflow.sdk import dag, task

# Stands in for a database table so the lab needs no database.
TABLE = []
ATTEMPTS = {"n": 0}
DAY = "2026-10-24"


def rows_for(day):
    return [{"day": day, "user_id": u, "event_type": "APPLY" if u % 3 else "apply"}
            for u in range(1, 6)]


# ---------------------------------------------------------------- step 1
@task
def extract(day=DAY):
    return rows_for(day)


@task
def clean(rows):
    seen, out = set(), []
    for r in rows:
        key = (r["day"], r["user_id"], r["event_type"].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append({**r, "event_type": r["event_type"].lower()})
    return out


@task
def load(rows):
    TABLE.extend(rows)
    print("rows in table:", len(TABLE))
    return len(TABLE)


@dag(schedule=None, catchup=False)
def step1():
    """Three tasks, one dag. Nothing in this file states the order."""
    load(clean(extract()))


step1()


# ---------------------------------------------------------------- step 2
@task
def clean_that_fails(rows):
    raise RuntimeError("api down")


@dag(schedule=None, catchup=False)
def step2():
    """The middle task fails. Note which tasks ran and which never started."""
    load(clean_that_fails(extract()))


step2()


# ---------------------------------------------------------------- step 3
@task(retries=2, retry_delay=timedelta(seconds=1))
def clean_flaky(rows):
    ATTEMPTS["n"] += 1
    if ATTEMPTS["n"] < 2:
        raise RuntimeError("api down")
    print("attempts:", ATTEMPTS["n"])
    return clean.function(rows)


@dag(schedule=None, catchup=False)
def step3():
    """A retry recovers a task that failed once."""
    load(clean_flaky(extract()))


step3()


# ---------------------------------------------------------------- step 4
@task(retries=2, retry_delay=timedelta(seconds=1))
def load_append_flaky(rows):
    """Not idempotent. It writes, and then it fails."""
    TABLE.extend(rows)
    ATTEMPTS["n"] += 1
    if ATTEMPTS["n"] < 3:
        raise RuntimeError("connection dropped after the write")
    print("attempts:", ATTEMPTS["n"], "rows in table:", len(TABLE), " <- expected 5")
    return len(TABLE)


@dag(schedule=None, catchup=False)
def step4():
    """Green dag, tripled rows, no error anywhere."""
    load_append_flaky(clean(extract()))


step4()


# ---------------------------------------------------------------- step 5
@task(retries=2, retry_delay=timedelta(seconds=1))
def load_replace_flaky(rows, day=DAY):
    """Idempotent. The day is removed before it is written."""
    global TABLE
    TABLE = [r for r in TABLE if r["day"] != day]
    TABLE.extend(rows)
    ATTEMPTS["n"] += 1
    if ATTEMPTS["n"] < 3:
        raise RuntimeError("connection dropped after the write")
    print("attempts:", ATTEMPTS["n"], "rows in table:", len(TABLE), " <- expected 5")
    return len(TABLE)


@dag(schedule=None, catchup=False)
def step5():
    """Same failure, same retries, and the count does not move."""
    load_replace_flaky(clean(extract()))


step5()


# ---------------------------------------------------------------- step 6
@task
def clean_events(rows):
    return clean.function(rows)


@task
def clean_users(rows):
    return sorted({r["user_id"] for r in rows})


@task
def report(a, b):
    print("events:", len(a), " users:", len(b))


@dag(schedule=None, catchup=False)
def step6():
    """Two tasks with no dependency between them. Read the log for the order."""
    rows = extract()
    report(clean_events(rows), clean_users(rows))


step6()

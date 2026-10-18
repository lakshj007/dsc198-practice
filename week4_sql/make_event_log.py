"""Build the DSC 198 event log: users, events, calendar, in DuckDB and CSV.

The log is deliberately flawed. Part 8 of the SQL handbook is about finding the
flaws, so do not clean them here.

    python make_event_log.py            # writes events.duckdb and three CSVs
"""
import duckdb, os, random, datetime as dt

random.seed(198)                       # same log for everybody, every time

N_USERS   = 400
MONTH     = (dt.date(2026, 10, 1), dt.date(2026, 10, 31))
EMPTY_DAY = dt.date(2026, 10, 12)      # nothing happens on this day, on purpose
CAMPUSES  = ["UCSD", "UCLA", "UCI", "UCD"]
PROGRAMS  = ["DS", "CS", "MATH", "COGS", "ECON"]
TYPES     = ["view", "search", "apply", "save"]
PLATFORMS = ["web", "ios", "android"]

def working_days():
    d, out = MONTH[0], []
    while d <= MONTH[1]:
        out.append(d); d += dt.timedelta(days=1)
    return out

def build():
    days = working_days()
    open_days = [d for d in days if d != EMPTY_DAY]

    # users. signup_ts is LOCAL Pacific time. That is flaw three.
    users = []
    for uid in range(1, N_USERS + 1):
        d = random.choice(days[:20])
        ts = dt.datetime.combine(d, dt.time(random.randrange(7, 23), random.randrange(60)))
        users.append((uid, ts, random.choice(CAMPUSES), random.choice(PROGRAMS)))

    # A quarter of the users never apply. That is what the anti-join finds.
    appliers = set(random.sample(range(1, N_USERS + 1), int(N_USERS * 0.75)))

    # About 135 users are active on a given day and each does two to four things,
    # so events per day run about three times users per day.
    events, eid = [], 1
    for d in open_days:
        for uid in random.sample(range(1, N_USERS + 1), 135):
            for _ in range(random.choice([2, 3, 3, 4])):
                pool = TYPES if uid in appliers else [t for t in TYPES if t != "apply"]
                w = [55, 20, 15, 10][:len(pool)]
                t = random.choices(pool, weights=w)[0]
                ts = dt.datetime.combine(d, dt.time(random.randrange(0, 24),
                                                    random.randrange(60), random.randrange(60)))
                events.append([eid, uid, t, ts, random.choice(PLATFORMS)])
                eid += 1

    # flaw one: some events were loaded twice, same event_id and all
    for e in random.sample(events, 180):
        events.append(list(e))

    # flaw two: casing drifts on some apply and save rows
    for e in events:
        if e[2] == "apply" and random.random() < 0.12:
            e[2] = random.choice(["Apply", "APPLY"])
        elif e[2] == "save" and random.random() < 0.08:
            e[2] = "Save"

    # flaw four: events from logged-out sessions have no user_id
    for e in random.sample(events, 240):
        e[1] = None

    random.shuffle(events)
    return users, events, days

def main():
    users, events, days = build()
    for f in ("events.duckdb", "events.duckdb.wal"):
        if os.path.exists(f):
            os.remove(f)
    con = duckdb.connect("events.duckdb")
    con.execute("CREATE TABLE users(user_id INTEGER, signup_ts TIMESTAMP, campus VARCHAR, program VARCHAR)")
    con.execute("CREATE TABLE events(event_id INTEGER, user_id INTEGER, event_type VARCHAR,"
                " occurred_ts TIMESTAMP, platform VARCHAR)")
    con.execute("CREATE TABLE calendar(day DATE)")
    con.executemany("INSERT INTO users VALUES (?,?,?,?)", users)
    con.executemany("INSERT INTO events VALUES (?,?,?,?,?)", events)
    con.executemany("INSERT INTO calendar VALUES (?)", [(d,) for d in days])
    for t in ("users", "events", "calendar"):
        con.execute(f"COPY {t} TO '{t}.csv' (FORMAT CSV, HEADER)")
    n_users, n_events = con.execute("SELECT (SELECT COUNT(*) FROM users), (SELECT COUNT(*) FROM events)").fetchone()
    con.close()
    print(f"events.duckdb written: {n_users} users, {n_events} events")
    print("users.csv, events.csv, calendar.csv written beside it")

if __name__ == "__main__":
    main()

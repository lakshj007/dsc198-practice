"""Session 5 storage exercises. Builds a million rows, then measures.

    python storage_lab.py

Writes ev.csv, ev.parquet and events/ into this folder, prints four numbers,
and leaves the files so you can query them yourself.
"""
import duckdb, os, time, shutil

ROWS = 1_000_000

def build(con):
    con.execute(f"""CREATE OR REPLACE TABLE ev AS
      SELECT i AS event_id,
             (i * 2654435761 % 400000) + 1 AS user_id,
             CASE i % 4 WHEN 0 THEN 'apply' WHEN 1 THEN 'view'
                        WHEN 2 THEN 'search' ELSE 'save' END AS event_type,
             TIMESTAMP '2026-10-01 00:00:00' + INTERVAL ((i * 231) % 2678400) SECOND AS occurred_ts,
             md5(CAST(i AS VARCHAR)) AS session_id,
             random() AS score
      FROM generate_series(1, {ROWS}) t(i)""")

def timed(con, sql, n=3):
    best = 9e9
    for _ in range(n):
        s = time.time(); con.execute(sql).fetchall(); best = min(best, time.time() - s)
    return best

def main():
    con = duckdb.connect()
    build(con)
    shutil.rmtree('events', ignore_errors=True)
    con.execute("COPY ev TO 'ev.csv' (FORMAT CSV, HEADER)")
    con.execute("COPY ev TO 'ev.parquet' (FORMAT PARQUET)")
    con.execute("COPY (SELECT *, occurred_ts::DATE AS day FROM ev) TO 'events' "
                "(FORMAT PARQUET, PARTITION_BY (day))")

    print("S1  one column of six")
    print("      parquet %.3f s     csv %.3f s"
          % (timed(con, "SELECT COUNT(DISTINCT event_type) FROM 'ev.parquet'"),
             timed(con, "SELECT COUNT(DISTINCT event_type) FROM 'ev.csv'")))
    print("    all six columns")
    print("      parquet %.3f s     csv %.3f s"
          % (timed(con, "SELECT COUNT(*), MAX(score), MAX(session_id) FROM 'ev.parquet'"),
             timed(con, "SELECT COUNT(*), MAX(score), MAX(session_id) FROM 'ev.csv'")))
    print("    file size")
    print("      parquet %.1f MB     csv %.1f MB"
          % (os.path.getsize('ev.parquet')/1e6, os.path.getsize('ev.csv')/1e6))

    q = ("SELECT COUNT(*) FROM read_parquet('events/**/*.parquet', hive_partitioning=true) "
         "WHERE day = DATE '2026-10-24'")
    plan = con.execute("EXPLAIN ANALYZE " + q).fetchall()[0][1]
    read = [l.strip(' │') for l in plan.splitlines() if 'Files' in l]
    print("\nS2  one day out of a partitioned table")
    for l in read:
        print("     ", l)

    q3 = ("SELECT COUNT(*) FROM read_parquet('events/**/*.parquet', hive_partitioning=true) "
          "WHERE occurred_ts::DATE = DATE '2026-10-24'")
    plan3 = con.execute("EXPLAIN ANALYZE " + q3).fetchall()[0][1]
    read3 = [l.strip(' │') for l in plan3.splitlines() if 'Files' in l]
    print("\nS3  the same day, asked for through a different column")
    for l in read3:
        print("     ", l)

    q4 = ("SELECT COUNT(*) FROM read_parquet('events/**/*.parquet', hive_partitioning=true) "
          "WHERE year(day) = 2026 AND month(day) = 10 AND day(day) = 24")
    plan4 = con.execute("EXPLAIN ANALYZE " + q4).fetchall()[0][1]
    read4 = [l.strip(' │') for l in plan4.splitlines() if 'Files' in l]
    print("\nS4  the partition column, wrapped in functions")
    for l in read4:
        print("     ", l)
    print("\n    Three queries, one answer, and three different amounts of work.")
    print("    S3 names a column that is not the partition column, so nothing can")
    print("    be skipped. S4 wraps the partition column in functions and DuckDB")
    print("    prunes anyway. Not every engine does. Check yours.")

if __name__ == "__main__":
    main()

# Session 5 lab: a pipeline that fails and recovers

Eighteen minutes in class. Six steps, and steps 4 and 5 are the point.

## Completed work

All six steps and the storage exercises have been run. See
[lab_results.md](lab_results.md) for the answers, measured results, and the
environment used, and [results/](results/) for captured command output.
Step 4 was also run with `--full` and its traceback and final state inspected.
The supplied pipeline, runner, storage script, and instructor notes are
unchanged so the intentional failures can be reproduced.

The runs used a Python 3.12 virtual environment. To create one with `uv` from
the repository root:

```sh
cd week5_workflows
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Then run the commands below from this folder. Generated storage files, Airflow
state, and the virtual environment are ignored by Git.

## Setup

Two ways. Use the container if the Airflow install fails on your machine.

    pip install -r requirements.txt
    python run_step.py 1

Or build the image from the `Dockerfile` in this folder and start a container
here, which puts this folder inside the container as `/labs`. Run the steps
from inside it.

    docker build -t dsrocks:fall2026 .
    docker run -it --rm -v "$PWD":/labs dsrocks:fall2026

The first run creates an Airflow database in this folder and takes a few
seconds. Every run after that is immediate. There is no server to start, no
account to create and nothing to configure. `run_step.py` points Airflow at this
folder, so `pipeline.py` beside it is the dag file.

## The six steps

Each step is a dag in `pipeline.py`. Run one at a time.

    python run_step.py 1     # three tasks, one dag. Read the order
    python run_step.py 2     # the middle task fails. Which task never started?
    python run_step.py 3     # a retry recovers it
    python run_step.py 4     # the load appends and then fails. Count the rows
    python run_step.py 5     # the load replaces the day. Count them again
    python run_step.py 6     # two tasks with no dependency between them

Step 4 prints 15 rows where 5 are correct, and the run finishes in state
`success`. Nothing errors. That is the failure worth understanding: a retry on a
task that appends triples the data and reports that all is well.

    step4
      extract              attempt 1
      clean                attempt 1
      load_append_flaky    attempt 1
           failed, RuntimeError: connection dropped after the write
      load_append_flaky    attempt 2
           failed, RuntimeError: connection dropped after the write
      load_append_flaky    attempt 3
           attempts: 3 rows in table: 15  <- expected 5
      run finished: success

Step 5 is the same failure and the same retries, with the day removed before it
is written. It prints 5.

## Reading the real log

`run_step.py` prints the task order, every attempt, the error that ended each
attempt, anything the step printed, and the final state. Airflow's own log for
one of these runs is about 225 lines, roughly two thirds of it framework
traceback. To see it:

    python run_step.py 4 --full

Nothing is summarised or reworded on the way through, so the short form and
`--full` never disagree. Read `--full` at least once. In a job you will be
reading that one.

## Storage exercises

    python storage_lab.py

Builds a million rows, writes them three ways, and prints four measurements:
Parquet against CSV on one column and on all six, the file sizes, and how many
files each of three queries reads.

The three partition queries return the same answer and do different amounts of
work. S2 names the partition column and reads one file of thirty-one. S3 asks
for the same day through a different column and reads all thirty-one. S4 wraps
the partition column in functions, and DuckDB prunes anyway.

## Files

| File | What it is |
|---|---|
| `pipeline.py` | The six steps, as six dags |
| `run_step.py` | Runs one step and filters the log |
| `storage_lab.py` | The measurements |
| `requirements.txt` | The two packages, for a virtual environment |
| `Dockerfile` | Builds the container, instead of installing the packages |
| `solutions/` | Worked answers. Open after you have run the steps |
| `lab_results.md` | Completed observations and storage results |
| `results/` | Captured output from all six steps and the storage lab |

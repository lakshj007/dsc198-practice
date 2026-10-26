"""Run one step of the Session 5 lab and print only what the step shows.

    python run_step.py 4          the readable version
    python run_step.py 4 --full   Airflow's own log, about 225 lines

Airflow prints roughly 225 lines for a three-task run, and about two thirds of
that is framework traceback. This keeps the task order, every attempt, why each
attempt failed, anything the step printed, and the final state. Nothing is
summarised or reworded, so --full and the short form never disagree.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

STRUCTURED = re.compile(r'\[(info|debug|warning|error)\s+\]')
START = re.compile(r'\[DAG TEST\] starting task_id=(\S+)')
RAISED = re.compile(r'^([A-Za-z_]\w*(?:Error|Exception)): (.*)$')
STATE = re.compile(r'state=(success|failed)')
NOISE = re.compile(r'^(Task start$|Dag name:|Task:<|Task instance |Task operator:|'
                   r'Failure caused by |Previous state|Current task name|'
                   r'Dag information:|Failed with message:|DagRun failed|'
                   r'Dag run |DagRun Finished|Marking |No tasks to run)')


def readable(log):
    out, attempts, pending, state = [], {}, None, None
    in_traceback = started = False
    for line in log:
        stripped = line.strip()

        if stripped.startswith('Traceback (most recent call last)'):
            in_traceback = True          # swallow the frames, keep the error they end in
            continue
        if in_traceback:
            m = RAISED.match(stripped)
            if m:
                in_traceback = False
                pending = 'failed, %s: %s' % (m.group(1), m.group(2))
            continue

        m = START.search(line)
        if m:
            started = True
            task_id = m.group(1)
            attempts[task_id] = attempts.get(task_id, 0) + 1
            if pending:
                out.append('       ' + pending)
                pending = None
            out.append('  %-20s attempt %d' % (task_id, attempts[task_id]))
            continue

        m = STATE.search(line)
        if m:
            state = m.group(1)
        if STRUCTURED.search(line) or NOISE.match(stripped) or not stripped:
            continue
        if not started:
            continue          # startup warnings, before any task has run
        out.append('       ' + stripped)

    if pending:
        out.append('       ' + pending)
    out.append('  run finished: %s' % (state or 'unknown'))
    return out


def main():
    step = sys.argv[1] if len(sys.argv) > 1 else '1'
    env = dict(os.environ)
    env['AIRFLOW_HOME'] = HERE
    env['AIRFLOW__CORE__DAGS_FOLDER'] = HERE      # pipeline.py beside this file is the dag
    env['AIRFLOW__CORE__LOAD_EXAMPLES'] = 'False'

    if not os.path.exists(os.path.join(HERE, 'airflow.db')):
        print('first run, setting up the Airflow database. This takes a few seconds.')
        subprocess.run(['airflow', 'db', 'migrate'], env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    finished = subprocess.run(['airflow', 'dags', 'test', 'step' + step],
                              capture_output=True, text=True, env=env)
    log = (finished.stdout + finished.stderr).split('\n')
    if '--full' in sys.argv:
        print('\n'.join(log))
        return
    print('step' + step)
    print('\n'.join(readable(log)))


if __name__ == "__main__":
    main()

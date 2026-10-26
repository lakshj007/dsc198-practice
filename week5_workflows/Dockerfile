# The DSC 198 Week 5 container. Airflow and DuckDB, ready to run.
#
# Week 5 installs Airflow, which is the one install in this course likely to
# fail on a laptop. This image avoids that. Docker Desktop is already installed
# for Week 3, so nothing new is needed.
#
# This file is self contained. Download it on its own, put it in any folder,
# and build the image from that folder.
#     docker build -t dsrocks:fall2026 .
#
# Run it from the folder holding the Week 5 code, which appears inside the
# container as /labs.
#     docker run -it --rm -v "$PWD":/labs dsrocks:fall2026
#
# The lab files stay on your own computer and the container holds the tools,
# so anything you write during a lab is still there after the container is
# deleted.

FROM python:3.12-slim

WORKDIR /labs

# The same two packages as requirements.txt beside this file, which is what a
# student working in a virtual environment installs instead. Change both
# together.
RUN pip install --no-cache-dir \
        "duckdb>=1.0" \
        "apache-airflow>=3.0,<4"

CMD ["bash"]

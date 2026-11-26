#!/usr/bin/env python3
"""Validate the dbt project: full `dbt build` with proxy vars unset.

Run from the repo root (as the daily cron does via run.sh). dbt must run
with its working directory inside dbt/: profiles.yml attaches
../data/ridership.sqlite relative to the working directory, so running
from the repo root fails with "Unable to open database". The proxy vars
are stripped because DuckDB 2.x cannot parse this machine's credentialed
http_proxy (see dbt/README.md).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = {k: v for k, v in os.environ.items()
       if k not in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY")}
DBT = os.path.join(HERE, "dbt", ".venv", "bin", "dbt")
r = subprocess.run(
    [DBT, "build", "--profiles-dir", "."],
    cwd=os.path.join(HERE, "dbt"), env=ENV)
sys.exit(r.returncode)

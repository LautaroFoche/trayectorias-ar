.PHONY: setup run offline test serve docs airflow-setup airflow-check airflow-test
setup:
	uv sync --frozen --extra dev --python 3.13
run:
	.venv/bin/trayectorias run
offline:
	.venv/bin/trayectorias run --offline
test:
	.venv/bin/pytest -q
serve:
	.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory reports/current
docs:
	DBT_WAREHOUSE="$(CURDIR)/data/warehouse.duckdb" .venv/bin/dbt docs serve --project-dir dbt --profiles-dir dbt --target-path "$(CURDIR)/reports/current/dbt" --host 127.0.0.1 --port 8081
airflow-setup:
	uv venv --python 3.13 .airflow-venv
	uv pip install --python .airflow-venv/bin/python apache-airflow==3.1.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.1.5/constraints-3.13.txt
airflow-check:
	AIRFLOW_HOME="$(CURDIR)/.airflow" .airflow-venv/bin/python scripts/check_dag.py
airflow-test:
	AIRFLOW_HOME="$(CURDIR)/.airflow" AIRFLOW__CORE__LOAD_EXAMPLES=false AIRFLOW__CORE__DAGS_FOLDER="$(CURDIR)/orchestration" TRAYECTORIAS_ROOT="$(CURDIR)" TRAYECTORIAS_OFFLINE=true .airflow-venv/bin/airflow db migrate
	AIRFLOW_HOME="$(CURDIR)/.airflow" AIRFLOW__CORE__LOAD_EXAMPLES=false AIRFLOW__CORE__DAGS_FOLDER="$(CURDIR)/orchestration" TRAYECTORIAS_ROOT="$(CURDIR)" TRAYECTORIAS_OFFLINE=true .airflow-venv/bin/airflow dags test trayectorias_ar 2026-09-01

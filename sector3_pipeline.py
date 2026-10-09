from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator


PROJECT_DIR = "/opt/airflow/sector3_it_enterprise"


default_args = {
    "owner": "atha",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="sector3_pipeline",
    description="Sector 3 Multi-Source Business Intelligence Pipeline",
    start_date=datetime(2026, 10, 8),
    schedule="@weekly", 
    catchup=False,
    default_args=default_args,
    tags=["sector3", "multi-source"], 
) as dag:

    # ========================================================
    # START
    # ========================================================

    start = EmptyOperator(
        task_id="start_pipeline"
    )

    # ========================================================
    # BISNIS.COM
    # ========================================================

    bisnis_scrape = BashOperator(
        task_id="bisnis_scrape",
        bash_command=f"""
            cd {PROJECT_DIR} &&
            test -f data/raw/bisnis_cyber_raw.csv &&
            echo "Bisnis raw dataset tersedia." &&
            wc -l data/raw/bisnis_cyber_raw.csv
        """,
    ) 

    bisnis_content = BashOperator(
        task_id="bisnis_content",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 02_content/scrape_bisnis_cyber_content.py
        """,
    )

    bisnis_clean = BashOperator(
        task_id="bisnis_clean",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 03_cleaning/clean_bisnis_cyber.py
        """,
    )

    bisnis_filter = BashOperator(
        task_id="bisnis_filter",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 04_filtering/filter_bisnis.py
        """,
    )

    bisnis_insight = BashOperator(
        task_id="bisnis_insight",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 05_insight/extract_bisnis_insight.py
        """,
    )

    bisnis_load = BashOperator(
        task_id="bisnis_load_postgres",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 06_database/load_bisnis_to_postgres.py
        """,
    )

    # ========================================================
    # KATADATA
    # ========================================================

    katadata_scrape = BashOperator(
        task_id="katadata_scrape",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 01_scraping/scrape_katadata_enterprise.py
        """,
    )

    katadata_clean = BashOperator(
        task_id="katadata_clean",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 03_cleaning/clean_katadata_enterprise.py
        """,
    )

    katadata_filter = BashOperator(
        task_id="katadata_filter",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 04_filtering/filter_katadata_enterprise.py
        """,
    )

    katadata_insight = BashOperator(
        task_id="katadata_insight",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 05_insight/extract_enterprise_insight.py
        """,
    )

    katadata_load = BashOperator(
        task_id="katadata_load_postgres",
        bash_command=f"""
        cd {PROJECT_DIR} &&
        python 06_database/load_enterprise_to_postgres.py
        """,
    )

    # ========================================================
    # END
    # ========================================================

    pipeline_done = EmptyOperator(
        task_id="pipeline_done"
    )

    # ========================================================
    # DEPENDENCIES
    # ========================================================

    start >> bisnis_scrape
    start >> katadata_scrape

    # Bisnis branch
    bisnis_scrape >> bisnis_content
    bisnis_content >> bisnis_clean
    bisnis_clean >> bisnis_filter
    bisnis_filter >> bisnis_insight
    bisnis_insight >> bisnis_load

    # Katadata branch
    katadata_scrape >> katadata_clean
    katadata_clean >> katadata_filter
    katadata_filter >> katadata_insight
    katadata_insight >> katadata_load

    # Join
    [bisnis_load, katadata_load] >> pipeline_done 
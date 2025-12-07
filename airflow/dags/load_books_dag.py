from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'load_books_csv',
    default_args=default_args,
    description='Load books from CSV into database',
    schedule_interval=None, # Manual trigger for now
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['etl', 'books'],
) as dag:

    # Since the Airflow worker has access to the etl directory (mounted volume),
    # we can run the python script directly.
    # We need to ensure the python environment has the dependencies.
    # The airflow image might not have pandas/sqlalchemy installed by default if it's just the base apache/airflow image.
    # However, looking at docker-compose, airflow-webserver/scheduler build from ./airflow/Dockerfile.
    # We should check if that Dockerfile installs requirements.
    
    # Assuming the environment is set up or we use the 'etl' container via DockerOperator (better isolation)
    # or just run python if dependencies are there.
    
    # For simplicity in this setup, let's assume we run it in the airflow worker 
    # BUT we need to make sure dependencies are there.
    # Alternatively, we can use DockerOperator to run the command in the 'etl' service container.
    # But DockerOperator requires docker socket mounting which might not be there.
    
    # Let's try running it directly first, assuming the user might need to install deps in airflow image 
    # or we can use a VirtualenvOperator.
    
    # Actually, the best way given the current docker-compose is to run it in the 'etl' container.
    # But accessing other containers from airflow usually requires DockerOperator.
    
    # Let's stick to a simple BashOperator that runs the script. 
    # We will assume the airflow image has the deps OR we install them.
    # Wait, the user has a separate 'etl' service. 
    # The 'etl' service is just a container that runs 'tail -f /dev/null'.
    # We can use `docker exec` if we mount the socket, but that's complex.
    
    # EASIEST PATH: The 'etl' directory is mounted to `/opt/airflow/etl` in the airflow containers (see docker-compose).
    # So we can run `python /opt/airflow/etl/csv_loader/loader.py`.
    # We just need to ensure `pandas` and `sqlalchemy` are installed in the Airflow environment.
    
    load_csv_task = BashOperator(
        task_id='load_books_csv',
        bash_command='pip install pandas sqlalchemy psycopg2-binary && python /opt/airflow/etl/csv_loader/loader.py',
        env={
            'DATABASE_URL': '{{ var.value.get("database_url", "postgresql+psycopg2://postgres:postgres@postgres:5432/library_db") }}' 
            # We might need to set this variable in Airflow or hardcode for now based on docker-compose
        }
    )

    # Note: Installing pip packages in every run is not ideal for production but fine for this demo/portfolio.
    # Ideally, add these to airflow/requirements.txt

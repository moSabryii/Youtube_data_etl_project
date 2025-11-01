from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.extract import get_playlist_id, get_video_ids, extract_video_data, save_to_json

# Define local timezone (e.g. Cairo, Egypt)
local_tz = pendulum.timezone("Africa/Cairo")

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': 'mohamed@sabry.com',
    'email_on_failure': False,
    'email_on_retry': False,
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(hours=1),
    'start_date': datetime(2025, 1, 1, tzinfo=local_tz),
}

# Example DAG definition
with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='Dag to extract data from youtube api and export it in json format',
    schedule='0 14 * * *',
    catchup=False
) as dag:
    #define tasks
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extracted_data = extract_video_data(video_ids)
    save_to_json_task = save_to_json(extracted_data)
    
    #define dependencies
    
playlist_id >> video_ids >> extracted_data >> save_to_json_task
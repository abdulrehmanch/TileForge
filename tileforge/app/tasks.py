import os
import subprocess

from celery import shared_task
from celery.result import AsyncResult

MBTILES_DIR = '../mbtiles'


@shared_task
def generate_mbtiles(host, db_name, user, password, port, table_name):
    # Create directory structure
    db_dir = os.path.join(MBTILES_DIR, db_name)
    try:
        os.makedirs(db_dir, exist_ok=True)
    except OSError as e:
        return f"Error creating directories: {str(e)}"

    output_path = os.path.join(db_dir, f"{table_name}.mbtiles")
    command = f'ogr2ogr -f "MBTiles" {output_path} PG:"host={host} dbname={db_name} user={user} password={password} port={port}" -sql "SELECT * FROM {table_name}" -dsco MAXZOOM=10 -dsco MINZOOM=0 -nln "{table_name}_layer" -mapFieldType Date=String -mapFieldType DateTime=String'
    try:
        subprocess.run(command, shell=True, check=True)
        result = f"MBTiles for table {table_name} generated successfully!"
        return result
    except subprocess.CalledProcessError as e:
        return f"Error generating MBTiles: {str(e)}"


def check_task_status(task_id):
    result = AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': result.status,  # E.g., PENDING, STARTED, SUCCESS, FAILURE
        'result': result.result,  # Actual result or exception
    }

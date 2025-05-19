from celery.signals import task_postrun, worker_ready
from django.utils import timezone

from app import utils
from app.models import Task, MVTLayer, DatabaseConnection
from tileforge.settings import BASE_DIR


# on completion of mbtiles generation fron generate mbtiles function
@task_postrun.connect
def on_task_complete(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    tasks = Task.objects.filter(task_id=task_id)
    tasks.update(completed_at=timezone.now())
    # populating MVT Layer Table
    mbtiles_path = f"{BASE_DIR.parent}/mbtiles/{tasks.first().database_name}/{tasks.first().table_name}.mbtiles"
    layer_url = f"/tiles/{tasks.first().database_name}/{tasks.first().table_name}/{{z}}/{{x}}/{{y}}"
    db_connection = DatabaseConnection.objects.get(database_name=tasks.first().database_name)

    geom_type = utils.get_geom_type(db_connection, tasks.first().table_name)

    MVTLayer.objects.create(
        db_connection=db_connection, layer_name=tasks.first().table_name,
        mbtiles_path=mbtiles_path, url=layer_url, geometry_type=geom_type,
        scheme='tms'
    )

    import sys
    sys.stdout.flush()


@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    print(f"DEBUG: Celery worker is ready: {sender}")
    import sys
    sys.stdout.flush()

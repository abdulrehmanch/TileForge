from celery.result import AsyncResult
from celery import app  # Replace this with the actual path to your Celery app

# Replace with the task ID you want to check
task_id = 'd2c0e488-7836-494a-826c-9b01a4009cec'

# Get the task result
result = AsyncResult(task_id, app=app)

# Check the task status
print(f"Task Status: {result.status}")

# If the task succeeded, you can access the result
if result.status == 'SUCCESS':
    print(f"Task Result: {result.result}")

# If the task failed, you may retrieve the exception
if result.status == 'FAILURE':
    print(f"Error: {result.result}")
import time

from celery import Celery

celery_app = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)


@celery_app.task
def process_long_task_with_celery():
    # Simulate work
    time.sleep(30)
    print("Task completed in queue...")

    return {"message": "Task queued successful"}

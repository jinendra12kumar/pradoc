# """
# Celery Worker Entrypoint
# Run with:
#     celery -A workers.celery_worker worker --loglevel=info -Q email_queue
# """
# from core.celery_app import celery_app  # noqa: F401
# import tasks.email_tasks  # noqa: F401 — ensures tasks are registered

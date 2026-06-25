celery -A workers.celery_worker worker --loglevel=info -Q email_queue

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "docustream",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)

# Optional: load task modules automatically
celery_app.autodiscover_tasks(["app.services"])

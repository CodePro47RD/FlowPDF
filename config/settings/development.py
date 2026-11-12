from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# In local development and testing, run Celery tasks synchronously if Redis is absent
CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "True").lower() == "true"
CELERY_TASK_EAGER_PROPAGATES = True

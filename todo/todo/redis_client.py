from redis import Redis
from django.conf import settings 

r = Redis.from_url(settings.CELERY_BROKER_URL)
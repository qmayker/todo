import redis_lock
from redis import Redis

def get_recurring_lock(r:Redis, id:int, ct:int):
    lock_key = f"key:{id}:{ct}"
    lock = redis_lock.Lock(r, lock_key, expire=20)
    return lock
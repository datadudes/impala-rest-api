import urlparse
import datetime
from flask import current_app
import redis


def get_redis_conn():
    url = urlparse.urlparse(current_app.config['REDIS_URL'])
    r = redis.StrictRedis(host=url.hostname, port=url.port, password=url.password)
    return r


def _tomorrow_morning():
    today = datetime.datetime.now()
    tomorrow = today.date() if 0 <= today.hour < 9 else today.date() + datetime.timedelta(days=1)
    return datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 00)


def set_and_expire(key, payload):
    redis_conn = get_redis_conn()
    redis_conn.set(key, payload)
    redis_conn.expireat(key, _tomorrow_morning())
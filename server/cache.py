import urlparse
import datetime
import redis


def _tomorrow_morning():
    today = datetime.datetime.now()
    tomorrow = today.date() if 0 <= today.hour < 9 else today.date() + datetime.timedelta(days=1)
    return datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 00)


class RedisCache(object):

    def __init__(self, redis_url):
        url = urlparse.urlparse(redis_url)
        self.conn = redis.StrictRedis(host=url.hostname, port=url.port, password=url.password)

    def get(self, sql, mimetype):
        key = '{}${}'.format(sql, mimetype)
        return self.conn.get(key)

    def set_and_expire(self, sql, mimetype, payload):
        key = '{}${}'.format(sql, mimetype)
        self.conn.set(key, payload)
        self.conn.expireat(key, _tomorrow_morning())
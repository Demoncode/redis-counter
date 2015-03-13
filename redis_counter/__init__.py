import time
from datetime import datetime


NAMESPACE = 'counter'
SEPARATOR = ':'


def get_key(name, start, interval, namespace=NAMESPACE, separator=SEPARATOR):
    end = start + interval
    return separator.join(map(str, [namespace, name, int(start), int(end)]))


def get_key_by_datetime(
        name, dt, delta, namespace=NAMESPACE, separator=SEPARATOR):
    start = get_quantised_timestamp(dt, delta)
    return get_key(
        name, start, delta, namespace, separator)


def get_keys_for_timerange(
        name, start, end, interval, namespace=NAMESPACE, separator=SEPARATOR):
    keys = []
    start = get_quantised_timestamp(start, interval)
    end = get_quantised_timestamp(end, interval)
    key_count = (end - start) / interval
    for x in range(0, key_count):
        ts = start + x * interval
        keys.append(get_key(name, ts, interval, namespace, separator))
    return keys


def get_key_expiry_time(key, ttl):
    end = datetime.fromtimestamp(int(key.split(':')[-1:][0]))
    expire = end + ttl
    return int((expire - datetime.utcnow()).total_seconds())


def get_quantised_timestamp(dt, interval):
    if not interval:
        raise ValueError('interval must be a > 0 value')

    timestamp = int(time.mktime(dt.timetuple()))
    quantised_timestamp = timestamp - (timestamp % interval)
    return quantised_timestamp


def clear_counts_for_name(
        redis, name, namespace=NAMESPACE, separator=SEPARATOR):

    if 'BasePipeline' not in [c.__name__ for c in redis.__class__.__bases__]:
        redis = redis.pipeline()

    # TODO: performance improvement over using keys()?
    for key in redis.keys(separator.join(map(str, [namespace, name, '*']))):
        redis.delete(key)

    redis.execute()


def incr_counter(redis, key, incr=1, ttl=None):
    redis.incr(key, 1)
    if ttl is not None:
        expire_seconds = get_key_expiry_time(key)
        redis.expire(key, expire_seconds)


def incr_set(redis, key, object_name, incr=1, ttl=None):
    redis.zincrby(key, object_name, incr)
    if ttl is not None:
        expire_seconds = get_key_expiry_time(key)
        redis.expire(key, expire_seconds)


def get_scalar_value(redis, key):
    return int(redis.get(key) or 0)


def get_scalar_aggregate(
        redis, name, start, end, interval, namespace=NAMESPACE,
        separator=SEPARATOR):
    lua = """
    local sum = 0

    for i,key in ipairs(KEYS) do
        local val = redis.call('GET', key) or 0
        sum = sum + tonumber(val)
    end

    return sum
    """
    sum = redis.register_script(lua)
    keys = get_keys_for_timerange(
        name, start, end, interval, namespace, separator)
    count = sum(keys=keys)
    return count


def get_top_entries(
        redis, name, start, end, interval, limit=10,
        offset=0, cache=0, namespace=NAMESPACE, separator=SEPARATOR):
    keys = get_keys_for_timerange(
        name, start, end, interval, namespace, separator)
    aggregate_interval = int((end - start).total_seconds())
    aggregate_key = get_key_by_datetime(
        name, start, aggregate_interval, namespace, separator)

    if 'BasePipeline' not in [c.__name__ for c in redis.__class__.__bases__]:
        redis = redis.pipeline()

    redis.zunionstore(aggregate_key, keys)
    redis.zrevrangebyscore(
        aggregate_key, '+inf', '-inf', start=offset, num=limit,
        withscores=True)
    if cache > 0:
        redis.expire(aggregate_key, cache)
    else:
        redis.delete(aggregate_key)
    result = redis.execute()
    entries = [{'id': item[0], 'count': int(item[1])} for item in result[1]]
    response = {
        'cardinality': result[0],
        'entries': entries}
    if cache:
        response['ttl'] = result[2]
    return response

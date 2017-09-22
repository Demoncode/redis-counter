# redis-counter
Time windowed counters in Python



`redis_counter` contains a set of utility functions to help generate and
aggregate counts in redis.

Several functions require a [redis-py](https://github.com/andymccurdy/redis-py)
StrictRedis/StrictPipeline instance as the first argument.

Keys are in the format `counter:counter-name:start_timestamp:end_timestamp`,

ex: `counter:my-counter:1420070400:1420156800`

#### Incrementing counters

```
import datetime
import redis
import redis_counter


dt = datetime(2015, 1, 1, 15, 0, 0)
redis = redis.StrictRedis()

key = redis_counter.get_key_by_datetime('my-counter', dt, 86400)
redis_counter.incr_counter(redis, key)

key = redis_counter.get_key_by_datetime('my-set-counter', dt, 86400)
redis_counter.incr_set(redis, key, 'item-name', incr=3)

```

#### Aggregating counts

```
TODO

```

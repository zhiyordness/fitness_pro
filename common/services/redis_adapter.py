import os

import redis

from common.services.cache_value_serializer import CacheValueSerializer


class RedisAdapter:

    SET_IF_OWNER_SCRIPT = """
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        redis.call("SET", KEYS[2], ARGV[2], "EX", ARGV[3])
        return 1
    end
    return 0
    """

    @staticmethod
    def get_client():
        return redis.Redis.from_url(
            os.getenv("REDIS_URL") + "/1",
            decode_responses=True,
        )

    @staticmethod
    def set_if_owner(
            *,
            client,
            serializer=None,
            lock_key,
            lock_token,
            cache_key,
            value,
            timeout,
    ):
        if serializer is None:
            serializer = CacheValueSerializer

        serialized_value = serializer.dumps(value)

        return client.eval(
            RedisAdapter.SET_IF_OWNER_SCRIPT,
            2,
            lock_key,
            cache_key,
            lock_token,
            serialized_value,
            timeout,
        ) == 1
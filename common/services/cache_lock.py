import uuid


class CacheLock:

    RELEASE_SCRIPT = """
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    end
    return 0
    """

    RENEW_SCRIPT = """
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("EXPIRE", KEYS[1], ARGV[2])
    end
    return 0
    """

    def __init__(
            self,
            *,
            client,
            key,
            timeout,
    ):
        self.client = client
        self.key = f"lock:{key}"
        self.token = str(uuid.uuid4())
        self.timeout = timeout

    def acquire(self):
        return self.client.set(
            self.key,
            self.token,
            nx=True,
            ex=self.timeout,
        )

    def renew(self):
        result = self.client.eval(
            self.RENEW_SCRIPT,
            1,
            self.key,
            self.token,
            self.timeout,
        )

        return result == 1

    def release(self):
        result = self.client.eval(
            self.RELEASE_SCRIPT,
            1,
            self.key,
            self.token,
        )

        return result == 1


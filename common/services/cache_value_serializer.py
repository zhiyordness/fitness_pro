import pickle


class CacheValueSerializer:
    PROTOCOL = 5

    @classmethod
    def dumps(cls, value):
        return pickle.dumps(
            value,
            protocol=cls.PROTOCOL,
        )

    @classmethod
    def loads(cls, value):
        return pickle.loads(value)
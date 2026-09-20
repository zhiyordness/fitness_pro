


class CacheTimeoutError(Exception):
    """
    Raised when waiting for a cached value exceeds
    the configured timeout.
    """


class CacheUnavailableError(Exception):
    """
    Raised when the cache backend is unavailable.
    """
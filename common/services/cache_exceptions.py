


class CacheTimeoutError(Exception):
    """
    Raised when waiting for a cached value exceeds
    the configured timeout.
    """
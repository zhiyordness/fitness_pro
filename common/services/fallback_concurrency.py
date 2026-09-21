import threading
from contextlib import contextmanager
from django.conf import settings

from common.services.cache_exceptions import FallbackConcurrencyTimeout


class FallbackConcurrency:

    def __init__(self, max_concurrency):
        self.semaphore = threading.Semaphore(max_concurrency)

    def acquire(self, timeout):
        return self.semaphore.acquire(timeout=timeout)

    def release(self):
        self.semaphore.release()

    @contextmanager
    def slot(self, timeout):
        acquired = self.acquire(timeout=timeout)

        if not acquired:
            raise FallbackConcurrencyTimeout(
                "Fallback concurrency slot is unavailable."
            )

        try:
            yield
        finally:
            self.release()


fallback_concurrency = FallbackConcurrency(
    max_concurrency=settings.CACHE_FALLBACK_MAX_CONCURRENCY
)
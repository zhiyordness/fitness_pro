import time
import uuid

from django.core.cache import cache

from common.logging.audit import AuditLogger
from common.services.cache_exceptions import CacheTimeoutError
from django.conf import settings


class CacheService:


    @staticmethod
    def get(key):
        return cache.get(key)


    @staticmethod
    def set(
            key,
            value,
            timeout,
    ):
        cache.set(
            key=key,
            value=value,
            timeout=timeout,
        )


    @staticmethod
    def delete(key):
        cache.delete(key)


    @staticmethod
    def get_or_set(
            *,
            key,
            builder,
            timeout,
            use_lock=False,
    ):

        if use_lock:
            return CacheService._get_or_set_with_lock(
                key=key,
                builder=builder,
                timeout=timeout,
            )

        return CacheService._get_or_set_without_lock(
            key=key,
            builder=builder,
            timeout=timeout,
        )

    @staticmethod
    def _get_or_set_without_lock(
            *,
            key,
            builder,
            timeout,
    ):
        cached_value = CacheService.get(key)

        if cached_value is not None:
            return cached_value

        value = builder()

        if value is None:
            return None

        CacheService.set(
            key=key,
            value=value,
            timeout=timeout,
        )

        return value

    @staticmethod
    def _get_or_set_with_lock(
            *,
            key,
            builder,
            timeout,
    ):
        cached_value = CacheService.get(key)

        if cached_value is not None:
            return cached_value

        value = CacheService._try_build_with_lock(
            key=key,
            builder=builder,
            timeout=timeout,
        )

        if value is not None:
            return value

        cached_value = CacheService._wait_for_cache(
            key=key,
        )

        if cached_value is not None:
            return cached_value

        value = CacheService._try_build_with_lock(
            key=key,
            builder=builder,
            timeout=timeout,
        )

        if value is not None:
            return value

        CacheService._cache_timeout(key)

    @staticmethod
    def _lock_key(key):
        return f"lock:{key}"

    @staticmethod
    def _acquire_lock(key):

        lock_token = str(uuid.uuid4())

        lock_acquired = cache.add(
            CacheService._lock_key(key),
            lock_token,
            timeout=settings.CACHE_LOCK_TIMEOUT,
        )

        if not lock_acquired:
            return None

        return lock_token

    @staticmethod
    def _release_lock(
            key,
            lock_token,
    ):

        stored_token = cache.get(
            CacheService._lock_key(key)
        )

        if stored_token != lock_token:
            return

        cache.delete(
            CacheService._lock_key(key)
        )

    @staticmethod
    def _wait_for_cache(
            *,
            key,
    ):

        for _ in range(settings.CACHE_LOCK_RETRY_COUNT):

            time.sleep(settings.CACHE_LOCK_RETRY_DELAY)

            cached_value = CacheService.get(key)

            if cached_value is not None:
                return cached_value

        return None


    @staticmethod
    def _build_and_cache(
            *,
            key,
            builder,
            timeout,
    ):

        value = builder()

        if value is None:
            return None

        CacheService.set(
            key=key,
            value=value,
            timeout=timeout,
        )

        return value

    @staticmethod
    def _cache_timeout(key):

        AuditLogger.cache_timeout(
            key,
        )

        raise CacheTimeoutError(
            f"Timeout waiting for cache '{key}'."
        )

    @staticmethod
    def _try_build_with_lock(
            *,
            key,
            builder,
            timeout,
    ):
        lock_token = CacheService._acquire_lock(key)

        if lock_token is None:
            return None

        try:
            return CacheService._build_and_cache(
                key=key,
                builder=builder,
                timeout=timeout,
            )
        finally:
            CacheService._release_lock(
                key,
                lock_token,
            )


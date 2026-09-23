import time

from django.core.cache import cache

from common.logging.audit import AuditLogger
from common.services.cache_exceptions import CacheTimeoutError, CacheUnavailableError
from django.conf import settings

from common.services.cache_lock import CacheLock
from common.services.redis_adapter import RedisAdapter
from common.services.lock_renewal import LockRenewal
from redis.exceptions import RedisError
from common.services.fallback_concurrency import fallback_concurrency


class CacheService:
    LOCK_NOT_ACQUIRED = object()


    @staticmethod
    def get(key):
        try:
            return cache.get(key)
        except RedisError as exc:
            raise CacheUnavailableError(
                "Cache backend is unavailable."
            ) from exc


    @staticmethod
    def set(key, value, timeout,):
        try:
            cache.set(
                key=key,
                value=value,
                timeout=timeout,
            )
        except RedisError:
            AuditLogger.cache_unavailable(
                operation="set",
                cache_key=key,
            )


    @staticmethod
    def delete(key):
        try:
            cache.delete(key)
        except RedisError:
            AuditLogger.cache_unavailable(
                operation="delete",
                cache_key=key,
            )


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
        try:
            cached_value = CacheService.get(key)
        except CacheUnavailableError:
            with fallback_concurrency.slot(timeout=settings.CACHE_FALLBACK_TIMEOUT):
                return builder()

        if cached_value is not None:
            return cached_value

        try:
            value = CacheService._try_build_with_lock(
                key=key,
                builder=builder,
                timeout=timeout,
            )
        except CacheUnavailableError:
            with fallback_concurrency.slot(
                    timeout=settings.CACHE_FALLBACK_TIMEOUT,
            ):
                return builder()

        if value is not CacheService.LOCK_NOT_ACQUIRED:
            return value

        cached_value = CacheService._wait_for_cache(
            key=key,
        )

        if cached_value is not None:
            return cached_value

        try:
            value = CacheService._try_build_with_lock(
                key=key,
                builder=builder,
                timeout=timeout,
            )
        except CacheUnavailableError:
            with fallback_concurrency.slot(
                    timeout=settings.CACHE_FALLBACK_TIMEOUT,
            ):
                return builder()

        if value is CacheService.LOCK_NOT_ACQUIRED:
            CacheService._cache_timeout(key)

        return value



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
    def _cache_timeout(key):

        AuditLogger.cache_timeout(
            key,
        )

        raise CacheTimeoutError(
            f"Timeout waiting for cache '{key}'."
        )

    @staticmethod
    def _try_build_with_lock(*, key, builder, timeout):
        """
        builder()
            value
            lock ownership still valid?
                NO  -> return value, NO caching
                YES -> set_if_owner()
                    success → return value
                    False   → log rejection → return value
                    RedisError → log unavailable → return value
            finally
                renewal.stop()
                lock.release()
        """
        client = RedisAdapter.get_client()

        lock = CacheLock(
            client=client,
            key=key,
            timeout=settings.CACHE_LOCK_TIMEOUT,
        )

        if not lock.acquire():
            return CacheService.LOCK_NOT_ACQUIRED

        renewal = LockRenewal(
            lock=lock,
            interval=settings.CACHE_LOCK_TIMEOUT / 2,
        )

        renewal.start()

        try:
            value = builder()

            if renewal.lock_lost_event.is_set():
                return value

            if value is None:
                return None

            try:
                cache_write_succeeded = RedisAdapter.set_if_owner(
                    client=client,
                    lock_key=f"lock:{key}",
                    lock_token=lock.token,
                    cache_key=cache.make_key(key),
                    value=value,
                    timeout=timeout,
                )
            except RedisError:
                AuditLogger.cache_unavailable(
                    operation="set_if_owner",
                    cache_key=key,
                )
            else:
                if not cache_write_succeeded:
                    AuditLogger.cache_write_rejected(
                        cache_key=key,
                    )

            return value

        finally:
            renewal.stop()
            lock.release()


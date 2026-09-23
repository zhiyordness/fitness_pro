from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase

from common.logging.audit import AuditLogger
from common.services.cache_exceptions import CacheTimeoutError, CacheUnavailableError, FallbackConcurrencyTimeout
from common.services.cache_service import CacheService
from django.contrib.auth import get_user_model

from unittest.mock import patch
from redis.exceptions import RedisError

User = get_user_model()





class CacheServiceTests(TestCase):

    @patch("common.services.cache_service.cache")
    def test_returns_cached_value_when_cache_hit(self, mock_cache):

        cached_summary = {
            "current_weight": 70,
        }

        mock_cache.get.return_value = cached_summary

        builder = Mock()

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
        )

        self.assertEqual(
            result,
            cached_summary,
        )

        builder.assert_not_called()

        mock_cache.set.assert_not_called()

    @patch("common.services.cache_service.cache")
    def test_returns_cached_value_when_cache_miss(
            self,
            mock_cache,
    ):
        summary = {
            "current_weight": 70,
        }

        mock_cache.get.return_value = None

        builder = Mock()
        builder.return_value = summary

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
        )

        self.assertEqual(
            result,
            summary,
        )

        builder.assert_called_once()

        mock_cache.set.assert_called_once_with(
            key = "test-key",
            value = summary,
            timeout = 300,
        )

    @patch("common.services.cache_service.cache")
    def test_returns_none_when_cache_miss(self, mock_cache):

        builder = Mock()

        mock_cache.get.return_value = None
        builder.return_value = None

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
        )

        self.assertEqual(result, None)

        builder.assert_called_once()
        mock_cache.set.assert_not_called()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.cache")
    def test_builds_and_caches_value_when_cache_miss_with_lock(
            self,
            mock_cache,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        builder = Mock()

        summary = {
            "name": "Test name"
        }

        mock_cache.get.return_value = None
        mock_cache.make_key.return_value = ":1:test-key"
        builder.return_value = summary

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = True

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            summary,
        )

        builder.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_called_once_with(
            client=mock_redis_client,
            lock_key="lock:test-key",
            lock_token=mock_lock.token,
            cache_key=":1:test-key",
            value=summary,
            timeout=300,
        )

        mock_cache_lock.assert_called_once_with(
            client=mock_redis_client,
            key="test-key",
            timeout=10,
        )

        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_called_once()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.cache")
    def test_propagates_redis_error_when_lock_acquire_fails(
            self,
            mock_cache,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        mock_cache.get.return_value = None

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.side_effect = RedisError("Redis unavailable")

        builder = Mock(return_value={"value": "from-db"})

        with self.assertRaises(RedisError):
            CacheService.get_or_set(
                key="test-key",
                builder=builder,
                timeout=300,
                use_lock=True,
            )

        builder.assert_not_called()
        mock_lock.release.assert_not_called()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.cache")
    @patch("common.services.cache_service.time")
    def test_builds_and_caches_value_when_cache_miss_when_acquire_lock_fails(
            self,
            mock_time,
            mock_cache,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        summary = {
            "age": 36,
            "name": "Test"
        }

        mock_cache.get.side_effect = [
            None,
            summary,
        ]

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = False

        builder = Mock()

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            summary,
        )

        builder.assert_not_called()

        mock_cache_lock.assert_called_once_with(
            client=mock_redis_client,
            key="test-key",
            timeout=10,
        )

        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_not_called()

        mock_cache.set.assert_not_called()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.time")
    @patch("common.services.cache_service.cache")
    def test_builds_and_caches_value_when_cache_miss_and_second_acquire_lock_attempt_succeeds(
            self,
            mock_cache,
            mock_time,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        summary = {
            "age": 36,
            "name": "Test"
        }

        mock_cache.get.return_value = None
        mock_cache.make_key.return_value = ":1:test-key"

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value

        mock_lock.acquire.side_effect = [
            False,
            True,
        ]

        builder = Mock()
        builder.return_value = summary

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            summary,
        )

        builder.assert_called_once()

        self.assertEqual(
            mock_lock.acquire.call_count,
            2,
        )

        mock_lock.release.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_called_once_with(
            client=mock_redis_client,
            lock_key="lock:test-key",
            lock_token=mock_lock.token,
            cache_key=":1:test-key",
            value=summary,
            timeout=300,
        )


    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.time")
    @patch("common.services.cache_service.cache")
    def test_acquire_lock_fail_timeouts_raises_exception_and_logs(
            self,
            mock_cache,
            mock_time,
            mock_cache_lock,
            mock_redis_adapter,
            mock_audit_logger,
    ):
        builder = Mock()

        mock_cache.get.return_value = None
        mock_time.sleep.return_value = None

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.side_effect = [
            False,
            False,
        ]

        with self.assertRaises(CacheTimeoutError):
            CacheService.get_or_set(
                key="test-key",
                builder=builder,
                timeout=300,
                use_lock=True,
            )

        self.assertEqual(
            mock_lock.acquire.call_count,
            2,
        )

        builder.assert_not_called()

        mock_cache.set.assert_not_called()

        mock_lock.release.assert_not_called()

        mock_audit_logger.cache_timeout.assert_called_once_with(
            "test-key"
        )

    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.cache")
    def test_does_not_cache_value_if_lock_is_lost(
            self,
            mock_cache,
            mock_cache_lock,
            mock_redis_adapter,
            mock_lock_renewal,
    ):
        summary = {
            "name": "Test"
        }

        mock_cache.get.return_value = None

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = True

        builder = Mock()
        builder.return_value = summary

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            summary,
        )

        builder.assert_called_once()

        mock_renewal.start.assert_called_once()
        mock_renewal.stop.assert_called_once()

        mock_cache.set.assert_not_called()

        mock_lock.release.assert_called_once()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.cache")
    def test_uses_atomic_set_if_owner_when_lock_is_kept(
            self,
            mock_cache,
            mock_lock_renewal,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        summary = {
            "name": "Test",
        }

        mock_cache.get.return_value = None
        mock_cache.make_key.return_value = ":1:test-key"

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        mock_redis_adapter.set_if_owner.return_value = True

        builder = Mock()
        builder.return_value = summary

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_called_once()

        mock_lock_renewal.assert_called_once_with(
            lock=mock_lock,
            interval=5,
        )

        mock_renewal.start.assert_called_once()
        mock_renewal.stop.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_called_once_with(
            client=mock_redis_client,
            lock_key="lock:test-key",
            lock_token=mock_lock.token,
            cache_key=":1:test-key",
            value=summary,
            timeout=300,
        )

        mock_cache.set.assert_not_called()

        mock_lock.release.assert_called_once()


    @patch("common.services.cache_service.cache.get")
    def test_get_raises_cache_unavailable_error_on_redis_error(
            self,
            mock_cache_get,
    ):
        mock_cache_get.side_effect = RedisError("Redis unavailable")

        with self.assertRaises(CacheUnavailableError):
            CacheService.get("test-key")

    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_get_or_set_uses_fallback_when_cache_is_unavailable(
            self,
            mock_slot,
            mock_cache_get,
    ):
        mock_cache_get.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        builder = Mock(return_value={"value": "from-db"})

        mock_slot.return_value.__enter__.return_value = None

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            {"value": "from-db"},
        )
        builder.assert_called_once()
        mock_slot.assert_called_once()

    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_get_or_set_does_not_bypass_fallback_when_slot_is_unavailable(
            self,
            mock_slot,
            mock_cache_get,
    ):
        mock_cache_get.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        mock_slot.side_effect = FallbackConcurrencyTimeout(
            "Fallback concurrency slot is unavailable."
        )

        builder = Mock(return_value={"value": "from-db"})

        with self.assertRaises(FallbackConcurrencyTimeout):
            CacheService.get_or_set(
                key="test-key",
                builder=builder,
                timeout=300,
                use_lock=True,
            )

        builder.assert_not_called()
        mock_slot.assert_called_once()

    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_fallback_propagates_builder_exception(
            self,
            mock_slot,
            mock_cache_get,
    ):
        mock_cache_get.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        builder = Mock(side_effect=RuntimeError("Database error"))

        mock_slot.return_value.__enter__.return_value = None

        with self.assertRaises(RuntimeError):
            CacheService.get_or_set(
                key="test-key",
                builder=builder,
                timeout=300,
                use_lock=True,
            )

        builder.assert_called_once()
        mock_slot.assert_called_once()

    @patch("common.services.cache_service.CacheService._try_build_with_lock")
    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_fallback_skips_lock_path_when_cache_is_unavailable(
            self,
            mock_slot,
            mock_cache_get,
            mock_try_build_with_lock,
    ):
        mock_cache_get.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        mock_slot.return_value.__enter__.return_value = None

        builder = Mock(return_value={"value": "from-db"})

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            {"value": "from-db"},
        )

        builder.assert_called_once()
        mock_slot.assert_called_once()
        mock_try_build_with_lock.assert_not_called()

    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_fallback_uses_configured_timeout(
            self,
            mock_slot,
            mock_cache_get,
    ):
        mock_cache_get.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        mock_slot.return_value.__enter__.return_value = None

        builder = Mock(return_value={"value": "from-db"})

        CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        mock_slot.assert_called_once_with(
            timeout=settings.CACHE_FALLBACK_TIMEOUT,
        )

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.cache")
    def test_set_logs_cache_unavailable_when_redis_fails(
            self,
            mock_cache,
            mock_audit_logger,
    ):
        mock_cache.set.side_effect = RedisError(
            "Redis unavailable"
        )

        CacheService.set(
            key="test-key",
            value={"value": "test"},
            timeout=300,
        )

        mock_audit_logger.cache_unavailable.assert_called_once_with(
            operation="set",
            cache_key="test-key",
        )

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.cache")
    def test_set_does_not_log_cache_unavailable_when_cache_set_succeeds(
            self,
            mock_cache,
            mock_audit_logger,
    ):
        CacheService.set(
            key="test-key",
            value={"value": "test"},
            timeout=300,
        )

        mock_cache.set.assert_called_once_with(
            key="test-key",
            value={"value": "test"},
            timeout=300,
        )

        mock_audit_logger.cache_unavailable.assert_not_called()

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.cache")
    def test_delete_logs_cache_unavailable_when_redis_fails(
            self,
            mock_cache,
            mock_audit_logger,
    ):
        mock_cache.delete.side_effect = RedisError(
            "Redis unavailable"
        )

        CacheService.delete(
            key="test-key"
        )

        mock_audit_logger.cache_unavailable.assert_called_once_with(
            operation = "delete",
            cache_key = "test-key",
        )

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.cache")
    def test_delete_does_not_log_cache_unavailable_when_cache_delete_succeeds(
            self,
            mock_cache,
            mock_audit_logger,
    ):

        CacheService.delete(
            key="test-key"
        )

        mock_cache.delete.assert_called_once_with(
            "test-key",
        )

        mock_audit_logger.cache_unavailable.assert_not_called()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    def test_does_not_cache_value_if_lock_is_lost_during_build(
            self,
            mock_lock_renewal,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        summary = {
            'current_weight': 70,
            'progress_percentage': 50,
        }

        mock_cache_lock.return_value.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        def builder():
            mock_renewal.lock_lost_event.is_set.return_value = True
            return summary

        result = CacheService._try_build_with_lock(
            key="test-key",
            builder=builder,
            timeout=300,
        )

        self.assertEqual(result, summary)
        mock_renewal.start.assert_called_once()
        mock_renewal.stop.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_not_called()
        mock_cache_lock.return_value.release.assert_called_once()

    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheService.get")
    @patch("common.services.cache_service.fallback_concurrency.slot")
    def test_uses_fallback_when_lock_acquire_fails_because_redis_is_unavailable(
            self,
            mock_slot,
            mock_cache_get,
            mock_redis_adapter,
            mock_cache_lock,
    ):
        mock_cache_get.return_value = None

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.side_effect = CacheUnavailableError(
            "Cache backend is unavailable."
        )

        mock_slot.return_value.__enter__.return_value = None

        builder = Mock(return_value={"value": "from-db"})

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(
            result,
            {"value": "from-db"},
        )

        builder.assert_called_once()
        mock_slot.assert_called_once_with(
            timeout=settings.CACHE_FALLBACK_TIMEOUT,
        )

        mock_lock.release.assert_not_called()

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.cache")
    def test_returns_built_value_when_cache_write_fails(
            self,
            mock_cache,
            mock_lock_renewal,
            mock_cache_lock,
            mock_redis_adapter,
            mock_audit_logger,
    ):
        summary = {
            "current_weight": 70,
            "progress_percentage": 50,
        }

        mock_cache.get.return_value = None
        mock_cache.make_key.return_value = ":1:test-key"

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        mock_redis_adapter.set_if_owner.side_effect = RedisError(
            "Redis unavailable"
        )

        builder = Mock(return_value=summary)

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_called_once()

        mock_audit_logger.cache_unavailable.assert_called_once_with(
            operation="set_if_owner",
            cache_key="test-key",
        )

        mock_lock.release.assert_called_once()

    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.cache")
    def test_returns_built_value_when_cache_write_is_rejected(
            self,
            mock_cache,
            mock_lock_renewal,
            mock_cache_lock,
            mock_redis_adapter,
    ):
        summary = {
            "current_weight": 70,
            "progress_percentage": 50,
        }

        mock_cache.get.return_value = None
        mock_cache.make_key.return_value = ":1:test-key"

        mock_redis_client = Mock()
        mock_redis_adapter.get_client.return_value = mock_redis_client

        mock_lock = mock_cache_lock.return_value
        mock_lock.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        mock_redis_adapter.set_if_owner.return_value = False

        builder = Mock(return_value=summary)

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_called_once()
        mock_redis_adapter.set_if_owner.assert_called_once()
        mock_lock.release.assert_called_once()

    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.cache")
    def test_logs_when_cache_write_is_rejected(
            self,
            mock_cache,
            mock_lock_renewal,
            mock_cache_lock,
            mock_redis_adapter,
            mock_audit_logger,
    ):
        summary = {
            "current_weight": 70,
            "progress_percentage": 50,
        }

        mock_cache.get.return_value = None

        mock_cache_lock.return_value.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        mock_redis_adapter.set_if_owner.return_value = False

        builder = Mock(return_value=summary)

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_called_once()

        mock_redis_adapter.set_if_owner.assert_called_once()

        mock_audit_logger.cache_write_rejected.assert_called_once_with(
            cache_key="test-key",
        )

        mock_cache_lock.return_value.release.assert_called_once()

    @patch("common.services.cache_service.fallback_concurrency")
    @patch("common.services.cache_service.CacheLock")
    @patch("common.services.cache_service.LockRenewal")
    @patch("common.services.cache_service.CacheService._wait_for_cache")
    @patch("common.services.cache_service.RedisAdapter")
    @patch("common.services.cache_service.cache")
    def test_does_not_wait_for_cache_when_builder_returns_none_after_lock_acquired(
            self,
            mock_cache,
            mock_redis_adapter,
            mock_wait_for_cache,
            mock_lock_renewal,
            mock_cache_lock,
            mock_fallback_concurrency,
    ):
        mock_cache.get.return_value = None

        mock_cache_lock.return_value.acquire.return_value = True

        mock_renewal = mock_lock_renewal.return_value
        mock_renewal.lock_lost_event.is_set.return_value = False

        builder = Mock(return_value=None)

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertIsNone(result)

        builder.assert_called_once()

        mock_wait_for_cache.assert_not_called()

        mock_cache_lock.return_value.release.assert_called_once()



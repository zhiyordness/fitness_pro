from decimal import Decimal
from unittest.mock import Mock, patch

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.redis import RedisSerializer
from django.test import TestCase

from choices import WeekDaysChoices
from common.services.cache_exceptions import CacheTimeoutError, CacheUnavailableError, FallbackConcurrencyTimeout
from common.services.cache_service import CacheService
from common.services.fallback_concurrency import FallbackConcurrency, fallback_concurrency
from common.services.lock_renewal import LockRenewal
from common.services.redis_adapter import RedisAdapter
from progress.models import ProgresTracking
from progress.services import ProgressAnalyticsService
from django.contrib.auth import get_user_model
from common.services.cache_lock import CacheLock
from common.services.cache_value_serializer import CacheValueSerializer
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

class ProgressAnalyticsServiceTests(TestCase):

    @patch("progress.services.CacheService.get_or_set")
    def test_get_progress_summary(
            self,
            mock_get_or_set,
    ):
        summary = {
            "progress": 50,
        }

        mock_get_or_set.return_value = summary

        user = Mock()

        result = ProgressAnalyticsService.get_progress_summary(user)

        self.assertEqual(result, summary)

        mock_get_or_set.assert_called_once()


    @patch("progress.services.CacheService.get_or_set")
    def test_returns_value_from_cache_service(
            self,
            mock_get_or_set,
    ):
        expected_summary = {
            "progress_percentage": Decimal("50")
        }

        mock_get_or_set.return_value = expected_summary

        user = Mock()

        result = ProgressAnalyticsService.get_progress_summary(user)

        self.assertEqual(
            result,
            expected_summary,
        )

    @patch("progress.services.ProgressAnalyticsService._build_progress_summary")
    @patch("progress.services.CacheService.get_or_set")
    def test_builder_calls_build_progress_summary(
            self,
            mock_get_or_set,
            mock_build_progress_summary,
    ):
        user = Mock()

        ProgressAnalyticsService.get_progress_summary(user)

        builder = mock_get_or_set.call_args.kwargs["builder"]

        builder()

        mock_build_progress_summary.assert_called_once_with(user)


    @staticmethod
    def create_progress_record(
            user,
            day,
            weight,
    ):
        return ProgresTracking.objects.create(
            owner=user,
            day=day,
            weight=Decimal(weight),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

    def test_returns_none_when_starting_weight_is_missing(self):
        user = User.objects.create_user(
            email="test-user@test.com",
            password="password123",
        )

        profile = user.profile
        profile.starting_weight = None
        profile.target_weight = Decimal("80")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("90.00"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertIsNone(result)



    def test_returns_none_when_target_weight_missing(self):
        user = User.objects.create_user(
            email="test-user@test.com",
            password="pass123"
        )
        profile=user.profile
        profile.starting_weight=Decimal("63")
        profile.target_weight=None
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("90.00"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertIsNone(result)

    def test_returns_none_when_latest_record_missing(self):
        user = User.objects.create_user(
            email="test-user@test.com",
            password="pass123"
        )
        profile = user.profile
        profile.starting_weight = Decimal("63")
        profile.target_weight = Decimal("75")
        profile.save()

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertIsNone(result)

    def test_returns_summary_when_required_data_exists(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )
        profile= user.profile
        profile.starting_weight = Decimal("63")
        profile.target_weight = Decimal("75")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("65.00"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(result["starting_weight"], Decimal("63"))
        self.assertEqual(result["target_weight"], Decimal("75"))
        self.assertEqual(result["current_weight"], Decimal("65"))



    def test_caps_progress_percentage_to_100(self):
        user = User.objects.create_user(
            email="test@test.com",
            password = "pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("100")
        profile.target_weight = Decimal("90")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("80"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["progress_percentage"],
            Decimal("100")
        )


    def test_sets_progress_percentage_to_zero_when_less_than_point_zero_one(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["progress_percentage"],
            Decimal("0.00")
        )

    def test_prediction_is_not_available_when_less_than_three_records(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertIsNone(result["weekly_rate"])
        self.assertIsNone(result["estimated_weeks"])
        self.assertFalse(result["prediction_available"])

    def test_calculates_prediction_when_three_or_more_records_exist(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.TUESDAY,
            weight=Decimal("60.2"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.SUNDAY,
            weight=Decimal("60.40"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(result["weekly_rate"], Decimal('2.80'))
        self.assertEqual(result["estimated_weeks"], Decimal('10.6'))
        self.assertTrue(result["prediction_available"])

    def test_estimated_weeks_is_none_when_weekly_rate_is_zero(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.TUESDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        ProgresTracking.objects.create(
            owner=user,
            day=WeekDaysChoices.SUNDAY,
            weight=Decimal("60"),
            chest=100,
            shoulders=120,
            waist=80,
            biceps=40,
            neck=40,
            butt=100,
            tight=60,
            calf=40,
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["weekly_rate"],
            Decimal("0")
        )
        self.assertIsNone(
            result["estimated_weeks"]
        )
        self.assertTrue(
            result["prediction_available"]
        )

    def test_uses_one_day_when_days_difference_is_zero(self):

        """
        This test relies on all ProgressTracking records being created on the same day.

        Because `date` uses `auto_now_add=True`, the initial `days_difference`
        is expected to be 0, exercising the fallback:

            if days_difference < 1:
                days_difference = 1

        If the timestamp creation strategy changes in the future, this test
        may need to be updated.
        """

        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "60",
        )
        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "61",
        )
        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "62",
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["weekly_rate"],
            Decimal("14")
        )

    def test_calculates_remaining_to_goal_correctly(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "60",
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["remaining_to_goal"],
            Decimal("30")
        )

    def test_calculates_negative_weight_change_correctly(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("70")
        profile.target_weight = Decimal("90")
        profile.save()

        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "60",
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["weight_change"],
            Decimal("-10")
        )

    def test_calculates_positive_weight_change_correctly(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123"
        )

        profile = user.profile
        profile.starting_weight = Decimal("60")
        profile.target_weight = Decimal("90")
        profile.save()

        self.create_progress_record(
            user,
            WeekDaysChoices.MONDAY,
            "70",
        )

        result = ProgressAnalyticsService._build_progress_summary(user)

        self.assertEqual(
            result["weight_change"],
            Decimal("10")
        )


    @patch("progress.services.CacheService.delete")
    @patch("progress.services.ProgressAnalyticsService._cache_key")
    def test_invalidate_cache_provides_correct_key_to_cache_service(
            self,
            mock_cache_key,
            mock_delete,
    ):
        user = Mock()

        mock_cache_key.return_value = "test_key"

        ProgressAnalyticsService.invalidate_cache(user)

        mock_delete.assert_called_once_with(
            "test_key"
        )

    def test_cache_creates_correct_key(
            self,
    ):
        user = Mock()
        user.id = 113

        result = ProgressAnalyticsService._cache_key(user)

        self.assertEqual(result, "user:113:progress_summary")


class CacheLockTests(TestCase):

    @patch("common.services.cache_lock.uuid")
    def test_acquire_creates_lock(
            self,
            mock_uuid,
    ):
        mock_client = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_client.set.return_value = True

        lock = CacheLock(
            client=mock_client,
            key="test-key",
            timeout=10,
        )

        result = lock.acquire()

        self.assertTrue(result)

        mock_client.set.assert_called_once_with(
            "lock:test-key",
            "test-token",
            nx=True,
            ex=10,
        )

    @patch("common.services.cache_lock.uuid")
    def test_release_deletes_lock_when_token_matches(
            self,
            mock_uuid,
    ):
        mock_client = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_client.eval.return_value = 1

        lock = CacheLock(
            client=mock_client,
            key="test-key",
            timeout=10,
        )

        result = lock.release()

        self.assertTrue(result)

        mock_client.eval.assert_called_once_with(
            CacheLock.RELEASE_SCRIPT,
            1,
            "lock:test-key",
            "test-token",
        )

    @patch("common.services.cache_lock.uuid")
    def test_release_does_not_delete_lock_when_token_does_not_match(
            self,
            mock_uuid,
    ):
        mock_client = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_client.eval.return_value = 0

        lock = CacheLock(
            client=mock_client,
            key="test-key",
            timeout=10,
        )

        result = lock.release()

        self.assertFalse(result)

        mock_client.eval.assert_called_once_with(
            CacheLock.RELEASE_SCRIPT,
            1,
            "lock:test-key",
            "test-token",
        )

    @patch("common.services.cache_lock.uuid")
    def test_renew_extends_lock_when_token_matches(
            self,
            mock_uuid,
    ):
        mock_client = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_client.eval.return_value = 1

        lock = CacheLock(
            client=mock_client,
            key="test-key",
            timeout=10,
        )

        result = lock.renew()

        self.assertTrue(result)

        mock_client.eval.assert_called_once_with(
            CacheLock.RENEW_SCRIPT,
            1,
            "lock:test-key",
            "test-token",
            10,
        )

    @patch("common.services.cache_lock.uuid")
    def test_renew_fails_when_token_does_not_match(
            self,
            mock_uuid,
    ):
        mock_client = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_client.eval.return_value = 0

        lock = CacheLock(
            client=mock_client,
            key="test-key",
            timeout=10,
        )

        result = lock.renew()

        self.assertFalse(result)

        mock_client.eval.assert_called_once_with(
            CacheLock.RENEW_SCRIPT,
            1,
            "lock:test-key",
            "test-token",
            10,
        )

class LockRenewalTests(TestCase):

    def test_run_renews_lock_when_not_stopped(self):
        lock = Mock()

        renewal = LockRenewal(
            lock=lock,
            interval=3,
        )

        renewal.stop_event.wait = Mock(
            side_effect=[
                False,
                True,
            ]
        )

        lock.renew.return_value = True

        renewal._run()

        lock.renew.assert_called_once()
        self.assertFalse(
            renewal.lock_lost_event.is_set()
        )

    def test_run_sets_lock_lost_when_renew_fails(self):
        lock = Mock()

        renewal = LockRenewal(
            lock=lock,
            interval=3,
        )

        renewal.stop_event.wait = Mock(
            return_value=False
        )

        lock.renew.return_value = False

        renewal._run()

        lock.renew.assert_called_once()

        self.assertTrue(
            renewal.lock_lost_event.is_set()
        )

    @patch("common.services.lock_renewal.threading.Thread")
    def test_start_creates_and_starts_thread(
            self,
            mock_thread,
    ):
        lock = Mock()

        renewal = LockRenewal(
            lock=lock,
            interval=3,
        )

        mock_thread_instance = mock_thread.return_value

        renewal.start()

        mock_thread.assert_called_once_with(
            target=renewal._run,
            daemon=True,
        )

        mock_thread_instance.start.assert_called_once()

        self.assertIs(
            renewal.thread,
            mock_thread_instance,
        )

    def test_stop_signals_and_joins_thread(self):
        lock = Mock()

        renewal = LockRenewal(
            lock=lock,
            interval=3,
        )

        mock_thread = Mock()
        renewal.thread = mock_thread

        renewal.stop()

        self.assertTrue(
            renewal.stop_event.is_set()
        )

        mock_thread.join.assert_called_once()

class RedisAdapterTests(TestCase):

    @patch("common.services.redis_adapter.redis.Redis.from_url")
    def test_set_if_owner_executes_atomic_script(
            self,
            mock_from_url,
    ):
        mock_client = Mock()
        mock_from_url.return_value = mock_client

        mock_serializer = Mock()
        mock_serializer.dumps.return_value = b"serialized-value"

        client = RedisAdapter.get_client()

        client.eval.return_value = 1

        result = RedisAdapter.set_if_owner(
            client=client,
            serializer=mock_serializer,
            lock_key="lock:test-key",
            lock_token="abc-123",
            cache_key="test-key",
            value="cached-value",
            timeout=300,
        )

        self.assertTrue(result)

        client.eval.assert_called_once()

    @patch("common.services.redis_adapter.redis.Redis.from_url")
    def test_set_if_owner_serializes_dict_value(
            self,
            mock_from_url,
    ):
        mock_client = Mock()
        mock_from_url.return_value = mock_client

        client = RedisAdapter.get_client()

        client.eval.return_value = 1

        mock_serializer = Mock()
        mock_serializer.dumps.return_value = b"serialized-value"


        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        result = RedisAdapter.set_if_owner(
            client=client,
            serializer=mock_serializer,
            lock_key="lock:test-key",
            lock_token="abc-123",
            cache_key="test-key",
            value=value,
            timeout=300,
        )

        self.assertTrue(result)

        mock_client.eval.assert_called_once()

        args = mock_client.eval.call_args.args

        serialized_value = args[5]

        self.assertIsInstance(
            serialized_value,
            bytes,
        )

    def test_django_cache_serializes_dict_value(self):
        from django.core.cache import cache

        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        cache.set(
            key="serialization-test",
            value=value,
            timeout=300,
        )

        result = cache.get("serialization-test")

        self.assertEqual(result, value)

    @patch("common.services.redis_adapter.redis.Redis.from_url")
    def test_set_if_owner_uses_serializer(
            self,
            mock_from_url,
    ):
        mock_client = Mock()
        mock_from_url.return_value = mock_client

        client = RedisAdapter.get_client()

        client.eval.return_value = 1

        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        mock_serializer = Mock()
        serialized_value = b"serialized-value"
        mock_serializer.dumps.return_value = serialized_value

        result = RedisAdapter.set_if_owner(
            client=client,
            serializer=mock_serializer,
            lock_key="lock:test-key",
            lock_token="abc-123",
            cache_key="test-key",
            value=value,
            timeout=300,
        )

        self.assertTrue(result)

        mock_serializer.dumps.assert_called_once_with(value)

        args = mock_client.eval.call_args.args

        self.assertEqual(
            args[5],
            serialized_value,
        )

    @patch("common.services.redis_adapter.redis.Redis.from_url")
    def test_set_if_owner_uses_default_serializer(
            self,
            mock_from_url,
    ):
        mock_client = Mock()
        mock_from_url.return_value = mock_client
        mock_client.eval.return_value = 1

        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        result = RedisAdapter.set_if_owner(
            client=mock_client,
            lock_key="lock:test-key",
            lock_token="test-token-123",
            cache_key="test-key",
            value=value,
            timeout=300,
        )

        self.assertTrue(result)

        args = mock_client.eval.call_args.args
        serialized_value = args[5]

        self.assertIsInstance(
            serialized_value,
            bytes,
        )

    def test_set_if_owner_returns_false_when_lock_is_not_owned(self):
        mock_client = Mock()
        mock_client.eval.return_value = 0

        value = {
            "current_weight": 70,
        }

        result = RedisAdapter.set_if_owner(
            client=mock_client,
            lock_key="lock:test-key",
            lock_token="abc-123",
            cache_key="test-key",
            value=value,
            timeout=300,
        )

        self.assertFalse(result)

    def test_set_if_owner_writes_value_that_django_cache_can_read(self):

        lock_key = "lock:integration-test"
        cache_key = cache.make_key("integration-test")
        lock_token = "integration-token"

        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        client = RedisAdapter.get_client()

        self.addCleanup(client.delete, lock_key)
        self.addCleanup(cache.delete, "integration-test")

        client.set(
            lock_key,
            lock_token,
            nx=True,
            ex=300,
        )

        self.assertEqual(
            client.get(lock_key),
            lock_token,
        )

        result = RedisAdapter.set_if_owner(
            client=client,
            lock_key=lock_key,
            lock_token=lock_token,
            cache_key=cache_key,
            value=value,
            timeout=300,
        )

        self.assertTrue(result)

        cached_value = cache.get("integration-test")

        self.assertEqual(
            cached_value,
            value,
        )

class CacheValueSerializerTests(TestCase):

    def test_dumps_returns_bytes(self):
        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        serialized = CacheValueSerializer.dumps(value)

        self.assertIsInstance(
            serialized,
            bytes,
        )

    def test_loads_returns_original_value(self):
        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        serialized = CacheValueSerializer.dumps(value)

        result = CacheValueSerializer.loads(serialized)

        self.assertEqual(
            result,
            value,
        )

    def test_matches_django_redis_serializer(self):
        value = {
            "current_weight": 70,
            "progress_percentage": 45.5,
        }

        django_serializer = RedisSerializer()

        expected = django_serializer.dumps(value)
        actual = CacheValueSerializer.dumps(value)

        self.assertEqual(
            actual,
            expected,
        )

        self.assertEqual(
            CacheValueSerializer.loads(actual),
            django_serializer.loads(expected),
        )


class FallbackConcurrencyTests(TestCase):

    def test_acquire_returns_true_when_slot_is_available(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        acquired = fallback.acquire(timeout=0)

        self.assertTrue(acquired)

    def test_second_acquire_fails_when_slot_is_already_taken(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        first_acquired = fallback.acquire(timeout=0)
        second_acquired = fallback.acquire(timeout=0)

        self.assertTrue(first_acquired)
        self.assertFalse(second_acquired)

    def test_slot_can_be_acquired_again_after_release(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        first_acquired = fallback.acquire(timeout=0)
        fallback.release()
        second_acquired = fallback.acquire(timeout=0)

        self.assertTrue(first_acquired)
        self.assertTrue(second_acquired)

    def test_slot_can_be_released_after_exception(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        first_acquired = fallback.acquire(timeout=0)

        try:
            raise RuntimeError("Builder failed")
        except RuntimeError:
            fallback.release()

        second_acquired = fallback.acquire(timeout=0)

        self.assertTrue(first_acquired)
        self.assertTrue(second_acquired)

    def test_acquire_returns_false_after_timeout(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        first_acquired = fallback.acquire(timeout=0)
        second_acquired = fallback.acquire(timeout=1)

        fallback.release()

        self.assertTrue(first_acquired)
        self.assertFalse(second_acquired)

    def test_slot_raises_timeout_when_no_slot_is_available(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        fallback.acquire(timeout=0)

        with self.assertRaises(FallbackConcurrencyTimeout):
            with fallback.slot(timeout=0):
                pass

        fallback.release()

    def test_slot_releases_after_exception(self):
        fallback = FallbackConcurrency(max_concurrency=1)

        with self.assertRaises(RuntimeError):
            with fallback.slot(timeout=0):
                raise RuntimeError("Builder failed")

        acquired_again = fallback.acquire(timeout=0)

        self.assertTrue(acquired_again)

    def test_shared_fallback_concurrency_uses_configured_limit(self):

        first_acquired = fallback_concurrency.acquire(timeout=0)
        second_acquired = fallback_concurrency.acquire(timeout=0)

        fallback_concurrency.release()

        self.assertTrue(first_acquired)
        self.assertFalse(second_acquired)

from decimal import Decimal
from unittest.mock import Mock, patch

from django.test import TestCase

from choices import WeekDaysChoices
from common.services.cache_exceptions import CacheTimeoutError
from common.services.cache_service import CacheService
from progress.models import ProgresTracking
from progress.services import ProgressAnalyticsService
from django.contrib.auth import get_user_model

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

    @patch("common.services.cache_service.cache")
    @patch("common.services.cache_service.uuid")
    def test_builds_and_caches_value_when_cache_miss_with_lock(self, mock_uuid, mock_cache):

        builder = Mock()

        summary = {
            "name": "Test name"
        }

        mock_uuid.uuid4.return_value = "test-token"

        mock_cache.get.side_effect = [
            None,
            "test-token",
        ]

        mock_cache.add.return_value = True

        builder.return_value = summary

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_called_once()

        mock_cache.add.assert_called_once_with(
            "lock:test-key",
            'test-token',
            timeout = 10,
        )

        mock_cache.set.assert_called_once_with(
            key = "test-key",
            value = summary,
            timeout = 300,
        )

        mock_cache.delete.assert_called_once_with(
            "lock:test-key"
        )

    @patch("common.services.cache_service.time")
    @patch("common.services.cache_service.cache")
    def test_builds_and_caches_value_when_cache_miss_when_acquire_lock_fails(self, mock_cache, mock_time):

        summary = {
            "age": 36,
            "name": "Test"
        }

        mock_cache.get.side_effect = [
            None,
            summary,
        ]

        mock_cache.add.return_value = False

        builder = Mock()

        mock_time.sleep(0.05)

        result = CacheService.get_or_set(
            key="test-key",
            builder=builder,
            timeout=300,
            use_lock=True,
        )

        self.assertEqual(result, summary)

        builder.assert_not_called()

        mock_cache.add.assert_called_once()

        mock_cache.set.assert_not_called()

        mock_cache.delete.assert_not_called()

    @patch("common.services.cache_service.uuid")
    @patch("common.services.cache_service.time")
    @patch("common.services.cache_service.cache")
    def test_builds_and_caches_value_when_cache_miss_and_second_acquire_lock_attempt_succeeds(
            self,
            mock_cache,
            mock_time,
            mock_uuid,
    ):
        summary = {
            "age": 36,
            "name": "Test"
        }

        mock_uuid.uuid4.return_value = "test-token"
        mock_time.sleep(0.05)

        def mock_get(key):
            if key == "test-key":
                return None

            if key == "lock:test-key":
                return "test-token"

            return None

        mock_cache.get.side_effect = mock_get

        mock_cache.add.side_effect = [
            False,
            True
        ]

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

        self.assertEqual(mock_cache.add.call_count, 2)

        mock_cache.set.assert_called_once()

        mock_cache.delete.assert_called_once()


    @patch("common.services.cache_service.AuditLogger")
    @patch("common.services.cache_service.uuid")
    @patch("common.services.cache_service.time")
    @patch("common.services.cache_service.cache")
    def test_acquire_lock_fail_timeouts_raises_exception_and_logs(
            self,
            mock_cache,
            mock_time,
            mock_uuid,
            mock_audit_logger,
    ):
        builder = Mock()

        mock_uuid.uuid4.return_value = "test-token"
        mock_time.sleep.return_value = None

        mock_cache.get.return_value = None

        mock_cache.add.side_effect = [
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

        self.assertEqual(mock_cache.add.call_count, 2)
        builder.assert_not_called()
        mock_cache.set.assert_not_called()
        mock_cache.delete.assert_not_called()
        mock_audit_logger.cache_timeout.assert_called_once_with(
            "test-key"
        )

    @patch("common.services.cache_service.cache")
    def test_lock_not_deleted_when_tokens_do_not_match(
            self,
            mock_cache,
    ):
        our_token = "our_token"
        another_token = "another_token"

        mock_cache.get.return_value = another_token

        CacheService._release_lock(
            "test-key",
            our_token,
        )

        mock_cache.get.assert_called_once_with(
            "lock:test-key"
        )

        mock_cache.delete.assert_not_called()


    @patch("common.services.cache_service.cache")
    def test_lock_deleted_when_tokens_match(
            self,
            mock_cache,
    ):
        our_token = "our_token"

        mock_cache.get.return_value = our_token

        CacheService._release_lock(
            "test-key",
            our_token,
        )

        mock_cache.get.assert_called_once_with(
            "lock:test-key"
        )

        mock_cache.delete.assert_called_once_with(
            "lock:test-key"
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
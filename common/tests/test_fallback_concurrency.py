from django.test import TestCase

from common.services.cache_exceptions import FallbackConcurrencyTimeout
from common.services.fallback_concurrency import FallbackConcurrency, fallback_concurrency
from django.contrib.auth import get_user_model

User = get_user_model()


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

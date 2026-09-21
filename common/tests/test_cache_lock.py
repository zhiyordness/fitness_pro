from unittest.mock import Mock, patch

from django.test import TestCase

from django.contrib.auth import get_user_model
from common.services.cache_lock import CacheLock


User = get_user_model()


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

from unittest.mock import Mock, patch

from django.test import TestCase

from common.services.lock_renewal import LockRenewal

from django.contrib.auth import get_user_model


User = get_user_model()


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

from unittest.mock import Mock, patch

from django.core.cache import cache

from django.test import TestCase
from redis.exceptions import RedisError

from common.services.redis_adapter import RedisAdapter

from django.contrib.auth import get_user_model


User = get_user_model()


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

    @patch("common.services.redis_adapter.CacheValueSerializer")
    def test_set_if_owner_raises_when_redis_is_unavailable(
            self,
            mock_serializer,
    ):
        mock_client = Mock()
        mock_serializer.dumps.return_value = b"serialized-value"
        mock_client.eval.side_effect = RedisError("Redis unavailable")

        with self.assertRaises(RedisError):
            RedisAdapter.set_if_owner(
                client=mock_client,
                lock_key="lock:test-key",
                lock_token="test-token",
                cache_key=":1:test-key",
                value={"value": "test"},
                timeout=300,
            )

        mock_serializer.dumps.assert_called_once_with(
            {"value": "test"},
        )

    def test_set_if_owner_returns_false_when_lock_token_does_not_match(self):
        mock_client = Mock()

        mock_client.eval.return_value = 0

        result = RedisAdapter.set_if_owner(
            client=mock_client,
            lock_key="lock:test-key",
            lock_token="test-token",
            cache_key=":1:test-key",
            value={"value": "test"},
            timeout=300,
        )

        self.assertFalse(result)

        mock_client.eval.assert_called_once()


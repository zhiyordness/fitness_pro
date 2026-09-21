from django.core.cache.backends.redis import RedisSerializer
from django.test import TestCase
from django.contrib.auth import get_user_model

from common.services.cache_value_serializer import CacheValueSerializer


User = get_user_model()


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


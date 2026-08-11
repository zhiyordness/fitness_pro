from django.core.cache import cache
from django.http import HttpResponseForbidden
import hashlib
import sys
import logging


logger = logging.getLogger(__name__)

class RateLimitMiddleware:

    RATE_LIMITS = {
        '/accounts/login/': {'limit': 5, 'window': 300, 'reset_on_success': True},
        '/accounts/register/': {'limit': 3, 'window': 300, 'reset_on_success': False},
        '/accounts/password-reset/': {'limit': 3, 'window': 600, 'reset_on_success': False},
        '/accounts/resend-verification/': {'limit': 3, 'window': 300, 'reset_on_success': False},
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def is_test_environment(self):
        return 'test' in sys.argv or 'pytest' in sys.argv[0]

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_cache_key(self, request):
        client_ip = self.get_client_ip(request)
        path = request.path
        key_string = f'ratelimit_{path}_{client_ip}'
        return f'ratelimit_{hashlib.md5(key_string.encode()).hexdigest()}'

    def is_rate_limited(self, request):
        if self.is_test_environment():
            return False

        path = request.path
        if path not in self.RATE_LIMITS:
            return False

        rate_config = self.RATE_LIMITS[path]
        limit = rate_config['limit']
        window = rate_config['window']

        try:
            key = self.get_cache_key(request)
            attempts = cache.get(key, 0)

            if attempts >= limit:
                return True

            if request.method == 'POST':
                cache.set(key, attempts + 1, timeout=window)

        except Exception as e:
            logger.error(f'Rate limit cache error: {e}')
            return False

        return False

    def reset_rate_limit(self, request):
        if self.is_test_environment():
            return

        try:
            path = request.path
            if path in self.RATE_LIMITS:
                key = self.get_cache_key(request)
                cache.delete(key)
        except Exception as e:
            logger.error(f'Rate limit reset error: {e}')

    def __call__(self, request):
        if self.is_test_environment():
            return self.get_response(request)

        try:
            if request.method == 'POST':
                if self.is_rate_limited(request):
                    path = request.path
                    rate_config = self.RATE_LIMITS.get(path, {})
                    limit = rate_config.get('limit', 5)
                    window = rate_config.get('window', 300)
                    minutes = window // 60

                    return HttpResponseForbidden(
                        f'Too many attempts. Maximum {limit} attempts per {minutes} minutes. '
                        f'Please try again later.'
                    )

            response = self.get_response(request)

            if request.path == '/accounts/login/' and response.status_code == 302:
                self.reset_rate_limit(request)

            return response

        except Exception as e:
            logger.error(f'Rate limit middleware error: {e}')
            return self.get_response(request)



from django.test import SimpleTestCase, TestCase


class AdherenceAnalyticsServiceUnitTest(SimpleTestCase):

    def test_get_adherence_overview_counts_completed_workouts(self):
        pass

    def test_get_adherence_overview_counts_cancelled_workouts(self):
        pass

    def test_get_adherence_overview_calculates_total_attempts(self):
        pass

    def test_get_adherence_overview_calculates_completion_rate(self):
        pass

    def test_get_adherence_overview_returns_zero_completion_rate_without_attempts(self):
        pass

    def test_get_adherence_overview_includes_current_streak(self):
        pass

    def test_get_adherence_overview_includes_longest_streak(self):
        pass

    def test_get_adherence_overview_calls_streak_service(self):
        pass


class AdherenceAnalyticsServiceIntegrationTest(TestCase):

    def test_get_adherence_overview_returns_real_adherence_data(self):
        pass

    def test_get_adherence_overview_handles_user_without_workout_attempts(self):
        pass

    def test_get_adherence_overview_ignores_other_users_data(self):
        pass
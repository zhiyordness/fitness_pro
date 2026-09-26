from django.test import SimpleTestCase, TestCase


class TrainingAnalyticsServiceUnitTest(SimpleTestCase):

    def test_get_training_overview_counts_completed_workouts(self):
        pass

    def test_get_training_overview_counts_completed_sets(self):
        pass

    def test_get_training_overview_sums_repetitions(self):
        pass

    def test_get_training_overview_calculates_total_volume(self):
        pass

    def test_get_training_overview_calculates_average_duration(self):
        pass

    def test_get_training_overview_returns_zero_average_duration_without_completed_durations(self):
        pass

    def test_get_training_overview_ignores_incomplete_sets(self):
        pass

    def test_get_training_overview_ignores_incomplete_workouts(self):
        pass

    def test_get_training_overview_is_scoped_to_user(self):
        pass


class TrainingAnalyticsServiceIntegrationTest(TestCase):

    def test_get_training_overview_returns_real_training_data(self):
        pass

    def test_get_training_overview_ignores_other_users_data(self):
        pass

    def test_get_training_overview_handles_user_without_completed_workouts(self):
        pass
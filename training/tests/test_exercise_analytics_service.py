from django.test import SimpleTestCase, TestCase


class ExerciseAnalyticsServiceUnitTest(SimpleTestCase):

    def test_get_exercise_overview_counts_completed_sets(self):
        pass

    def test_get_exercise_overview_sums_repetitions(self):
        pass

    def test_get_exercise_overview_calculates_total_volume(self):
        pass

    def test_get_exercise_overview_calculates_average_weight(self):
        pass

    def test_get_exercise_overview_ignores_zero_weight_for_average_weight(self):
        pass

    def test_get_exercise_overview_calculates_average_repetitions(self):
        pass

    def test_get_exercise_overview_counts_completed_exercise_sessions(self):
        pass

    def test_get_exercise_overview_returns_zero_for_empty_data(self):
        pass

    def test_get_exercise_overview_is_scoped_to_user(self):
        pass

    def test_get_exercise_overview_is_scoped_to_exercise(self):
        pass


class ExerciseAnalyticsServiceIntegrationTest(TestCase):

    def test_get_exercise_overview_returns_real_exercise_data(self):
        pass

    def test_get_exercise_overview_ignores_other_users_data(self):
        pass

    def test_get_exercise_overview_ignores_other_exercises(self):
        pass

    def test_get_exercise_overview_handles_exercise_without_completed_sets(self):
        pass
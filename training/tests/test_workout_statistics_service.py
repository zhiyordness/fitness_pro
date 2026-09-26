from django.test import SimpleTestCase, TestCase


class WorkoutStatisticsServiceUnitTest(SimpleTestCase):

    def test_get_workout_statistics_returns_exercise_count(
            self,
    ):
        pass

    def test_get_workout_statistics_returns_total_sets(
            self,
    ):
        pass

    def test_get_workout_statistics_returns_completed_sets(
            self,
    ):
        pass

    def test_get_workout_statistics_calculates_completion_rate(
            self,
    ):
        pass

    def test_get_workout_statistics_returns_zero_completion_rate_without_sets(
            self,
    ):
        pass

    def test_get_workout_statistics_returns_none_duration_when_not_finished(
            self,
    ):
        pass

    def test_get_workout_statistics_formats_duration_under_one_hour(
            self,
    ):
        pass

    def test_get_workout_statistics_formats_duration_with_hours(
            self,
    ):
        pass


class WorkoutStatisticsServiceIntegrationTest(TestCase):

    def test_get_workout_statistics_calculates_from_real_workout_data(self):
        pass

    def test_get_workout_statistics_handles_real_unfinished_workout(self):
        pass
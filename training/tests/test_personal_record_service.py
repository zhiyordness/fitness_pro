from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import FitnessProUser
from choices import WeekDaysChoices
from training.models import Exercise, TrainingDay, TrainingDayExercise, WorkoutSession, \
    WorkoutSessionExercise, WorkoutSet, PersonalRecord
from training.services import PersonalRecordService
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from datetime import datetime

from django.test import SimpleTestCase

User = get_user_model()


class PersonalRecordServiceUnitTest(SimpleTestCase):

    @patch("training.services.PersonalRecord")
    def test_lower_weight_does_not_update_personal_record(
            self,
            personal_record_model,
    ):
        owner = object()
        exercise = object()

        personal_record = MagicMock()
        personal_record.weight = 100
        personal_record.repetitions = 5

        personal_record_model.objects.filter.return_value.first.return_value = (
            personal_record
        )

        workout_set = SimpleNamespace(
            weight = 95,
            repetitions = 8,
            exercise_session = SimpleNamespace(
                training_day_exercise = SimpleNamespace(
                    exercise=exercise,
                ),
                workout_session = SimpleNamespace(
                    owner=owner,
                ),
            ),
        )

        PersonalRecordService.update_personal_record(
            workout_set
        )

        personal_record.save.assert_not_called()
        personal_record_model.objects.create.assert_not_called()

    @patch("training.services.timezone.now")
    @patch("training.services.PersonalRecord")
    def test_higher_weight_updates_personal_record(
            self,
            mock_personal_record,
            mock_timezone_now,
    ):
        owner = object()
        exercise = object()

        personal_record = MagicMock()
        personal_record.weight = 100
        personal_record.repetitions = 5

        expected_time = datetime(2026, 9, 23, 12, 0, 0)

        mock_personal_record.objects.filter.return_value.first.return_value = (
            personal_record
        )

        workout_set = SimpleNamespace(
            weight=105,
            repetitions=5,
            exercise_session=SimpleNamespace(
                training_day_exercise=SimpleNamespace(
                    exercise=exercise,
                ),
                workout_session=SimpleNamespace(
                    owner=owner,
                ),
            ),
        )

        mock_timezone_now.return_value = expected_time

        PersonalRecordService.update_personal_record(workout_set)

        self.assertEqual(personal_record.weight, 105)
        self.assertEqual(personal_record.repetitions, 5)
        self.assertEqual(personal_record.workout_set, workout_set)
        self.assertEqual(personal_record.achieved_at, expected_time)

        personal_record.save.assert_called_once_with(
            update_fields=[
                "workout_set",
                "weight",
                "repetitions",
                "achieved_at",
            ]
        )
        mock_personal_record.objects.create.assert_not_called()

    @patch("training.services.timezone.now")
    @patch("training.services.PersonalRecord")
    def test_creates_personal_record_when_none_exists(
            self,
            mock_personal_record,
            mock_timezone_now,
    ):
        owner = object()
        exercise = object()
        expected_time = datetime(2026,4,13,13,22,22)

        workout_set = SimpleNamespace(
            weight=80,
            repetitions=10,
            exercise_session=SimpleNamespace(
                training_day_exercise=SimpleNamespace(
                    exercise=exercise,
                ),
                workout_session=SimpleNamespace(
                    owner=owner,
                ),
            ),
        )

        mock_personal_record.objects.filter.return_value.first.return_value = None

        mock_timezone_now.return_value = expected_time

        PersonalRecordService.update_personal_record(workout_set)

        mock_personal_record.objects.create.assert_called_once_with(
            owner=owner,
            exercise=exercise,
            workout_set=workout_set,
            weight=80,
            repetitions=10,
            achieved_at=expected_time,
        )

        mock_personal_record.objects.filter.assert_called_once_with(
            owner=owner,
            exercise=exercise,
        )

    @patch("training.services.PersonalRecord")
    def test_equal_weight_does_not_update_personal_record(
            self,
            mock_personal_record,
    ):
        owner = object()
        exercise = object()

        personal_record = MagicMock()
        personal_record.weight = 100
        personal_record.repetitions = 5

        mock_personal_record.objects.filter.return_value.first.return_value = (
            personal_record
        )

        workout_set = SimpleNamespace(
            weight=100,
            repetitions=5,
            exercise_session=SimpleNamespace(
                training_day_exercise=SimpleNamespace(
                    exercise=exercise,
                ),
                workout_session=SimpleNamespace(
                    owner=owner,
                ),
            ),
        )

        PersonalRecordService.update_personal_record(
            workout_set
        )

        personal_record.save.assert_not_called()
        mock_personal_record.objects.create.assert_not_called()

    @patch("training.services.PersonalRecord")
    def test_personal_record_is_scoped_to_owner(
            self,
            mock_personal_record,
    ):

        owner = object()
        exercise = object()

        personal_record = MagicMock()
        personal_record.weight = 100

        mock_personal_record.objects.filter.return_value.first.return_value = (
            personal_record
        )

        new_workout_set = SimpleNamespace(
            weight=100,
            repetitions=5,
            exercise_session=SimpleNamespace(
                training_day_exercise=SimpleNamespace(
                    exercise=exercise,
                ),
                workout_session=SimpleNamespace(
                    owner=owner,
                ),
            ),
        )

        PersonalRecordService.update_personal_record(new_workout_set)

        mock_personal_record.objects.filter.assert_called_once_with(
            owner=owner,
            exercise=exercise,
        )



class PersonalRecordServiceIntegrationTest(TestCase):

    def test_update_personal_record_with_higher_weight(
            self,
    ):
        user = FitnessProUser.objects.create_user(
            email="test@user.com",
            password="test_password123",
        )

        exercise = Exercise.objects.create(
            name="TestExercise",
            sets=3,
            repetitions=12,
            video_link="https://example.com/bench-press",
        )

        training_day = TrainingDay.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            description="Test-Push-day",
        )

        training_day_exercise = TrainingDayExercise.objects.create(
            training_day=training_day,
            exercise=exercise,
            custom_sets=3,
            custom_repetitions=12,
            order=1,
        )

        workout_session = WorkoutSession.objects.create(
            owner=user,
            training_day=training_day,
        )

        workout_exercise_session = WorkoutSessionExercise.objects.create(
            workout_session=workout_session,
            training_day_exercise=training_day_exercise,
            order=1,
        )

        old_workout_set = WorkoutSet.objects.create(
            exercise_session=workout_exercise_session,
            set_number=2,
            weight=100,
            repetitions=5,
        )

        personal_record = PersonalRecord.objects.create(
            owner=user,
            exercise=exercise,
            workout_set=old_workout_set,
            weight=100,
            repetitions=5,
            achieved_at=datetime.now(),
        )

        new_workout_set = WorkoutSet.objects.create(
            exercise_session=workout_exercise_session,
            set_number=3,
            weight=105,
            repetitions=5,
        )

        PersonalRecordService.update_personal_record(new_workout_set)

        new_personal_record = PersonalRecord.objects.get(
            owner=user,
            exercise=exercise,
        )

        self.assertEqual(new_personal_record.weight, 105)
        self.assertEqual(new_personal_record.repetitions, 5)
        self.assertEqual(new_personal_record.workout_set, new_workout_set)

    def test_create_personal_record_when_none_exists(self):
        user = FitnessProUser.objects.create_user(
            email="test@user.com",
            password="test_password123",
        )

        exercise = Exercise.objects.create(
            name="TestExercise",
            sets=3,
            repetitions=12,
            video_link="https://example.com/bench-press",
        )

        training_day = TrainingDay.objects.create(
            owner=user,
            day=WeekDaysChoices.MONDAY,
            description="Test-Push-day",
        )

        training_day_exercise = TrainingDayExercise.objects.create(
            training_day=training_day,
            exercise=exercise,
            custom_sets=3,
            custom_repetitions=12,
            order=1,
        )

        workout_session = WorkoutSession.objects.create(
            owner=user,
            training_day=training_day,
        )

        workout_exercise_session = WorkoutSessionExercise.objects.create(
            workout_session=workout_session,
            training_day_exercise=training_day_exercise,
            order=1,
        )

        workout_set = WorkoutSet.objects.create(
            exercise_session=workout_exercise_session,
            set_number=3,
            weight=105,
            repetitions=5,
        )

        PersonalRecordService.update_personal_record(workout_set=workout_set)

        personal_record = PersonalRecord.objects.get(
            owner=user,
            exercise=exercise,
        )

        self.assertEqual(personal_record.owner, user)
        self.assertEqual(personal_record.exercise, exercise)
        self.assertEqual(personal_record.workout_set, workout_set)
        self.assertEqual(personal_record.weight, 105)
        self.assertEqual(personal_record.repetitions, 5)




from datetime import datetime
from unittest.mock import patch, Mock, call

from django.test import SimpleTestCase, TestCase

from django.contrib.auth import get_user_model

from choices import WeekDaysChoices, WorkoutSessionStatus
from training.models import TrainingDay, Exercise, TrainingDayExercise, WorkoutSessionExercise, WorkoutSet, \
    WorkoutSession
from training.services import WorkoutSessionService

User = get_user_model()


class WorkoutSessionServiceUnitTest(SimpleTestCase):

    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_returns_existing_active_session(
            self,
            mock_get_active_session,
            mock_create,
    ):
        user = Mock()
        training_day = Mock()
        existing_active_workout_session = Mock()

        mock_get_active_session.return_value = existing_active_workout_session

        result = WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        self.assertEqual(result, existing_active_workout_session)

        mock_get_active_session.assert_called_once_with(
            user=user,
            training_day=training_day,
        )

        mock_create.assert_not_called()


    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_creates_new_session_when_no_active_session_exists(
            self,
            mock_get_active_session,
            mock_create,
            mock_set_create,
            mock_exercise_create,
    ):

        user = Mock()
        training_day = Mock()
        new_created_session = Mock()

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 3
        training_day_exercise_1.custom_repetitions = 10

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 4
        training_day_exercise_2.custom_repetitions = 8

        training_day_exercises = [training_day_exercise_1, training_day_exercise_2]
        training_day.training_day_exercises.all.return_value = training_day_exercises

        mock_get_active_session.return_value = None
        mock_create.return_value = new_created_session

        result = WorkoutSessionService.start_workout(
            user,
            training_day,
        )

        self.assertEqual(result, new_created_session)

        mock_create.assert_called_once_with(
            owner=user,
            training_day=training_day,
        )

        mock_get_active_session.assert_called_once_with(
            user=user,
            training_day=training_day,
        )

    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_creates_exercise_session_for_each_training_day_exercise(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):

        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 3
        training_day_exercise_1.custom_repetitions = 10
        training_day_exercise_1.order = 1

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 4
        training_day_exercise_2.custom_repetitions = 8
        training_day_exercise_2.order = 2

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercises = [training_day_exercise_1, training_day_exercise_2]
        training_day.training_day_exercises.all.return_value = training_day_exercises

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        self.assertEqual(len(mock_wse_create.call_args_list), 2)

        self.assertEqual(
            mock_wse_create.call_args_list,
            [
                call(
                    workout_session=workout_session,
                    training_day_exercise=training_day_exercise_1,
                    order=1,
                ),
                call(
                    workout_session=workout_session,
                    training_day_exercise=training_day_exercise_2,
                    order=2,
                )
            ]
        )

    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_preserves_exercise_order(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):
        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 3
        training_day_exercise_1.custom_repetitions = 10
        training_day_exercise_1.order = 3

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 4
        training_day_exercise_2.custom_repetitions = 8
        training_day_exercise_2.order = 7

        training_day.training_day_exercises.all.return_value = [training_day_exercise_2, training_day_exercise_1]

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        self.assertEqual(
            mock_wse_create.call_args_list,
            [
                call(
                    workout_session=workout_session,
                    training_day_exercise=training_day_exercise_2,
                    order=7,
                ),
                call(
                    workout_session=workout_session,
                    training_day_exercise=training_day_exercise_1,
                    order=3,
                )
            ]
        )


    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_creates_correct_number_of_workout_sets(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):
        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 3
        training_day_exercise_1.custom_repetitions = 10

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 4
        training_day_exercise_2.custom_repetitions = 8

        training_day.training_day_exercises.all.return_value = [training_day_exercise_2, training_day_exercise_1]

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        self.assertEqual(mock_workout_set_create.call_count, 7)


    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_initializes_workout_sets_with_zero_weight(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):
        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 3
        training_day_exercise_1.custom_repetitions = 10

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 4
        training_day_exercise_2.custom_repetitions = 8

        exercise_session = Mock()
        mock_wse_create.return_value = exercise_session

        training_day.training_day_exercises.all.return_value = [training_day_exercise_2, training_day_exercise_1]

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        for call_args, call_kwargs in mock_workout_set_create.call_args_list:
            self.assertEqual(call_kwargs["weight"], 0)


    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_initializes_workout_sets_with_configured_repetitions(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):
        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 2
        training_day_exercise_1.custom_repetitions = 10

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 3
        training_day_exercise_2.custom_repetitions = 8

        exercise_session = Mock()
        mock_wse_create.return_value = exercise_session

        training_day.training_day_exercises.all.return_value = [training_day_exercise_2, training_day_exercise_1]

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        for index, (call_args, call_kwargs) in enumerate(
                mock_workout_set_create.call_args_list
        ):
            if index < training_day_exercise_2.custom_sets:
                self.assertEqual(call_kwargs["repetitions"], 8)
            else:
                self.assertEqual(call_kwargs["repetitions"], 10)


    @patch("training.services.WorkoutSessionExercise.objects.create")
    @patch("training.services.WorkoutSet.objects.create")
    @patch("training.services.WorkoutSession.objects.create")
    @patch("training.services.WorkoutSessionService.get_active_workout_session")
    def test_start_workout_starts_set_number_at_one(
            self,
            mock_get_active_session,
            mock_new_session_create,
            mock_workout_set_create,
            mock_wse_create,
    ):
        user = Mock()
        training_day = Mock()

        mock_get_active_session.return_value = None

        workout_session = Mock()
        workout_session.owner = user
        workout_session.training_day = training_day

        mock_new_session_create.return_value = workout_session

        training_day_exercise_1 = Mock()
        training_day_exercise_1.custom_sets = 2
        training_day_exercise_1.custom_repetitions = 10

        training_day_exercise_2 = Mock()
        training_day_exercise_2.custom_sets = 3
        training_day_exercise_2.custom_repetitions = 8

        exercise_session = Mock()
        mock_wse_create.return_value = exercise_session

        training_day.training_day_exercises.all.return_value = [training_day_exercise_2, training_day_exercise_1]

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        expected_set_numbers = [1, 2, 3, 1, 2]

        for call, expected_set_number in zip(
                mock_workout_set_create.call_args_list,
                expected_set_numbers,
        ):
            self.assertEqual(
                call.kwargs["set_number"],
                expected_set_number,
            )


    @patch("training.services.WorkoutSet.objects.filter")
    def test_has_completed_sets_returns_true_when_completed_set_exists(
            self,
            mock_filter,
    ):

        workout_session = Mock()

        mock_filter.return_value.exists.return_value = True

        result = WorkoutSessionService.has_completed_sets(workout_session)

        self.assertTrue(result)

        mock_filter.assert_called_once_with(
            exercise_session__workout_session=workout_session,
            is_completed=True,
        )

    @patch("training.services.WorkoutSet.objects.filter")
    def test_has_completed_sets_returns_false_when_no_completed_set_exists(
            self,
            mock_filter,
    ):
        workout_session = Mock()

        mock_filter.return_value.exists.return_value = False

        result = WorkoutSessionService.has_completed_sets(workout_session)

        self.assertFalse(result)

        mock_filter.assert_called_once_with(
            exercise_session__workout_session=workout_session,
            is_completed=True,
        )

    @patch("training.services.WorkoutSession.objects.filter")
    def test_get_active_workout_session_returns_latest_started_session(
            self,
            mock_filter,
    ):
        user = Mock()
        training_day = Mock()
        active_workout_session = Mock()

        mock_filter.return_value.order_by.return_value.first.return_value = active_workout_session

        result = WorkoutSessionService.get_active_workout_session(
            user,
            training_day
        )

        self.assertEqual(result, active_workout_session)

        mock_filter.assert_called_once_with(
            owner=user,
            training_day=training_day,
            status=WorkoutSessionStatus.STARTED,
        )

        mock_filter.return_value.order_by.assert_called_once_with(
            "-started_at",
        )

    @patch("training.services.WorkoutSession.objects.filter")
    def test_get_active_workout_session_returns_none_when_no_active_session_exists(
            self,
            mock_filter,
    ):
        user = Mock()
        training_day = Mock()

        mock_filter.return_value.order_by.return_value.first.return_value = None

        result = WorkoutSessionService.get_active_workout_session(
            user,
            training_day
        )

        self.assertIsNone(result)

        mock_filter.assert_called_once_with(
            owner=user,
            training_day=training_day,
            status=WorkoutSessionStatus.STARTED,
        )

        mock_filter.return_value.order_by.assert_called_once_with(
            "-started_at",
        )


    @patch("training.services.timezone.now")
    @patch("training.services.WorkoutSet.objects.filter")
    def test_check_and_finish_workout_completes_when_all_sets_are_completed(
            self,
            mock_set_filter,
            mock_timezone,
    ):
        workout_session = Mock()

        expected_time = datetime(2026,9, 21, 13, 22, 12)
        mock_timezone.return_value = expected_time

        expected_status = WorkoutSessionStatus.COMPLETED

        mock_set_filter.return_value.count.side_effect = [
            3,
            3
        ]

        WorkoutSessionService.check_and_finish_workout(workout_session)

        self.assertEqual(
            workout_session.status,
            expected_status
        )

        self.assertEqual(
            workout_session.finished_at,
            expected_time
        )

        workout_session.save.assert_called_once_with(
            update_fields=[
                'status',
                'finished_at',
            ]
        )


    @patch("training.services.WorkoutSet.objects.filter")
    def test_check_and_finish_workout_does_not_finish_when_some_sets_are_incomplete(
            self,
            mock_set_filter,
    ):
        workout_session = Mock()

        mock_set_filter.return_value.count.side_effect = [
            3,
            2
        ]

        WorkoutSessionService.check_and_finish_workout(workout_session)

        workout_session.save.assert_not_called()


    @patch("training.services.WorkoutSet.objects.filter")
    def test_check_and_finish_workout_does_not_finish_when_no_sets_exist(
            self,
            mock_set_filter,
    ):
        workout_session = Mock()

        mock_set_filter.return_value.count.side_effect = [
            0,
            0
        ]

        WorkoutSessionService.check_and_finish_workout(workout_session)

        workout_session.save.assert_not_called()


class WorkoutSessionServiceIntegrationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@mail.com",
            password="test_password"
        )
        self.training_day = TrainingDay.objects.create(
            owner=self.user,
            day=WeekDaysChoices.MONDAY,
            description="Test_training_day",
        )
        self.exercise_1 = Exercise.objects.create(
            name="Squats",
            sets=3,
            repetitions=8,
            video_link="video_link"
        )
        self.exercise_2 = Exercise.objects.create(
            name="Dumbbell press",
            sets=4,
            repetitions=12,
            video_link="video_link"
        )
        self.training_day_exercise_1 = TrainingDayExercise.objects.create(
            training_day=self.training_day,
            exercise=self.exercise_1,
            custom_sets=3,
            custom_repetitions=8,
            order=1
        )
        self.training_day_exercise_2 = TrainingDayExercise.objects.create(
            training_day=self.training_day,
            exercise=self.exercise_2,
            custom_sets=4,
            custom_repetitions=12,
            order=2
        )

    def test_start_workout_creates_complete_workout_structure(self):

        user = self.user
        training_day = self.training_day

        WorkoutSessionService.start_workout(
            user=user,
            training_day=training_day,
        )

        workout_session = WorkoutSession.objects.get(
            owner=user,
            training_day=training_day,
        )

        workout_session_exercises = WorkoutSessionExercise.objects.filter(
            workout_session=workout_session,
        )

        self.assertEqual(workout_session.owner, user)
        self.assertEqual(workout_session.training_day, training_day)

        self.assertEqual(workout_session_exercises.count(), 2)

        for workout_session_exercise in workout_session_exercises:
            self.assertEqual(
                workout_session_exercise.workout_session,
                workout_session,
            )

        workout_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=workout_session,
        )

        self.assertEqual(workout_sets.count(), 7)


    def test_start_workout_creates_sets_from_different_configurations(self):

        WorkoutSessionService.start_workout(
            user=self.user,
            training_day=self.training_day,
        )

        workout_session = WorkoutSession.objects.get(
            owner=self.user,
            training_day=self.training_day,
        )

        workout_session_exercise_1 = WorkoutSessionExercise.objects.get(
            workout_session=workout_session,
            training_day_exercise=self.training_day_exercise_1
        )

        workout_session_exercise_2 = WorkoutSessionExercise.objects.get(
            workout_session=workout_session,
            training_day_exercise=self.training_day_exercise_2
        )

        self.assertEqual(workout_session_exercise_1.sets.count(), 3)

        self.assertEqual(workout_session_exercise_2.sets.count(), 4)

        sets_wse_1 = workout_session_exercise_1.sets.all()
        sets_wse_2 = workout_session_exercise_2.sets.all()

        for workout_set in sets_wse_1:
            self.assertEqual(workout_set.repetitions, 8)

        for workout_set in sets_wse_2:
            self.assertEqual(workout_set.repetitions, 12)


    def test_start_workout_does_not_create_duplicate_active_session(self):

        first_call = WorkoutSessionService.start_workout(
            user=self.user,
            training_day=self.training_day,
        )

        second_call = WorkoutSessionService.start_workout(
            user=self.user,
            training_day=self.training_day,
        )

        created_sessions = WorkoutSession.objects.filter(
            owner=self.user,
            training_day=self.training_day,
        )

        self.assertEqual(first_call, second_call)
        self.assertEqual(created_sessions.count(), 1)

    def test_get_active_workout_session_returns_real_latest_session(self):

        first_session = WorkoutSession.objects.create(
            owner=self.user,
            training_day=self.training_day,
            started_at=datetime(2026,9,25,16,44,1)
        )

        second_session = WorkoutSession.objects.create(
            owner=self.user,
            training_day=self.training_day,
            started_at=datetime(2026,9,26,13,12,4)
        )

        returned_session = WorkoutSessionService.get_active_workout_session(
            user=self.user,
            training_day=self.training_day,
        )

        self.assertEqual(returned_session, second_session)


    def test_has_completed_sets_returns_real_result(self):

        workout_session = WorkoutSessionService.start_workout(
            user=self.user,
            training_day=self.training_day,
        )

        workout_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=workout_session
        )

        for index, workout_set in enumerate(workout_sets):
            if index == 0:
                workout_set.is_completed = True
                workout_set.save()


        result = WorkoutSessionService.has_completed_sets(
            workout_session=workout_session,
        )

        self.assertTrue(result)


    def test_check_and_finish_workout_updates_real_session(self):

        workout_session = WorkoutSessionService.start_workout(
            user=self.user,
            training_day=self.training_day,
        )

        workout_sets = WorkoutSet.objects.filter(
            exercise_session__workout_session=workout_session
        )

        for workout_set in workout_sets:
            workout_set.is_completed = True
            workout_set.save()

        WorkoutSessionService.check_and_finish_workout(
            workout_session,
        )

        updated_session = WorkoutSession.objects.get(
            pk=workout_session.pk,
        )

        self.assertEqual(
            updated_session.status,
            WorkoutSessionStatus.COMPLETED
        )

        self.assertIsNotNone(updated_session.finished_at)
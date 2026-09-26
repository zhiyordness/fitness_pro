import json
from types import SimpleNamespace

from django.contrib.auth import get_user_model

from django.test import SimpleTestCase, TestCase

from unittest.mock import Mock, patch, call, MagicMock

from choices import WeekDaysChoices
from training.models import MuscleGroup, Muscle, Exercise, TrainingDay, TrainingDayExercise
from training.services import TrainingDayService

User = get_user_model()


class TrainingDayServiceUnitTest(SimpleTestCase):
    @patch("training.services.MuscleGroup.objects.filter")
    @patch("training.services.TrainingDayExercise.objects.create")
    @patch("training.models.Exercise.objects.get")
    def test_configure_training_day_creates_training_day_exercises(
            self,
            mock_get,
            mock_create,
            mock_filter,
    ):
        training_day = Mock()
        exercise_id_list = [101, 202]

        exercise_1 = Mock()
        exercise_1.sets = 3
        exercise_1.repetitions = 10

        exercise_2 = Mock()
        exercise_2.sets = 4
        exercise_2.repetitions = 8

        mock_get.side_effect = [
            exercise_1,
            exercise_2
        ]

        filtered_muscle_groups = Mock()
        mock_filter.return_value = filtered_muscle_groups

        distinct_muscle_groups = Mock()
        filtered_muscle_groups.distinct.return_value = distinct_muscle_groups

        mock_muscle_groups = Mock()
        training_day.muscle_groups = mock_muscle_groups

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )

        self.assertEqual(mock_create.call_count, 2)

        mock_create.assert_any_call(
            training_day=training_day,
            exercise=exercise_1,
            custom_sets=3,
            custom_repetitions=10,
            order=1,
        )

        mock_create.assert_any_call(
            training_day=training_day,
            exercise=exercise_2,
            custom_sets=4,
            custom_repetitions=8,
            order=2,
        )

    @patch("training.services.TrainingDayExercise.objects.create")
    @patch("training.services.Exercise.objects.get")
    def test_configure_training_day_preserves_exercise_order(
            self,
            mock_get,
            mock_create,
    ):
        training_day = Mock()
        exercise_id_list = [101, 202, 303]

        exercise_1 = Mock()
        exercise_1.sets = 3
        exercise_1.repetitions = 10

        exercise_2 = Mock()
        exercise_2.sets = 3
        exercise_2.repetitions = 10

        exercise_3 = Mock()
        exercise_3.sets = 3
        exercise_3.repetitions = 10

        mock_get.side_effect = [
            exercise_1,
            exercise_2,
            exercise_3,
        ]

        TrainingDayService.configure_training_day(
            training_day,
            exercise_id_list,
        )

        mock_create.assert_has_calls(
            [
                call(
                    training_day=training_day,
                    exercise=exercise_1,
                    custom_sets=3,
                    custom_repetitions=10,
                    order=1,
                     ),
                call(
                    training_day=training_day,
                    exercise=exercise_2,
                    custom_sets=3,
                    custom_repetitions=10,
                    order=2,
                ),
                call(
                    training_day=training_day,
                    exercise=exercise_3,
                    custom_sets=3,
                    custom_repetitions=10,
                    order=3,
                ),
            ],
            any_order=False
        )

    @patch("training.services.MuscleGroup.objects.filter")
    @patch("training.services.TrainingDayExercise.objects.create")
    @patch("training.models.Exercise.objects.get")
    def test_configure_training_day_copies_exercise_sets_and_repetitions(
            self,
            mock_get,
            mock_create,
            mock_filter,
    ):
        training_day = Mock()
        exercise_id_list = [101, ]

        exercise_1 = Mock()
        exercise_1.sets = 3
        exercise_1.repetitions = 10

        mock_get.return_value = exercise_1

        filtered_muscle_groups = Mock()
        mock_filter.return_value = filtered_muscle_groups

        distinct_muscle_groups = Mock()
        filtered_muscle_groups.distinct.return_value = distinct_muscle_groups

        mock_muscle_groups = Mock()
        training_day.muscle_groups = mock_muscle_groups

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )

        mock_create.assert_called_once_with(
            training_day=training_day,
            exercise=exercise_1,
            custom_sets=3,
            custom_repetitions=10,
            order=1,
        )

    @patch("training.services.MuscleGroup.objects.filter")
    @patch("training.services.TrainingDayExercise.objects.create")
    @patch("training.models.Exercise.objects.get")
    def test_configure_training_day_assigns_distinct_muscle_groups(
            self,
            mock_get,
            mock_create,
            mock_filter,
    ):
        training_day = Mock()
        exercise_id_list = [101, ]

        exercise_1 = Mock()
        exercise_1.sets = 3
        exercise_1.repetitions = 10

        mock_get.return_value = exercise_1

        distinct_muscle_groups = Mock()

        filtered_muscle_groups = Mock()
        mock_filter.return_value = filtered_muscle_groups

        filtered_muscle_groups.distinct.return_value = distinct_muscle_groups

        TrainingDayService.configure_training_day(
            training_day,
            exercise_id_list,
        )

        filtered_muscle_groups.distinct.assert_called_once_with()

        training_day.muscle_groups.set.assert_called_once_with(
            distinct_muscle_groups,
        )

    @patch("training.services.TrainingDayExercise.objects.filter")
    def test_clear_training_day_deletes_training_day_exercises(
            self,
            mock_filter,
    ):
        training_day = Mock()

        filtered_exercises = Mock()
        mock_filter.return_value = filtered_exercises

        TrainingDayService.clear_training_day(training_day)

        filtered_exercises.delete.assert_called_once_with()

    @patch("training.services.TrainingDayExercise.objects.filter")
    def test_clear_training_day_clears_muscle_groups(
            self,
            mock_filter,
    ):
        training_day = Mock()

        filtered_exercises = Mock()
        mock_filter.return_value = filtered_exercises

        TrainingDayService.clear_training_day(training_day)

        training_day.muscle_groups.clear.assert_called_once()


    def test_swap_exercise_order_swaps_orders(self):

        current_exercise = Mock()
        current_exercise.order = 1

        target_exercise = Mock()
        target_exercise.order = 2

        TrainingDayService.swap_exercise_order(
            current_exercise,
            target_exercise
        )

        self.assertEqual(current_exercise.order, 2)
        self.assertEqual(target_exercise.order, 1)


    def test_swap_exercise_order_saves_both_exercises(self):

        current_exercise = Mock()
        current_exercise.order = 1

        target_exercise = Mock()
        target_exercise.order = 2

        TrainingDayService.swap_exercise_order(
            current_exercise,
            target_exercise
        )

        current_exercise.save.assert_called_once_with()
        target_exercise.save.assert_called_once_with()

    def test_build_exercises_by_muscle_groups_exercises_by_muscle(self):

        training_day = Mock()
        muscle = Mock()
        muscle.name = "Chest"

        exercise = Mock()

        training_day_exercise = SimpleNamespace(
            training_day=training_day,
            exercise=exercise,
            custom_sets=3,
            custom_repetitions=5,
            order=1,
        )

        training_day.training_day_exercises.all.return_value = [training_day_exercise]
        exercise.muscles.all.return_value = [muscle]

        result = TrainingDayService.build_exercises_by_muscle(training_day)

        self.assertEqual(
            result,
            {
                "Chest": [training_day_exercise]
            }
        )


    def test_build_exercises_by_muscle_handles_multiple_muscles(self):
        training_day = Mock()

        muscle_1 = Mock()
        muscle_1.name = "Chest"

        muscle_2 = Mock()
        muscle_2.name = "Back"

        exercise_1 = Mock()
        exercise_1.muscles.all.return_value = [muscle_1]

        exercise_2 = Mock()
        exercise_2.muscles.all.return_value = [muscle_2]

        training_day_exercise_1 = SimpleNamespace(
            training_day=training_day,
            exercise=exercise_1,
            custom_sets=3,
            custom_repetitions=5,
            order=1,
        )

        training_day_exercise_2 = SimpleNamespace(
            training_day=training_day,
            exercise=exercise_2,
            custom_sets=3,
            custom_repetitions=5,
            order=2,
        )

        training_day.training_day_exercises.all.return_value = [
            training_day_exercise_1,
            training_day_exercise_2
        ]

        result = TrainingDayService.build_exercises_by_muscle(training_day)

        self.assertEqual(
            result,
            {
                "Chest": [training_day_exercise_1],
                "Back": [training_day_exercise_2],
            }
        )

    def test_build_muscle_data_builds_expected_structure(self):
        muscle_group = Mock()
        muscle_group.id = 1
        muscle_group.name = "Arms"

        muscle = Mock()
        muscle.id = 2
        muscle.name = "Biceps"

        exercise = Mock()
        exercise.id = 3
        exercise.name = "Chin ups"
        exercise.sets = 3
        exercise.repetitions = 8

        muscle_group.muscles.all.return_value = [muscle]
        muscle.exercises.all.return_value = [exercise]

        result = TrainingDayService.build_muscle_data([muscle_group])

        data = json.loads(result)

        self.assertEqual(
            data,
            {
                "1": {
                    "id": 1,
                    "name": "Arms",
                    "muscles": {
                        "2": {
                            "id": 2,
                            "name": "Biceps",
                            "exercises": {
                                "3": {
                                    "id": 3,
                                    "name": "Chin ups",
                                    "sets": 3,
                                    "repetitions": 8,
                                }
                            },
                        }
                    },
                }
            },
        )

    def test_build_muscle_data_returns_json(self):
        muscle_group = Mock()
        muscle_group.id = 1
        muscle_group.name = "Arms"

        muscle = Mock()
        muscle.id = 2
        muscle.name = "Biceps"

        exercise = Mock()
        exercise.id = 3
        exercise.name = "Chin ups"
        exercise.sets = 3
        exercise.repetitions = 8

        muscle_group.muscles.all.return_value = [muscle]
        muscle.exercises.all.return_value = [exercise]

        result = TrainingDayService.build_muscle_data([muscle_group])

        self.assertIsInstance(result, str)

    def test_build_selected_exercises_builds_expected_structure(self):
        selected_exercise = Mock()
        selected_exercise.id = 3
        selected_exercise.name = "Chin ups"
        selected_exercise.sets = 3
        selected_exercise.repetitions = 8

        group = Mock()
        group.id = 1
        group.name = "Arms"

        muscle = Mock()
        muscle.name = "Biceps"

        group.muscles.all.return_value = [muscle]
        muscle.exercises.all.return_value = [selected_exercise]

        result = TrainingDayService.build_selected_exercises(
            [selected_exercise],
            [group],
        )

        data = json.loads(result)

        self.assertEqual(data,
                         [
                             {
                                 "id": 3,
                                 "name": "Chin ups",
                                 "sets": 3,
                                 "repetitions": 8,
                                 "muscle_name": "Biceps",
                                 "group_name": "Arms",
                             }
                         ]
                         )

    def test_build_selected_exercises_returns_json(self):
        selected_exercise = Mock()
        selected_exercise.id = 3
        selected_exercise.name = "Chin ups"
        selected_exercise.sets = 3
        selected_exercise.repetitions = 8

        group = Mock()
        group.id = 1
        group.name = "Arms"

        muscle = Mock()
        muscle.name = "Biceps"

        group.muscles.all.return_value = [muscle]
        muscle.exercises.all.return_value = [selected_exercise]

        result = TrainingDayService.build_selected_exercises(
            [selected_exercise],
            [group],
        )

        data = json.loads(result)

        self.assertIsInstance(result, str)

    def test_build_selected_exercises_ignores_exercises_not_in_muscle_groups(self):

        selected_exercise = Mock()
        selected_exercise.id = 3
        selected_exercise.name = "Chin ups"
        selected_exercise.sets = 3
        selected_exercise.repetitions = 8

        group = Mock()
        group.id = 1
        group.name = "Arms"

        muscle = Mock()
        muscle.name = "Biceps"

        group.muscles.all.return_value = [muscle]
        muscle.exercises.all.return_value = []

        result = TrainingDayService.build_selected_exercises(
            [selected_exercise],
            [group],
        )

        data = json.loads(result)

        self.assertEqual(data, [])


class TrainingDayServiceIntegrationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test_password"
        )
        self.muscle_group_1 = MuscleGroup.objects.create(
            name="Chest",
        )
        self.muscle_group_2 = MuscleGroup.objects.create(
            name="Back",
        )
        self.muscle_1 = Muscle.objects.create(
            name="Pectoralis Major",
            group=self.muscle_group_1,
        )
        self.muscle_2 = Muscle.objects.create(
            name="Latissimus Dorsi",
            group=self.muscle_group_2,
        )
        self.exercise_1 = Exercise.objects.create(
            name="Bench press",
            sets=3,
            repetitions=8,
            video_link="test_link"
        )
        self.exercise_2 = Exercise.objects.create(
            name="Pull ups",
            sets=4,
            repetitions=8,
            video_link="test_link"
        )
        self.training_day = TrainingDay.objects.create(
            owner=self.user,
            day=WeekDaysChoices.MONDAY,
            description="Test training day",
        )

        self.exercise_1.muscles.add(self.muscle_1)
        self.exercise_2.muscles.add(self.muscle_2)


    def test_configure_training_day_creates_real_relationships(self):

        training_day = self.training_day
        exercise_id_list = [self.exercise_1.id, self.exercise_2.id]

        TrainingDayService.configure_training_day(
            training_day,
            exercise_id_list
        )

        training_day_exercises = TrainingDayExercise.objects.filter(
            training_day=self.training_day,
        )
        self.assertEqual(len(training_day_exercises), 2)

        self.assertEqual(training_day_exercises[0].exercise, self.exercise_1)
        self.assertEqual(training_day_exercises[0].order, 1)

        self.assertEqual(training_day_exercises[1].exercise, self.exercise_2)
        self.assertEqual(training_day_exercises[1].order,2)

        self.assertEqual(training_day_exercises[0].training_day, self.training_day)
        self.assertEqual(training_day_exercises[1].training_day, self.training_day)


    def test_configure_training_day_assigns_real_muscle_groups(self):
        training_day = self.training_day
        exercise_id_list = [self.exercise_1.id, self.exercise_2.id]

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )

        training_day_muscle_groups = training_day.muscle_groups.all()
        self.assertEqual(len(training_day_muscle_groups), 2)

        self.assertIn(self.muscle_group_1, training_day_muscle_groups)
        self.assertIn(self.muscle_group_2, training_day_muscle_groups)


    def test_clear_training_day_removes_real_exercises_and_muscle_groups(self):
        training_day = self.training_day
        exercise_id_list = [self.exercise_1.id, self.exercise_2.id]

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )

        training_day_exercises = TrainingDayExercise.objects.filter(
            training_day=self.training_day,
        )

        training_day_muscle_groups = training_day.muscle_groups.all()

        self.assertEqual(training_day_exercises.count(), 2)
        self.assertEqual(training_day_muscle_groups.count(), 2)

        TrainingDayService.clear_training_day(training_day)

        training_day_exercises = TrainingDayExercise.objects.filter(
            training_day=self.training_day,
        )

        training_day_muscle_groups = training_day.muscle_groups.all()

        self.assertEqual(training_day_exercises.count(), 0)
        self.assertEqual(training_day_muscle_groups.count(), 0)


    def test_swap_exercise_order_persists_new_orders(self):
        training_day = self.training_day
        exercise_id_list = [self.exercise_1.id, self.exercise_2.id]

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )

        training_day_exercises = TrainingDayExercise.objects.filter(
            training_day=self.training_day,
        )

        exercise_a = training_day_exercises[0]
        exercise_b = training_day_exercises[1]

        self.assertEqual(exercise_a.order, 1)
        self.assertEqual(exercise_a.exercise.name, "Bench press")
        self.assertEqual(exercise_b.order, 2)
        self.assertEqual(exercise_b.exercise.name, "Pull ups")

        TrainingDayService.swap_exercise_order(
            exercise_a,
            exercise_b,
        )

        training_day_exercises = TrainingDayExercise.objects.filter(
            training_day=self.training_day,
        )

        exercise_a = training_day_exercises[1]
        exercise_b = training_day_exercises[0]

        self.assertEqual(exercise_a.order, 2)
        self.assertEqual(exercise_a.exercise.name, "Bench press")
        self.assertEqual(exercise_b.order, 1)
        self.assertEqual(exercise_b.exercise.name, "Pull ups")

    def test_build_exercises_by_muscle_returns_real_relationships(self):

        training_day = self.training_day
        exercise_id_list = [self.exercise_1.id, self.exercise_2.id]

        TrainingDayService.configure_training_day(
            training_day=training_day,
            exercise_id_list=exercise_id_list,
        )
        training_day_exercise_1 = TrainingDayExercise.objects.first()
        training_day_exercise_2 = TrainingDayExercise.objects.last()

        result = TrainingDayService.build_exercises_by_muscle(training_day)


        self.assertEqual(result,
                         {'Pectoralis Major': [training_day_exercise_1],
                                'Latissimus Dorsi': [training_day_exercise_2],
                          }
                         )


    def test_build_muscle_data_reads_real_relationships(self):

        muscle_groups = [self.muscle_group_1, self.muscle_group_2]

        result = TrainingDayService.build_muscle_data(muscle_groups)

        self.assertIsInstance(result, str)

        data = json.loads(result)

        self.assertEqual(data,
                         {
                             str(self.muscle_group_1.id): {
                                 "id": self.muscle_group_1.id,
                                 "name": "Chest",
                                 "muscles": {
                                     str(self.muscle_1.id): {
                                         "id": self.muscle_1.id,
                                         "name": "Pectoralis Major",
                                         "exercises": {
                                             str(self.exercise_1.id): {
                                                 "id": self.exercise_1.id,
                                                 "name": "Bench press",
                                                 "sets": 3,
                                                 "repetitions": 8
                                             }
                                         }
                                     }
                                 }
                             },
                             str(self.muscle_group_2.id): {
                                 "id": self.muscle_group_2.id,
                                 "name": "Back",
                                 "muscles": {
                                     str(self.muscle_2.id): {
                                         "id": self.muscle_2.id,
                                         "name": "Latissimus Dorsi",
                                         "exercises": {
                                             str(self.exercise_2.id): {
                                                 "id": self.exercise_2.id,
                                                 "name": "Pull ups",
                                                 "sets": 4,
                                                 "repetitions": 8
                                             }
                                         }
                                     }
                                 }
                             }
                         }
                         )


    def test_build_selected_exercises_reads_real_relationships(self):

        selected_exercises = [self.exercise_1, self.exercise_2]
        muscle_groups = [self.muscle_group_1, self.muscle_group_2]

        result = TrainingDayService.build_selected_exercises(
            selected_exercises,
            muscle_groups
        )

        self.assertIsInstance(result, str)

        data = json.loads(result)

        self.assertIsInstance(data, list)

        self.assertEqual(
            data,
            [
                {
                    'id': self.exercise_1.id,
                    'name': self.exercise_1.name,
                    'sets': self.exercise_1.sets,
                    'repetitions': self.exercise_1.repetitions,
                    'muscle_name': self.muscle_1.name,
                    'group_name': self.muscle_group_1.name
                },
                {
                    'id': self.exercise_2.id,
                    'name': self.exercise_2.name,
                    'sets': self.exercise_2.sets,
                    'repetitions': self.exercise_2.repetitions,
                    'muscle_name': self.muscle_2.name,
                    'group_name': self.muscle_group_2.name
                }
            ]
        )

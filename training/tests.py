from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from training.models import Exercise, Muscle, MuscleGroup

User = get_user_model()


class ExerciseModelTest(TestCase):

    def setUp(self):
        self.muscle_group = MuscleGroup.objects.create(name='Upper Body')
        self.muscle = Muscle.objects.create(
            name='Chest',
            group=self.muscle_group
        )

    def test_create_exercise(self):
        exercise = Exercise.objects.create(
            name='Bench Press',
            sets=3,
            repetitions=10,
            video_link='https://youtube.com/watch?v=123'
        )
        exercise.muscles.add(self.muscle)
        self.assertEqual(exercise.name, 'Bench Press')
        self.assertEqual(exercise.muscles.count(), 1)


class ExercisePublicViewTest(TestCase):

    def setUp(self):
        Exercise.objects.create(
            name='Push-up',
            sets=3,
            repetitions=15,
            video_link='https://example.com'
        )

    def test_exercise_list_public_access(self):
        response = self.client.get(reverse('trainings:exercise-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Push-up')



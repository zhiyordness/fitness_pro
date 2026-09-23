from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from training.models import Exercise

User = get_user_model()



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


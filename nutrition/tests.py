from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from nutrition.models import FoodDatabase, NutritionDay

User = get_user_model()


class FoodDatabaseModelTest(TestCase):

    def test_create_food(self):
        food = FoodDatabase.objects.create(
            name='Apple',
            calories=95,
            protein=0.5,
            carbohydrates=25,
            fat=0.3
        )
        self.assertEqual(food.name, 'Apple')
        self.assertEqual(food.calories, 95)
        self.assertEqual(food.protein, 0.5)
        self.assertEqual(food.carbohydrates, 25)
        self.assertEqual(food.fat, 0.3)


class FoodDatabasePublicViewTest(TestCase):

    def setUp(self):
        FoodDatabase.objects.create(name='Apple', calories=95)
        FoodDatabase.objects.create(name='Banana', calories=105)

    def test_food_list_public_access(self):
        response = self.client.get(reverse('nutrition:food-database-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertContains(response, 'Banana')

    def test_food_search_functionality(self):
        response = self.client.get(
            reverse('nutrition:food-database-list'),
            {'search': 'Apple'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Apple')
        self.assertNotContains(response, 'Banana')


class NutritionDayTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_email_verified = True
        self.user.save()
        self.client.force_login(self.user)

    def test_create_nutrition_day(self):
        response = self.client.post(reverse('nutrition:day-create'), {
            'name': 'Monday'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NutritionDay.objects.filter(
            owner=self.user,
            name='Monday'
        ).exists())

    def test_day_details_requires_authentication(self):
        self.client.logout()
        day = NutritionDay.objects.create(owner=self.user, name='Monday')
        response = self.client.get(reverse('nutrition:day-details',
                                           kwargs={'pk': day.pk}))
        self.assertEqual(response.status_code, 302)



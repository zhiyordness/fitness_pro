from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from nutrition.models import FoodDatabase


class FoodAPITest(APITestCase):

    def setUp(self):
        FoodDatabase.objects.create(
            name='Apple',
            calories=95,
            protein=0.5,
            carbohydrates=25,
            fat=0.3
        )

    def test_food_list_api(self):
        response = self.client.get(reverse('api:foods'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Apple')

    def test_food_search_api(self):
        response = self.client.get(
            reverse('api:food-search'),
            {'q': 'Apple'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


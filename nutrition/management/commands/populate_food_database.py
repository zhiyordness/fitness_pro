from django.core.management.base import BaseCommand
from nutrition.models import FoodDatabase

class Command(BaseCommand):
    help = 'Populates the FoodDatabase with initial food items.'

    def handle(self, *args, **options):
        food_items = [
            {'name': 'Chicken Breast', 'calories': 165, 'protein': 31, 'carbohydrates': 0, 'fat': 3.6},
            {'name': 'Brown Rice', 'calories': 123, 'protein': 2.7, 'carbohydrates': 25.6, 'fat': 0.9},
            {'name': 'Broccoli', 'calories': 55, 'protein': 3.7, 'carbohydrates': 11.2, 'fat': 0.6},
            {'name': 'Salmon', 'calories': 208, 'protein': 20, 'carbohydrates': 0, 'fat': 13},
            {'name': 'Sweet Potato', 'calories': 86, 'protein': 1.6, 'carbohydrates': 20.1, 'fat': 0.1},
            {'name': 'Spinach', 'calories': 23, 'protein': 2.9, 'carbohydrates': 3.6, 'fat': 0.4},
            {'name': 'Eggs', 'calories': 155, 'protein': 13, 'carbohydrates': 1.1, 'fat': 11},
            {'name': 'Oats', 'calories': 389, 'protein': 16.9, 'carbohydrates': 66.3, 'fat': 6.9},
            {'name': 'Greek Yogurt', 'calories': 59, 'protein': 10, 'carbohydrates': 3.6, 'fat': 0.4},
            {'name': 'Almonds', 'calories': 579, 'protein': 21, 'carbohydrates': 21, 'fat': 49},
            {'name': 'Apple', 'calories': 52, 'protein': 0.3, 'carbohydrates': 13.8, 'fat': 0.2},
            {'name': 'Banana', 'calories': 89, 'protein': 1.1, 'carbohydrates': 22.8, 'fat': 0.3},
            {'name': 'Olive Oil', 'calories': 884, 'protein': 0, 'carbohydrates': 0, 'fat': 100},
            {'name': 'Whole Wheat Bread', 'calories': 265, 'protein': 13, 'carbohydrates': 49, 'fat': 3.6},
            {'name': 'Lentils', 'calories': 116, 'protein': 9, 'carbohydrates': 20, 'fat': 0.4},
            {'name': 'Tuna (canned in water)', 'calories': 116, 'protein': 25.5, 'carbohydrates': 0, 'fat': 0.8},
            {'name': 'Avocado', 'calories': 160, 'protein': 2, 'carbohydrates': 9, 'fat': 15},
            {'name': 'Quinoa', 'calories': 120, 'protein': 4.4, 'carbohydrates': 21.3, 'fat': 1.9},
            {'name': 'Cottage Cheese', 'calories': 98, 'protein': 11, 'carbohydrates': 3.4, 'fat': 4.3},
            {'name': 'Blueberries', 'calories': 57, 'protein': 0.7, 'carbohydrates': 14.5, 'fat': 0.3},
        ]

        for item_data in food_items:
            food_item, created = FoodDatabase.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'calories': item_data['calories'],
                    'protein': item_data['protein'],
                    'carbohydrates': item_data['carbohydrates'],
                    'fat': item_data['fat']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added '{food_item.name}' to the FoodDatabase."))
            else:
                self.stdout.write(self.style.WARNING(f"'{food_item.name}' already exists in the FoodDatabase."))

        self.stdout.write(self.style.SUCCESS('FoodDatabase population complete.'))
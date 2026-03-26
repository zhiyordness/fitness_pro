from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        nutrition_group, created = Group.objects.get_or_create(name='Nutrition Editors')
        if created:
            permissions = Permission.objects.filter(
                codename__in=[
                    'add_fooddatabase',
                    'change_fooddatabase',
                    'delete_fooddatabase',
                    'view_fooddatabase',
                ]
            )
            nutrition_group.permissions.add(*permissions)
            self.stdout.write('✅ Nutrition Editors group created')


        exercise_group, created = Group.objects.get_or_create(name='Exercise Editors')
        if created:
            permissions = Permission.objects.filter(
                codename__in=[
                    'add_exercise',
                    'change_exercise',
                    'delete_exercise',
                    'view_exercise',
                ]
            )
            exercise_group.permissions.add(*permissions)
            self.stdout.write('✅ Exercise Editors group created')

        self.stdout.write(self.style.SUCCESS('Groups created successfully!'))


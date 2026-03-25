from rest_framework import serializers
from nutrition.models import FoodDatabase
from training.models import Exercise


class FoodDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodDatabase
        fields = ['id', 'name', 'calories', 'protein', 'carbohydrates', 'fat']


class ExerciseSerializer(serializers.Serializer):
    muscles = serializers.StringRelatedField(many=True)

    class Meta:
        model = Exercise
        fields = ['id', 'name', 'sets', 'repetitions', 'video_link', 'muscles']
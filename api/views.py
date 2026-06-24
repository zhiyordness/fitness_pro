from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from nutrition.models import FoodDatabase
from training.models import Exercise
from training.services import AdherenceAnalyticsService
from .serializers import FoodDatabaseSerializer, ExerciseSerializer, AdherenceAnalyticsSerializer


class FoodDatabaseAPIView(generics.ListAPIView):
    queryset = FoodDatabase.objects.all().order_by('name')
    serializer_class = FoodDatabaseSerializer
    permission_classes = [permissions.AllowAny]


class ExerciseAPIView(generics.ListAPIView):
    queryset = Exercise.objects.all().order_by('name')
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.AllowAny]


class FoodSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        foods = FoodDatabase.objects.filter(name__icontains=query)[:20]
        serializer = FoodDatabaseSerializer(foods, many=True)
        return Response(serializer.data)


class AdherenceAnalyticsAPIView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        analytics = (
            AdherenceAnalyticsService
            .get_adherence_overview(
                request.user
            )
        )

        serializer = (
            AdherenceAnalyticsSerializer(
                analytics
            )
        )

        return Response(
            serializer.data
        )
from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('foods/', views.FoodDatabaseAPIView.as_view(), name='foods'),
    path('exercises/', views.ExerciseAPIView.as_view(), name='exercises'),
    path('foods/search/', views.FoodSearchAPIView.as_view(), name='food-search'),
]


from django.urls import path
from common import views

app_name = "common"

urlpatterns = [
    path('', views.current_training_day_details, name='home'),

]
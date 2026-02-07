from django.urls import path, include

from training import views

app_name = 'training'

urlpatterns = [
    path('', include([
        path('details/', views.split_details, name='details'),
        path('split/', include([
            path('split-create/', views.split_create, name='split-create'),
            path('split-edit/', views.split_edit, name='split-edit'),
            path('split-delete/', views.split_delete, name='split-delete'),
            path('split-add-exercise/', views.exercise_add, name='split-add-exercise'),
        ])),
        path('exercise/', include([
            path('exercise-edit/', views.exercise_edit, name='exercise-edit'),
            path('exercise-delete/', views.exercise_delete, name='exercise-delete'),
            path('exercise-details/', views.exercise_details, name='exercise-details'),
        ])),
    ]))
]

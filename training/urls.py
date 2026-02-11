from django.urls import path, include

from training import views

app_name = 'training'

urlpatterns = [
    path('', include([
        path('list/', views.split_list, name='split-list'),
        path('split/', include([
            path('split-create/', views.split_create, name='split-create'),
            path('<int:pk>/', include([
                path('details/', views.split_details, name='details'),
                path('split-edit/', views.split_edit, name='split-edit'),
                path('split-delete/', views.SplitDeleteView.as_view(), name='split-delete'),
                path('split-add-exercise/', views.ExerciseCreateView.as_view(), name='split-add-exercise'),
            ]))
        ])),
        path('exercise/', include([
            path('<int:pk>/', include([
                path('exercise_edit/', views.exercise_edit, name='exercise-edit'),
                path('exercise_delete/', views.ExerciseDeleteView.as_view(), name='exercise-delete'),
                path('exercise_details/', views.exercise_details, name='exercise-details'),
        ])),
        ])),
    ])),
]

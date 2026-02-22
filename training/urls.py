from django.urls import path, include

from training import views

app_name = 'trainings'

urlpatterns = [
    path('', include([
        path('list/', views.TrainingDayListView.as_view(), name='list'),
        path('training_day/', include([
            path('training_day-create/', views.TrainingDayCreateView.as_view(), name='training-day-create'),
            path('<int:pk>/', include([
                path('details/', views.TrainingDayDetailsView.as_view(), name='details'),
                path('training_day-edit/', views.TrainingDayEditView.as_view(), name='training-day-edit'),
                path('training_day-delete/', views.TrainingDayDeleteView.as_view(), name='training-day-delete'),
                path('training_day-add-exercise/', views.ExerciseCreateView.as_view(), name='training-day-add-exercise'),
            ]))
        ])),
        path('exercise/', include([
            path('list/', views.ExerciseListView.as_view(), name='exercise-list'),
            path('create/', views.ExerciseCreateView.as_view(), name='exercise-create'),
            path('<int:pk>/', include([
                path('exercise_edit/', views.ExerciseEditView.as_view(), name='exercise-edit'),
                path('exercise_delete/', views.ExerciseDeleteView.as_view(), name='exercise-delete'),
                        path('exercise_details/', views.ExerciseDetailsView.as_view(), name='exercise-details'),
                        ])),
                    ])),
                ])),
]

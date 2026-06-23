from django.urls import path, include

from training import views

app_name = 'trainings'

urlpatterns = [
    path('', include([
        path('list/', views.TrainingDayListView.as_view(), name='list'),
        path('training_day/', include([
            path('training_day-create/', views.TrainingDayCreateView.as_view(), name='training-day-create'),
            path('training_day_exercise/<int:pk>/edit/', views.TrainingDayExerciseEditView.as_view(), name='training-day-exercise-edit'),
            path('day-exercise/<int:pk>/move-up/', views.TrainingDayExerciseMoveUpView.as_view(), name='training-day-exercise-move-up'),
            path('day-exercise/<int:pk>/move-down/', views.TrainingDayExerciseMoveDownView.as_view(), name='training-day-exercise-move-down'),

            path('workout-session/', include([
                path('<int:pk>/', views.WorkoutSessionDetailsView.as_view(), name='workout-session-details'),
                path('set/<int:pk>/complete/',views.WorkoutSetCompleteView.as_view(), name='workout-set-complete'),
                path('set/<int:pk>/edit/', views.WorkoutSetEditView.as_view(), name='workout-set-edit'),
                path('<int:pk>/finish/', views.WorkoutSessionFinishView.as_view(), name='workout-session-finish'),
                path('workout-session/<int:pk>/cancel/', views.WorkoutSessionCancelView.as_view(), name='workout-session-cancel'),
            ])),
            path('<int:pk>/', include([
                path('details/', views.TrainingDayDetailsView.as_view(), name='details'),
                path('training_day-edit/', views.TrainingDayEditView.as_view(), name='training-day-edit'),
                path('training_day-delete/', views.TrainingDayDeleteView.as_view(), name='training-day-delete'),
                path('training_day-add-exercise/', views.ExerciseCreateView.as_view(), name='training-day-add-exercise'),
                path('start-workout/', views.WorkoutStartView.as_view(), name='start-workout'),
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

        path('workout-history/', views.WorkoutHistoryView.as_view(), name='workout-history'),
        path('workout-history/<int:pk>/', views.WorkoutHistoryDetailsView.as_view(), name='workout-history-details'),
]



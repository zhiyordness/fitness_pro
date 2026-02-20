from django.urls import path, include

from training import views

app_name = 'training'

urlpatterns = [
    path('', include([
        path('list/', views.TrainingDayListView.as_view(), name='split-list'),
        path('split/', include([
            path('split-create/', views.TrainingDayCreateView.as_view(), name='split-create'),
            path('<int:pk>/', include([
                path('details/', views.TrainingDayDetailsView.as_view(), name='details'),
                path('split-edit/', views.TrainingDayEditView.as_view(), name='split-edit'),
                path('split-delete/', views.SplitDeleteView.as_view(), name='split-delete'),
                path('split-add-exercise/', views.ExerciseCreateView.as_view(), name='split-add-exercise'),
            ]))
        ])),
        path('exercise/', include([
            path('<int:pk>/', include([
                path('exercise_edit/', views.ExerciseEditView.as_view(), name='exercise-edit'),
                path('exercise_delete/', views.ExerciseDeleteView.as_view(), name='exercise-delete'),
                        path('exercise_details/', views.ExerciseDetailsView.as_view(), name='exercise-details'),
                        ])),
                    ])),
                ])),
]

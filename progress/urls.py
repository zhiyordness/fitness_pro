from django.urls import path, include

from progress import views

app_name = 'progress'

urlpatterns = [
    path('', include([
        path('overview/', views.progress_overview, name='overview'),
        path('record/', include([
            path('create/', views.record_create, name='record-create'),
            path('<int:pk>/', include([
                path('', views.record_details, name='record-details'),
                path('edit/', views.record_edit, name='record-edit'),
                path('delete/', views.record_delete, name='record-delete'),
        ])),
    ]))
    ]))
]

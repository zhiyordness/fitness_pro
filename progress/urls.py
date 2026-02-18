from django.urls import path, include

from progress import views

app_name = 'progress'

urlpatterns = [
    path('', include([
        path('overview/', views.progress_overview, name='overview'),
        path('list/', views.RecordListView.as_view(), name='records-list'),
        path('record/', include([
            path('create/', views.RecordCreateView.as_view(), name='record-create'),
            path('<int:pk>/', include([
                path('', views.record_details, name='record-details'),
                path('edit/', views.RecordEditView.as_view(), name='record-edit'),
                path('delete/', views.RecordDeleteView.as_view(), name='record-delete'),

        ])),
    ]))
    ]))
]

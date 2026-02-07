from django.urls import path, include

from nutrition import views

app_name = "nutrition"

urlpatterns = [
    path('', include([
        path('plan/', include([
            path('create/', views.plan_create, name='plan-create'),
            path('<int:pk>/', include([
                path('', views.plan_details, name='plan-details'),
                path('edit/', views.plan_edit, name='plan-edit'),
                path('delete/', views.plan_delete, name='plan-delete'),
            ])),
        ])),
        path('meal/', include([
            path('create/', views.meal_create, name='meal-create'),
            path('<int:pk>/', include([
                path('', views.meal_details, name='meal-details'),
                path('edit/', views.meal_edit, name='meal-edit'),
                path('delete/', views.meal_delete, name='meal-delete'),
            ])),
        ])),

        path('day/', include([
            path('create/', views.day_create, name='day-create'),
            path('<int:pk>/', include([
                path('', views.day_details, name='day-details'),
                path('edit/', views.day_edit, name='day-edit'),
                path('delete/', views.day_delete, name='day-delete'),
            ])),
        ])),
        path('item/', include([
            path('create/', views.item_create, name='item-create'),
            path('<int:pk>/', include([
                path('', views.item_details, name='item-details'),
                path('edit/', views.item_edit, name='item-edit'),
                path('delete/', views.item_delete, name='item-delete'),
            ]))
        ])),
    ])),
]
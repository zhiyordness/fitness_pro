from django.urls import path, include

from nutrition import views

app_name = "nutrition"

urlpatterns = [
    path('nutrition/', views.NutritionHomeView.as_view(), name='nutrition-home'),
    path('', include([
        path('plan/', include([
            path('create/', views.PlanCreateView.as_view(), name='plan-create'),
            path('<int:pk>/', include([
                path('', views.PlanDetailsView.as_view(), name='plan-details'),
                path('edit/', views.PlanEditView.as_view(), name='plan-edit'),
                path('delete/', views.PlanDeleteView.as_view(), name='plan-delete'),
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
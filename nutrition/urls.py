from django.urls import path, include

from nutrition import views

app_name = "nutrition"

urlpatterns = [
    path('nutrition/', views.NutritionHomeView.as_view(), name='nutrition-home'),
    path('', include([
        path('meal/', include([
            path('<int:meal_pk>/item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
            path('<int:pk>/', include([
                path('add-item/', views.ItemAddView.as_view(), name='item-add'),
                path('details/', views.MealDetailsView.as_view(), name='meal-details'),
                path('edit/', views.MealEditView.as_view(), name='meal-edit'),
                path('delete/', views.MealDeleteView.as_view(), name='meal-delete'),
            ])),
        ])),

        path('day/', include([
            path('<int:day_pk>/meal/create/', views.MealCreateView.as_view(), name='meal-create'),
            path('create/', views.DayCreateView.as_view(), name='day-create'),
            path('<int:pk>/', include([
                path('', views.DayDetailsView.as_view(), name='day-details'),
                # path('edit/', views.day_edit, name='day-edit'),
                path('delete/', views.DayDeleteView.as_view(), name='day-delete'),
                path('edit/', views.DayEditView.as_view(), name='day-edit'),
            ])),
        ])),
        path('item/', include([
            path('create/', views.ItemCreateView.as_view(), name='item-create'),
            path('<int:pk>/', include([
                path('', views.item_details, name='item-details'),
                path('edit/', views.item_edit, name='item-edit'),
            ]))
        ])),
    ])),
]
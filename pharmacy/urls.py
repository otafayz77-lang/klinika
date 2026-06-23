from django.urls import path
from . import views
urlpatterns = [
    path('', views.medicine_list, name='medicines'),
    path('add/', views.medicine_add, name='medicine_add'),
    path('<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('income/', views.income_list, name='medicine_income'),
]

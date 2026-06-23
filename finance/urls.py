from django.urls import path
from . import views
urlpatterns = [
    path('kassa/', views.kassa, name='kassa'),
    path('expenses/', views.expense_list, name='expenses'),
]

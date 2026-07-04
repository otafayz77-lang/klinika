from django.urls import path
from . import views
urlpatterns = [
    path('', views.operation_list, name='operations'),
    path('panel/', views.doctor_operations, name='doctor_operations'),
]

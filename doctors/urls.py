from django.urls import path
from . import views
urlpatterns = [
    path('', views.doctor_list, name='doctors'),
    path('add/', views.doctor_add, name='doctor_add'),
    path('<int:pk>/credentials/', views.doctor_credentials, name='doctor_credentials'),
    path('<int:pk>/', views.doctor_detail_admin, name='doctor_detail_admin'),
    path('<int:pk>/reset-password/', views.doctor_reset_password, name='doctor_reset_password'),

    path('panel/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('panel/availability/', views.availability_manage, name='availability_manage'),
    path('panel/availability/<int:pk>/delete/', views.availability_delete, name='availability_delete'),
    path('panel/patients/', views.doctor_patients, name='doctor_patients'),
    path('panel/profile/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('panel/services/', views.doctor_services, name='doctor_services'),
    path('panel/services/<int:pk>/delete/', views.doctor_service_delete, name='doctor_service_delete'),

    # Admin: Barcha shifokorlarning ko'rik xizmatlari (to'liq ko'rinish)
    path('admin/services/', views.doctor_services_admin, name='doctor_services_admin'),
]

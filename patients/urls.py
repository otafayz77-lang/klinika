from django.urls import path
from . import views
urlpatterns = [
    path('', views.patient_list_admin, name='patients'),
    path('<int:pk>/', views.patient_detail_admin, name='patient_detail_admin'),

    path('panel/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('panel/history/', views.patient_history, name='patient_history'),

    path('<int:patient_pk>/treat/', views.treatment_create, name='treatment_create'),
    path('<int:patient_pk>/treat/<int:appointment_pk>/', views.treatment_create, name='treatment_create_from_appt'),

    path('receipt/<int:treatment_pk>/', views.treatment_receipt, name='treatment_receipt'),
]

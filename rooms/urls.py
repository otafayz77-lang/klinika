from django.urls import path
from . import views
urlpatterns = [
    path('wards/', views.ward_list, name='wards'),
    path('admissions/', views.admission_list, name='admissions'),
    path('admissions/<int:pk>/discharge/', views.discharge_patient, name='discharge_patient'),
    path('cabinets/', views.cabinet_list, name='cabinets'),
]

from django.urls import path
from . import views
urlpatterns = [
    path('book/doctors/', views.doctor_list_for_booking, name='doctor_list_for_booking'),
    path('book/<int:doctor_pk>/', views.book_appointment, name='book_appointment'),
    path('cancel/<int:pk>/', views.cancel_appointment, name='cancel_appointment'),
    path('admin/list/', views.appointment_list_admin, name='appointment_list_admin'),
]

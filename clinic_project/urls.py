from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as acc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', acc_views.home_redirect, name='home'),
    path('login/', acc_views.login_view, name='login'),
    path('logout/', acc_views.logout_view, name='logout'),
    path('register/', acc_views.patient_register_view, name='register'),
    path('dashboard/admin/', acc_views.admin_dashboard, name='admin_dashboard'),

    path('staff/', acc_views.staff_list, name='staff_list'),
    path('staff/add/', acc_views.staff_add, name='staff_add'),
    path('staff/<int:pk>/', acc_views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', acc_views.staff_edit, name='staff_edit'),
    path('staff/<int:pk>/pay/', acc_views.staff_pay_salary, name='staff_pay_salary'),
    path('staff/<int:pk>/reset-password/', acc_views.staff_reset_password, name='staff_reset_password'),

    path('doctors/', include('doctors.urls')),
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('rooms/', include('rooms.urls')),
    path('pharmacy/', include('pharmacy.urls')),
    path('finance/', include('finance.urls')),
    path('operations/', include('operations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

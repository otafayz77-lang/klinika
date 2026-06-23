from django.contrib import admin
from .models import Doctor, Specialization, DoctorAvailability, DoctorService

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'phone', 'cabinet', 'is_active']
    search_fields = ['first_name', 'last_name', 'phone']
    list_filter = ['specialization', 'is_active']

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'date']

@admin.register(DoctorService)
class DoctorServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor', 'price', 'is_active']

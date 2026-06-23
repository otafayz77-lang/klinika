from django.contrib import admin
from .models import Ward, PatientAdmission, Cabinet

@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['number', 'floor', 'is_active']

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'ward_type', 'total_beds', 'price_per_day', 'is_active']
    list_filter = ['ward_type', 'is_active']

@admin.register(PatientAdmission)
class PatientAdmissionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'ward', 'doctor', 'status', 'admitted_at']
    list_filter = ['status']

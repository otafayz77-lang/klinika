from django.contrib import admin
from .models import Patient, Treatment, TreatmentItem

class TreatmentItemInline(admin.TabularInline):
    model = TreatmentItem
    extra = 0

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'last_name', 'first_name', 'phone', 'has_booked', 'registered_at']
    search_fields = ['patient_id', 'last_name', 'first_name', 'phone']
    list_filter = ['has_booked', 'gender']

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'total_price', 'created_at']
    inlines = [TreatmentItemInline]

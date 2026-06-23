from django.contrib import admin
from .models import Operation

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['operation_name', 'patient', 'lead_surgeon', 'scheduled_date', 'status']

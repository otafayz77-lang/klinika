from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Staff, SalaryPayment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (('Klinika', {'fields': ('role', 'phone')}),)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'monthly_salary', 'phone', 'is_active']
    list_filter = ['position', 'is_active']

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ['staff', 'amount', 'period', 'paid_at']
    list_filter = ['period']

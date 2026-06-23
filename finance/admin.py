from django.contrib import admin
from .models import CashRegister, Expense

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'description', 'date']
    list_filter = ['transaction_type']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'amount', 'date']

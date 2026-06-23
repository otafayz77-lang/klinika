from django.contrib import admin
from .models import Medicine, MedicineCategory, MedicineIncome

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'sell_price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(MedicineIncome)
class MedicineIncomeAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'quantity', 'purchase_price', 'date']

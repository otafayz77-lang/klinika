from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import role_required
from .models import Medicine, MedicineCategory, MedicineIncome
from finance.models import CashRegister
from finance.views import get_kassa_balance


@login_required
@role_required('admin')
def medicine_list(request):
    q = request.GET.get('q', '')
    medicines = Medicine.objects.filter(is_active=True).select_related('category')
    if q:
        medicines = medicines.filter(Q(name__icontains=q))
    categories = MedicineCategory.objects.all()
    return render(request, 'pharmacy/list.html', {'medicines': medicines, 'q': q, 'categories': categories})


@login_required
@role_required('admin')
def medicine_add(request):
    """Faqat admin narx va miqdor kiritadi."""
    categories = MedicineCategory.objects.all()
    if request.method == 'POST':
        Medicine.objects.create(
            name=request.POST['name'],
            category_id=request.POST.get('category') or None,
            unit=request.POST['unit'],
            sell_price=request.POST['sell_price'],
            stock_quantity=request.POST.get('stock_quantity', 0),
            min_stock=request.POST.get('min_stock', 10),
        )
        messages.success(request, "Mahsulot qo'shildi.")
        return redirect('medicines')
    return render(request, 'pharmacy/form.html', {'categories': categories})


@login_required
@role_required('admin')
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    categories = MedicineCategory.objects.all()
    if request.method == 'POST':
        medicine.name = request.POST['name']
        medicine.category_id = request.POST.get('category') or None
        medicine.unit = request.POST['unit']
        medicine.sell_price = request.POST['sell_price']
        medicine.stock_quantity = request.POST.get('stock_quantity', 0)
        medicine.min_stock = request.POST.get('min_stock', 10)
        medicine.save()
        messages.success(request, "Mahsulot yangilandi.")
        return redirect('medicines')
    return render(request, 'pharmacy/form.html', {'medicine': medicine, 'categories': categories})


@login_required
@role_required('admin')
def income_list(request):
    incomes = MedicineIncome.objects.select_related('medicine').order_by('-date')[:50]
    medicines = Medicine.objects.filter(is_active=True)
    if request.method == 'POST':
        income = MedicineIncome.objects.create(
            medicine_id=request.POST['medicine'],
            quantity=request.POST['quantity'],
            purchase_price=request.POST['purchase_price'],
            supplier=request.POST.get('supplier', ''),
            date=request.POST['date'],
        )

        # KASSA: Dori kelishi avtomatik CHIQIM
        total_cost = int(income.quantity) * int(float(income.purchase_price))

        current_balance = get_kassa_balance()
        if total_cost > current_balance:
            # Agar pul yetmasa → dori kelishini o'chirib tashlaymiz (rollback)
            income.delete()
            messages.error(request, f"Balansda yetarli mablag' yo'q! Joriy balans: {current_balance:,.0f} so'm. Dori kelishi bekor qilindi.")
            return redirect('medicine_income')

        CashRegister.objects.create(
            transaction_type='expense',
            amount=total_cost,
            description=f"Dori kelishi: {income.medicine.name} × {income.quantity} dona",
        )

        messages.success(request, "Kelish qayd etildi, zaxira oshirildi va kassaga chiqim yozildi.")
        return redirect('medicine_income')
    return render(request, 'pharmacy/income.html', {'incomes': incomes, 'medicines': medicines})

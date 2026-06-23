from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date
from accounts.decorators import role_required
from .models import CashRegister, Expense


def get_kassa_balance():
    """Kassadagi jami balansni hisoblaydi (barcha vaqt)"""
    income = CashRegister.objects.filter(transaction_type='income').aggregate(t=Sum('amount'))['t'] or 0
    expense = CashRegister.objects.filter(transaction_type='expense').aggregate(t=Sum('amount'))['t'] or 0
    return income - expense



@login_required
@role_required('admin')
def kassa(request):
    today = date.today()
    entries = CashRegister.objects.select_related('patient').order_by('-date')[:50]
    today_income = CashRegister.objects.filter(transaction_type='income', date__date=today).aggregate(t=Sum('amount'))['t'] or 0
    today_expense = CashRegister.objects.filter(transaction_type='expense', date__date=today).aggregate(t=Sum('amount'))['t'] or 0
    month_income = CashRegister.objects.filter(transaction_type='income', date__date__gte=today.replace(day=1)).aggregate(t=Sum('amount'))['t'] or 0

    if request.method == 'POST':
        tx_type = request.POST['transaction_type']
        amount = int(request.POST['amount'])

        if tx_type == 'expense':
            current_balance = get_kassa_balance()
            if amount > current_balance:
                messages.error(request, f"Balansda yetarli mablag' yo'q! Joriy balans: {current_balance:,.0f} so'm")
                return redirect('kassa')

        CashRegister.objects.create(
            transaction_type=tx_type,
            amount=amount,
            description=request.POST['description'],
        )
        messages.success(request, "Kassa yozuvi qo'shildi.")
        return redirect('kassa')

    current_balance = get_kassa_balance()

    return render(request, 'finance/kassa.html', {
        'entries': entries, 'today_income': today_income, 'today_expense': today_expense,
        'balance': current_balance, 'month_income': month_income,
    })


@login_required
@role_required('admin')
def expense_list(request):
    expenses = Expense.objects.all()
    total = expenses.aggregate(t=Sum('amount'))['t'] or 0
    if request.method == 'POST':
        Expense.objects.create(
            category=request.POST['category'], title=request.POST['title'],
            amount=request.POST['amount'], date=request.POST['date'],
            description=request.POST.get('description', ''),
        )
        messages.success(request, "Xarajat qo'shildi.")
        return redirect('expenses')
    return render(request, 'finance/expenses.html', {'expenses': expenses, 'total': total})

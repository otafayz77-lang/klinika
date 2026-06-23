from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from datetime import date
from accounts.decorators import role_required


def home_redirect(request):
    """Foydalanuvchi rolini tekshirib, to'g'ri dashboardga yo'naltiradi."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'doctor':
        return redirect('doctor_dashboard')
    elif request.user.role == 'patient':
        return redirect('patient_dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'accounts/login.html', {'error': "Login yoki parol noto'g'ri"})
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def patient_register_view(request):
    """Bemor o'zi ro'yxatdan o'tadi — login yaratiladi. Lekin hali 'has_booked=False'."""
    from accounts.models import User
    from patients.models import Patient

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address', '')
        blood_type = request.POST.get('blood_type', '')
        allergies = request.POST.get('allergies', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Bu login allaqachon band. Boshqa login tanlang.'})

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name,
            phone=phone, role='patient'
        )
        Patient.objects.create(
            user=user, first_name=first_name, last_name=last_name,
            gender=gender, birth_date=birth_date, phone=phone,
            address=address, blood_type=blood_type, allergies=allergies,
        )
        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz! Endi shifokor tanlab navbat band qiling.")
        return redirect('patient_dashboard')

    return render(request, 'accounts/register.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')

    from datetime import date
    from django.db.models import Sum
    from doctors.models import Doctor
    from patients.models import Patient, Treatment
    from appointments.models import Appointment
    from finance.models import CashRegister
    from pharmacy.models import Medicine
    from rooms.models import Ward

    today = date.today()
    month_start = today.replace(day=1)

    total_doctors = Doctor.objects.filter(is_active=True).count()
    total_patients = Patient.objects.filter(has_booked=True).count()
    pending_patients = Patient.objects.filter(has_booked=False).count()
    today_appointments = Appointment.objects.filter(availability__date=today, status='booked').count()

    month_income = CashRegister.objects.filter(
        transaction_type='income', date__date__gte=month_start
    ).aggregate(t=Sum('amount'))['t'] or 0
    today_income = CashRegister.objects.filter(
        transaction_type='income', date__date=today
    ).aggregate(t=Sum('amount'))['t'] or 0

    low_stock = Medicine.objects.filter(stock_quantity__lte=10, is_active=True)[:5]
    recent_treatments = Treatment.objects.select_related('patient', 'doctor').order_by('-created_at')[:8]
    wards = Ward.objects.filter(is_active=True)

    return render(request, 'accounts/admin_dashboard.html', {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'pending_patients': pending_patients,
        'today_appointments': today_appointments,
        'month_income': month_income,
        'today_income': today_income,
        'low_stock': low_stock,
        'recent_treatments': recent_treatments,
        'wards': wards,
    })


# ============ ADMIN: Hodimlar (Sozlamalar) ============

@login_required
@role_required('admin')
def staff_list(request):
    from .models import Staff
    staff_members = Staff.objects.filter(is_active=True).select_related('doctor')
    return render(request, 'accounts/staff_list.html', {'staff_members': staff_members})


@login_required
@role_required('admin')
def staff_add(request):
    from .models import Staff
    if request.method == 'POST':
        position = request.POST['position']
        Staff.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            position=position,
            phone=request.POST.get('phone', ''),
            monthly_salary=request.POST.get('monthly_salary', 0),
            hire_date=request.POST.get('hire_date') or None,
        )
        messages.success(request, "Xodim qo'shildi.")
        return redirect('staff_list')
    return render(request, 'accounts/staff_form.html', {})


@login_required
@role_required('admin')
def staff_detail(request, pk):
    from .models import Staff, SalaryPayment
    from datetime import date
    staff = get_object_or_404(Staff, pk=pk)
    payments = staff.salary_payments.all()
    current_period = date.today().strftime('%Y-%m')
    already_paid_this_month = payments.filter(period=current_period).exists()
    return render(request, 'accounts/staff_detail.html', {
        'staff': staff, 'payments': payments,
        'current_period': current_period, 'already_paid_this_month': already_paid_this_month,
    })


@login_required
@role_required('admin')
def staff_edit(request, pk):
    from .models import Staff
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.first_name = request.POST['first_name']
        staff.last_name = request.POST['last_name']
        staff.position = request.POST['position']
        staff.phone = request.POST.get('phone', '')
        staff.monthly_salary = request.POST.get('monthly_salary', 0)
        staff.save()
        messages.success(request, "Xodim ma'lumotlari yangilandi.")
        return redirect('staff_detail', pk=pk)
    return render(request, 'accounts/staff_form.html', {'staff': staff})


@login_required
@role_required('admin')
def staff_pay_salary(request, pk):
    from .models import Staff, SalaryPayment
    from finance.models import Expense, CashRegister
    from finance.views import get_kassa_balance
    from datetime import date

    staff = get_object_or_404(Staff, pk=pk)
    period = date.today().strftime('%Y-%m')

    if SalaryPayment.objects.filter(staff=staff, period=period).exists():
        messages.error(request, f"{staff.full_name}ga bu oy uchun maosh allaqachon to'langan.")
        return redirect('staff_detail', pk=pk)

    current_balance = get_kassa_balance()
    if staff.monthly_salary > current_balance:
        messages.error(request, f"Balansda yetarli mablag' yo'q! Joriy balans: {current_balance:,.0f} so'm. Oylik to'lanmadi.")
        return redirect('staff_detail', pk=pk)

    SalaryPayment.objects.create(staff=staff, amount=staff.monthly_salary, period=period)
    Expense.objects.create(
        category='salary',
        title=f"Oylik maosh: {staff.full_name} ({staff.get_position_display()})",
        amount=staff.monthly_salary,
        date=date.today(),
        description=f"Davr: {period}",
    )

    # KASSA: Oylik to'lovi avtomatik CHIQIM bo'lsin
    CashRegister.objects.create(
        transaction_type='expense',
        amount=staff.monthly_salary,
        description=f"Oylik maosh: {staff.full_name} ({staff.get_position_display()}) — {period}",
    )

    messages.success(request, f"{staff.full_name}ga {staff.monthly_salary:,.0f} so'm maosh to'landi.")
    return redirect('staff_detail', pk=pk)


@login_required
@role_required('admin')
def staff_reset_password(request, pk):
    """Agar xodim shifokor bo'lsa va Doctor profiliga ega bo'lsa, uning parolini tiklash."""
    from .models import Staff
    staff = get_object_or_404(Staff, pk=pk)
    if not staff.doctor:
        messages.error(request, "Bu xodimning kirish profili yo'q.")
        return redirect('staff_detail', pk=pk)
    from doctors.views import generate_password
    new_password = generate_password()
    staff.doctor.user.set_password(new_password)
    staff.doctor.user.save()
    request.session['last_password'] = new_password
    messages.success(request, "Parol tiklandi.")
    return redirect('doctor_credentials', pk=staff.doctor.pk)

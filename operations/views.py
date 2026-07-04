from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Operation
from patients.models import Patient
from doctors.models import Doctor
from finance.models import CashRegister


@login_required
@role_required('admin')
def operation_list(request):
    operations = Operation.objects.select_related('patient', 'lead_surgeon').order_by('-scheduled_date')
    patients = Patient.objects.filter(has_booked=True)
    doctors = Doctor.objects.filter(is_active=True)
    if request.method == 'POST':
        price = int(request.POST.get('price', 0) or 0)
        operation = Operation.objects.create(
            patient_id=request.POST['patient'], lead_surgeon_id=request.POST['lead_surgeon'],
            operation_name=request.POST['operation_name'], operation_room=request.POST['operation_room'],
            scheduled_date=request.POST['scheduled_date'], price=price,
        )
        # KASSA: Operatsiya rejalashtirilganda avtomatik KIRIM
        if price > 0:
            CashRegister.objects.create(
                transaction_type='income',
                amount=price,
                description=f"Operatsiya: {operation.operation_name} — {operation.patient.full_name}",
            )
        messages.success(request, "Operatsiya rejalashtirildi va kassaga kirim qo‘shildi.")
        return redirect('operations')
    return render(request, 'operations/list.html', {
        'operations': operations, 'patients': patients, 'doctors': doctors,
    })


# ============ DOCTOR: O'z operatsiyalari ============

@login_required
@role_required('doctor')
def doctor_operations(request):
    doctor = request.user.doctor_profile
    operations = Operation.objects.filter(
        lead_surgeon=doctor
    ).select_related('patient').order_by('-scheduled_date')

    if request.method == 'POST':
        op_id = request.POST.get('operation_id')
        try:
            op = Operation.objects.get(pk=op_id, lead_surgeon=doctor)
            op.status = 'completed'
            op.save()
            messages.success(request, "Operatsiya yakunlandi.")
        except Operation.DoesNotExist:
            messages.error(request, "Operatsiya topilmadi.")
        return redirect('doctor_operations')

    return render(request, 'operations/doctor_operations.html', {
        'operations': operations
    })

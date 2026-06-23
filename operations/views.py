from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Operation
from patients.models import Patient
from doctors.models import Doctor


@login_required
@role_required('admin')
def operation_list(request):
    operations = Operation.objects.select_related('patient', 'lead_surgeon').order_by('-scheduled_date')
    patients = Patient.objects.filter(has_booked=True)
    doctors = Doctor.objects.filter(is_active=True)
    if request.method == 'POST':
        Operation.objects.create(
            patient_id=request.POST['patient'], lead_surgeon_id=request.POST['lead_surgeon'],
            operation_name=request.POST['operation_name'], operation_room=request.POST['operation_room'],
            scheduled_date=request.POST['scheduled_date'], price=request.POST.get('price', 0),
        )
        messages.success(request, "Operatsiya rejalashtirildi.")
        return redirect('operations')
    return render(request, 'operations/list.html', {
        'operations': operations, 'patients': patients, 'doctors': doctors,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Ward, PatientAdmission, Cabinet
from patients.models import Patient
from doctors.models import Doctor


# ============ PALATA (yotish) — alohida bo'lim ============

@login_required
@role_required('admin')
def ward_list(request):
    wards = Ward.objects.filter(is_active=True)
    if request.method == 'POST':
        Ward.objects.create(
            name=request.POST['name'], number=request.POST['number'],
            ward_type=request.POST['ward_type'], floor=request.POST['floor'],
            total_beds=request.POST['total_beds'], price_per_day=request.POST['price_per_day'],
        )
        messages.success(request, "Palata qo'shildi.")
        return redirect('wards')
    return render(request, 'rooms/wards.html', {'wards': wards})


@login_required
@role_required('admin')
def admission_list(request):
    admissions = PatientAdmission.objects.filter(status='active').select_related('patient', 'ward', 'doctor')
    wards = Ward.objects.filter(is_active=True)
    patients = Patient.objects.filter(has_booked=True)
    doctors = Doctor.objects.filter(is_active=True)
    if request.method == 'POST':
        PatientAdmission.objects.create(
            patient_id=request.POST['patient'], ward_id=request.POST['ward'],
            doctor_id=request.POST['doctor'], bed_number=request.POST.get('bed_number', ''),
            diagnosis=request.POST['diagnosis'],
        )
        messages.success(request, "Bemor palataga yotqizildi.")
        return redirect('admissions')
    return render(request, 'rooms/admissions.html', {
        'admissions': admissions, 'wards': wards, 'patients': patients, 'doctors': doctors,
    })


@login_required
@role_required('admin')
def discharge_patient(request, pk):
    admission = get_object_or_404(PatientAdmission, pk=pk)
    from django.utils import timezone
    admission.status = 'discharged'
    admission.discharged_at = timezone.now()
    admission.save()
    messages.success(request, "Bemor chiqarildi.")
    return redirect('admissions')


# ============ KABINET (qabul xonasi) — butunlay ALOHIDA bo'lim ============

@login_required
@role_required('admin')
def cabinet_list(request):
    cabinets = Cabinet.objects.filter(is_active=True).prefetch_related('doctors')
    if request.method == 'POST':
        Cabinet.objects.create(
            number=request.POST['number'], floor=request.POST['floor'],
            description=request.POST.get('description', ''),
        )
        messages.success(request, "Kabinet qo'shildi.")
        return redirect('cabinets')
    return render(request, 'rooms/cabinets.html', {'cabinets': cabinets})

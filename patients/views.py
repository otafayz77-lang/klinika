from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from accounts.decorators import role_required
from .models import Patient, Treatment, TreatmentItem
from pharmacy.models import Medicine
from finance.models import CashRegister


# ============ ADMIN: Bemorlar ro'yxati (faqat ko'rish, ular o'zi ro'yxatdan o'tadi) ============

@login_required
@role_required('admin')
def patient_list_admin(request):
    """Admin uchun — FAQAT navbat band qilgan (has_booked=True) bemorlar ko'rinadi."""
    q = request.GET.get('q', '')
    patients = Patient.objects.filter(has_booked=True)
    if q:
        from django.db.models import Q
        patients = patients.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(patient_id__icontains=q) | Q(phone__icontains=q)
        )
    pending = Patient.objects.filter(has_booked=False).count()
    return render(request, 'patients/admin_list.html', {'patients': patients, 'q': q, 'pending': pending})


@login_required
@role_required('admin')
def patient_detail_admin(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    treatments = patient.treatments.select_related('doctor').order_by('-created_at')
    appointments = patient.appointments.select_related('doctor', 'availability').order_by('-created_at')[:10]
    return render(request, 'patients/admin_detail.html', {
        'patient': patient, 'treatments': treatments, 'appointments': appointments,
    })


# ============ PATIENT: O'z paneli ============

@login_required
@role_required('patient')
def patient_dashboard(request):
    patient = request.user.patient_profile
    appointments = patient.appointments.select_related('doctor', 'availability').order_by('-created_at')[:10]
    treatments = patient.treatments.select_related('doctor').order_by('-created_at')[:10]
    return render(request, 'patients/dashboard.html', {
        'patient': patient, 'appointments': appointments, 'treatments': treatments,
    })


@login_required
@role_required('patient')
def patient_history(request):
    patient = request.user.patient_profile
    treatments = patient.treatments.select_related('doctor').prefetch_related('used_items__medicine').order_by('-created_at')
    return render(request, 'patients/history.html', {'patient': patient, 'treatments': treatments})


# ============ DOCTOR: Davolash kiritish (narx avtomatik) ============

@login_required
@role_required('doctor')
def treatment_create(request, patient_pk, appointment_pk=None):
    doctor = request.user.doctor_profile
    patient = get_object_or_404(Patient, pk=patient_pk)
    medicines = Medicine.objects.filter(is_active=True, stock_quantity__gt=0)
    services = doctor.services.filter(is_active=True)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        notes = request.POST.get('notes', '')
        medicine_ids = request.POST.getlist('medicine_id')
        quantities = request.POST.getlist('quantity')
        service_id = request.POST.get('extra_service')

        with transaction.atomic():
            treatment = Treatment.objects.create(
                patient=patient, doctor=doctor, diagnosis=diagnosis, notes=notes,
                consultation_price_snapshot=doctor.consultation_price,
            )
            if appointment_pk:
                from appointments.models import Appointment
                appt = Appointment.objects.filter(pk=appointment_pk).first()
                if appt:
                    treatment.appointment = appt
                    appt.status = 'completed'
                    appt.save()

            total = doctor.consultation_price

            if service_id:
                from doctors.models import DoctorService
                service = DoctorService.objects.filter(pk=service_id, doctor=doctor).first()
                if service:
                    treatment.extra_service = service
                    treatment.extra_service_price_snapshot = service.price
                    total += service.price

            for med_id, qty in zip(medicine_ids, quantities):
                if not med_id or not qty:
                    continue
                qty = int(qty)
                med = Medicine.objects.get(pk=med_id)
                if qty > med.stock_quantity:
                    qty = med.stock_quantity
                if qty <= 0:
                    continue
                TreatmentItem.objects.create(
                    treatment=treatment, medicine=med, quantity=qty, unit_price=med.sell_price
                )
                med.stock_quantity -= qty
                med.save(update_fields=['stock_quantity'])
                total += qty * med.sell_price

            treatment.total_price = total
            treatment.save(update_fields=['total_price', 'extra_service', 'extra_service_price_snapshot', 'appointment'])

            # Kassaga avtomatik kirim
            CashRegister.objects.create(
                transaction_type='income',
                amount=total,
                description=f"Davolash: {patient.full_name} — Dr. {doctor.full_name}",
                patient=patient,
                treatment=treatment,
            )

        messages.success(request, f"Davolash yozildi. Jami narx: {total:,.0f} so'm (kassaga qo'shildi)")
        return redirect('doctor_dashboard')

    return render(request, 'patients/treatment_form.html', {
        'patient': patient, 'doctor': doctor, 'medicines': medicines, 'services': services,
    })

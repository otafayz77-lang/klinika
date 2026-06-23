from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from accounts.decorators import role_required
from .models import Appointment
from doctors.models import Doctor, DoctorAvailability


@login_required
@role_required('patient')
def doctor_list_for_booking(request):
    """Bemor shifokorlar ro'yxatini ko'radi (band qilish uchun)."""
    doctors = Doctor.objects.filter(is_active=True).select_related('specialization', 'cabinet')
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})


@login_required
@role_required('patient')
def book_appointment(request, doctor_pk):
    """Bemor doktor tanlab, bo'sh vaqtlardan birini tanlaydi va band qiladi."""
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    patient = request.user.patient_profile
    from datetime import date
    today = date.today()

    available_slots = doctor.availabilities.filter(date__gte=today, is_booked=False).order_by('date', 'start_time')

    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        complaint = request.POST.get('complaint', '')

        slot = DoctorAvailability.objects.filter(pk=slot_id, doctor=doctor).first()

        if not slot:
            messages.error(request, "Vaqt topilmadi.")
            return redirect('book_appointment', doctor_pk=doctor.pk)

        if slot.is_booked:
            # Doktor bemor kiritgan vaqtda vaqti bo'lmasa -> "Vaqt yo'q"
            messages.error(request, "Vaqt yo'q! Bu vaqt allaqachon band qilingan. Boshqa vaqtni tanlang.")
            return redirect('book_appointment', doctor_pk=doctor.pk)

        with transaction.atomic():
            slot.is_booked = True
            slot.save(update_fields=['is_booked'])

            Appointment.objects.create(
                patient=patient, doctor=doctor, availability=slot, complaint=complaint
            )
            if not patient.has_booked:
                patient.has_booked = True
                patient.save(update_fields=['has_booked'])

        messages.success(request, f"Navbat band qilindi! {slot.date} kuni soat {slot.start_time} da Dr. {doctor.full_name} qabulida bo'lasiz.")
        return redirect('patient_dashboard')

    return render(request, 'appointments/book.html', {
        'doctor': doctor, 'slots': available_slots,
    })


@login_required
@role_required('patient')
def cancel_appointment(request, pk):
    patient = request.user.patient_profile
    appt = get_object_or_404(Appointment, pk=pk, patient=patient)
    if appt.status == 'booked':
        appt.status = 'cancelled'
        appt.save()
        appt.availability.is_booked = False
        appt.availability.save(update_fields=['is_booked'])
        messages.success(request, "Navbat bekor qilindi.")
    return redirect('patient_dashboard')


@login_required
@role_required('admin')
def appointment_list_admin(request):
    appointments = Appointment.objects.select_related('patient', 'doctor', 'availability').order_by('-created_at')[:100]
    return render(request, 'appointments/admin_list.html', {'appointments': appointments})

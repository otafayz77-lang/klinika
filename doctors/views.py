from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date
import random
import string

from accounts.decorators import role_required
from accounts.models import User
from .models import Doctor, Specialization, DoctorAvailability, DoctorService
from rooms.models import Cabinet


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_username(first_name, last_name):
    base = f"{first_name}.{last_name}".lower().replace(' ', '')
    base = ''.join(c for c in base if c.isalnum() or c == '.')
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1
    return username


# ============ ADMIN: Doktorlarni boshqarish ============

@login_required
@role_required('admin')
def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related('specialization', 'cabinet', 'user')
    return render(request, 'doctors/admin_list.html', {'doctors': doctors})


@login_required
@role_required('admin')
def doctor_add(request):
    """Admin doktor qo'shadi -> User avtomatik yaratiladi, login/parol generatsiya qilinadi."""
    specializations = Specialization.objects.all()
    cabinets = Cabinet.objects.filter(is_active=True)

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        gender = request.POST['gender']
        spec_id = request.POST.get('specialization')
        experience_years = request.POST.get('experience_years', 0)
        consultation_price = request.POST.get('consultation_price', 0)
        cabinet_id = request.POST.get('cabinet')
        bio = request.POST.get('bio', '')

        username = generate_username(first_name, last_name)
        password = generate_password()

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name,
            phone=phone, role='doctor'
        )
        doctor = Doctor.objects.create(
            user=user, first_name=first_name, last_name=last_name,
            phone=phone, gender=gender,
            specialization_id=spec_id if spec_id else None,
            experience_years=experience_years,
            consultation_price=consultation_price,
            cabinet_id=cabinet_id if cabinet_id else None,
            bio=bio,
        )

        from accounts.models import Staff
        Staff.objects.create(
            first_name=first_name, last_name=last_name, position='doctor',
            phone=phone, doctor=doctor, hire_date=timezone.now().date(),
        )
        if request.FILES.get('photo'):
            doctor.photo = request.FILES['photo']
            doctor.save()

        request.session['last_password'] = password
        messages.success(request, f"Shifokor {doctor.full_name} qo'shildi!")
        return redirect('doctor_credentials', pk=doctor.pk)

    return render(request, 'doctors/admin_form.html', {
        'specializations': specializations, 'cabinets': cabinets,
    })


@login_required
@role_required('admin')
def doctor_credentials(request, pk):
    """Doktor qo'shilgandan keyin login/parolni ko'rsatish uchun (faqat bir marta)."""
    doctor = get_object_or_404(Doctor, pk=pk)
    password = request.session.pop('last_password', None)
    return render(request, 'doctors/credentials.html', {'doctor': doctor, 'password': password})


@login_required
@role_required('admin')
def doctor_detail_admin(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    treatments = doctor.treatments.select_related('patient').order_by('-created_at')[:20]
    return render(request, 'doctors/admin_detail.html', {'doctor': doctor, 'treatments': treatments})


@login_required
@role_required('admin')
def doctor_reset_password(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    new_password = generate_password()
    doctor.user.set_password(new_password)
    doctor.user.save()
    request.session['last_password'] = new_password
    messages.success(request, "Parol tiklandi.")
    return redirect('doctor_credentials', pk=pk)


# ============ DOCTOR: O'z paneli ============

@login_required
@role_required('doctor')
def doctor_dashboard(request):
    doctor = request.user.doctor_profile
    today = date.today()
    today_appointments = doctor.appointments.filter(
        availability__date=today, status='booked'
    ).select_related('patient', 'availability')
    upcoming_slots = doctor.availabilities.filter(date__gte=today, is_booked=False).order_by('date', 'start_time')[:10]
    total_patients = doctor.appointments.values('patient').distinct().count()

    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_slots': upcoming_slots,
        'total_patients': total_patients,
        'today': today,
    }
    return render(request, 'doctors/dashboard.html', context)


@login_required
@role_required('doctor')
def availability_manage(request):
    """Doktor o'zi bo'sh vaqtlarini (sana + boshlanish/tugash) kiritadi."""
    doctor = request.user.doctor_profile
    today = date.today()

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        exists = DoctorAvailability.objects.filter(
            doctor=doctor, date=date_str, start_time=start_time
        ).exists()
        if exists:
            messages.error(request, "Bu sana va vaqt uchun allaqachon slot mavjud.")
        else:
            DoctorAvailability.objects.create(
                doctor=doctor, date=date_str, start_time=start_time, end_time=end_time
            )
            messages.success(request, "Bo'sh vaqt qo'shildi.")
        return redirect('availability_manage')

    slots = doctor.availabilities.filter(date__gte=today).order_by('date', 'start_time')
    return render(request, 'doctors/availability.html', {'doctor': doctor, 'slots': slots, 'today': today})


@login_required
@role_required('doctor')
def availability_delete(request, pk):
    doctor = request.user.doctor_profile
    slot = get_object_or_404(DoctorAvailability, pk=pk, doctor=doctor)
    if not slot.is_booked:
        slot.delete()
        messages.success(request, "Slot o'chirildi.")
    else:
        messages.error(request, "Band qilingan slotni o'chirib bo'lmaydi.")
    return redirect('availability_manage')


@login_required
@role_required('doctor')
def doctor_patients(request):
    """Doktor o'z bemorlarini ko'radi (faqat unga navbat olganlar)."""
    doctor = request.user.doctor_profile
    from patients.models import Patient
    patient_ids = doctor.appointments.values_list('patient_id', flat=True).distinct()
    patients = Patient.objects.filter(id__in=patient_ids)
    return render(request, 'doctors/patients.html', {'patients': patients, 'doctor': doctor})


@login_required
@role_required('doctor')
def doctor_profile_edit(request):
    """
    Doktor o'z profilini ko'radi, lekin FAQAT konsultatsiya narxini tahrirlay oladi.
    Boshqa shaxsiy ma'lumotlar (ism, telefon va h.k.) faqat admin orqali o'zgaradi.
    """
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        new_price = request.POST.get('consultation_price')
        if new_price:
            doctor.consultation_price = new_price
            doctor.save(update_fields=['consultation_price'])
            messages.success(request, "Konsultatsiya narxi yangilandi.")
        return redirect('doctor_profile_edit')
    return render(request, 'doctors/profile_edit.html', {'doctor': doctor})


# ============ DOCTOR: O'z ko'rik xizmatlari (EKG, USG va h.k.) ============

@login_required
@role_required('doctor')
def doctor_services(request):
    doctor = request.user.doctor_profile
    services = doctor.services.filter(is_active=True)
    if request.method == 'POST':
        DoctorService.objects.create(
            doctor=doctor,
            name=request.POST['name'],
            price=request.POST['price'],
        )
        messages.success(request, "Xizmat qo'shildi.")
        return redirect('doctor_services')
    return render(request, 'doctors/services.html', {'doctor': doctor, 'services': services})


@login_required
@role_required('doctor')
def doctor_service_delete(request, pk):
    doctor = request.user.doctor_profile
    service = get_object_or_404(DoctorService, pk=pk, doctor=doctor)
    service.is_active = False
    service.save(update_fields=['is_active'])
    messages.success(request, "Xizmat o'chirildi.")
    return redirect('doctor_services')


# ============ ADMIN: Barcha shifokorlarning Ko'rik xizmatlari (to'liq transparency) ============

@login_required
@role_required('admin')
def doctor_services_admin(request):
    """Admin uchun — BARCHA shifokorlarning qo'shimcha ko'rik xizmatlari ro'yxati.
    Hech qanday yashirish yo'q, hamma narsa ko'rinadi. Admin faollashtirish/o'chirishni boshqaradi.
    """
    services = DoctorService.objects.select_related('doctor').order_by('doctor__last_name', '-id')

    if request.method == 'POST':
        pk = request.POST.get('pk')
        action = request.POST.get('action')
        if pk and action:
            svc = get_object_or_404(DoctorService, pk=pk)
            if action == 'toggle':
                svc.is_active = not svc.is_active
                svc.save(update_fields=['is_active'])
                status = "faollashtirildi" if svc.is_active else "o'chirildi (yashirildi)"
                messages.success(request, f"Xizmat {status}.")
            return redirect('doctor_services_admin')

    return render(request, 'doctors/admin_services.html', {'services': services})

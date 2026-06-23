from django.db import models
from django.conf import settings
import random
import string


def generate_patient_id():
    return 'P' + ''.join(random.choices(string.digits, k=6))


class Patient(models.Model):
    """
    Bemor profili — bemor o'zi ro'yxatdan o'tganda yaratiladi.
    Lekin "bemor qo'shildi" deyilishi uchun u albatta birinchi marta
    biror doktorga navbat band qilishi (Appointment yaratishi) kerak.
    has_booked=False bo'lsa, u faqat ro'yxatdan o'tgan, hali "bemor" emas.
    """
    GENDER_CHOICES = [('M', 'Erkak'), ('F', 'Ayol')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=20, unique=True, default=generate_patient_id, verbose_name="Bemor ID")
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Jinsi")
    birth_date = models.DateField(verbose_name="Tug'ilgan sana")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    address = models.TextField(blank=True, verbose_name="Manzil")
    blood_type = models.CharField(max_length=5, blank=True, verbose_name="Qon guruhi")
    allergies = models.TextField(blank=True, verbose_name="Allergiyalar")

    has_booked = models.BooleanField(default=False, verbose_name="Birinchi navbatni band qilganmi")
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.patient_id})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"


class Treatment(models.Model):
    """Doktor bemorni davolash jarayonida kiritadigan yozuv (tashxis + ishlatilgan dorilar)."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, related_name='treatments')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True, related_name='treatments')
    extra_service = models.ForeignKey('doctors.DoctorService', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Qo'shimcha ko'rik xizmati")
    extra_service_price_snapshot = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Xizmat narxi (saqlangan)")
    diagnosis = models.TextField(verbose_name="Tashxis")
    notes = models.TextField(blank=True, verbose_name="Izoh")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Jami narx")
    created_at = models.DateTimeField(auto_now_add=True)

    def recalc_total(self):
        total = self.consultation_price_snapshot or 0
        for item in self.used_items.all():
            total += item.total_price
        self.total_price = total
        self.save(update_fields=['total_price'])

    consultation_price_snapshot = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Konsultatsiya narxi (saqlangan)")

    def __str__(self):
        return f"{self.patient} — {self.diagnosis[:30]}"

    class Meta:
        verbose_name = "Davolash yozuvi"
        verbose_name_plural = "Davolash yozuvlari"
        ordering = ['-created_at']


class TreatmentItem(models.Model):
    """Davolashda ishlatilgan har bir dori/mahsulot — narx avtomatik hisoblanadi."""
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='used_items')
    medicine = models.ForeignKey('pharmacy.Medicine', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdor")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Birlik narxi (saqlangan)")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.medicine} x{self.quantity}"

    class Meta:
        verbose_name = "Ishlatilgan mahsulot"
        verbose_name_plural = "Ishlatilgan mahsulotlar"

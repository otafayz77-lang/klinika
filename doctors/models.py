from django.db import models
from django.conf import settings


class Specialization(models.Model):
    name = models.CharField(max_length=200, verbose_name="Mutaxassislik")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mutaxassislik"
        verbose_name_plural = "Mutaxassisliklar"


class Doctor(models.Model):
    """
    Doktor profili — Admin qo'shganda 10 ta asosiy maydon to'ldiriladi.
    Qo'shilganda User avtomatik yaratiladi (login + parol).
    """
    GENDER_CHOICES = [('M', 'Erkak'), ('F', 'Ayol')]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')

    # 10 ta asosiy maydon:
    first_name = models.CharField(max_length=100, verbose_name="1. Ism")
    last_name = models.CharField(max_length=100, verbose_name="2. Familiya")
    phone = models.CharField(max_length=20, verbose_name="3. Telefon")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="4. Jinsi")
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True, verbose_name="5. Mutaxassislik")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="6. Ish tajribasi (yil)")
    consultation_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="7. Konsultatsiya narxi")
    cabinet = models.ForeignKey('rooms.Cabinet', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors', verbose_name="8. Kabinet (xona)")
    photo = models.ImageField(upload_to='doctors/', blank=True, verbose_name="9. Rasmi")
    bio = models.TextField(blank=True, verbose_name="10. Qisqacha ma'lumot")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Shifokor"
        verbose_name_plural = "Shifokorlar"


class DoctorAvailability(models.Model):
    """Doktor o'zi kiritadigan bo'sh vaqt oraliqlari (sana + boshlanish/tugash vaqti)."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField(verbose_name="Sana")
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti")
    is_booked = models.BooleanField(default=False, verbose_name="Band qilinganmi")

    def __str__(self):
        status = "Band" if self.is_booked else "Bo'sh"
        return f"{self.doctor} — {self.date} {self.start_time}-{self.end_time} ({status})"

    class Meta:
        verbose_name = "Bo'sh vaqt"
        verbose_name_plural = "Bo'sh vaqtlar"
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time']


class DoctorService(models.Model):
    """Doktor o'zi yaratadigan qo'shimcha ko'rik xizmatlari (EKG, USG va h.k.)."""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Narxi")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.price:,.0f} so'm)"

    class Meta:
        verbose_name = "Ko'rik xizmati"
        verbose_name_plural = "Ko'rik xizmatlari"

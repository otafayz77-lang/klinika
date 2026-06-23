from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Shifokor'),
        ('patient', 'Bemor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'

    @property
    def is_doctor_role(self):
        return self.role == 'doctor'

    @property
    def is_patient_role(self):
        return self.role == 'patient'


class Staff(models.Model):
    """
    Klinikaning barcha xodimlari ro'yxati: Admin, Shifokor, Hamshira, Farrosh va h.k.
    Bu jadval boshqaruv/oylik uchun -- Doctor/User bilan bog'liq emas (login kerak emas).
    Agar xodim shifokor bo'lsa, alohida Doctor profili ham bo'lishi mumkin (kirish uchun);
    lekin Hamshira/Farrosh kabi rollar uchun bu yerda faqat ro'yxat saqlanadi.
    """
    POSITION_CHOICES = [
        ('admin', 'Administrator'),
        ('doctor', 'Shifokor'),
        ('nurse', 'Hamshira'),
        ('cleaner', 'Farrosh'),
        ('other', 'Boshqa xodim'),
    ]
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name="Lavozim")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Oylik maosh")
    doctor = models.OneToOneField('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_record', verbose_name="Bog'liq shifokor profili")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Ishga kirgan sana")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_position_display()})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
        ordering = ['position', 'last_name']


class SalaryPayment(models.Model):
    """Har bir xodimga oylik to'langanda yoziladigan tarix -- avtomatik xarajatga qo'shiladi."""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='salary_payments')
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="To'langan summa")
    period = models.CharField(max_length=20, verbose_name="Davr (oy-yil)")
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff} -- {self.period}: {self.amount:,.0f} so'm"

    class Meta:
        verbose_name = "Maosh to'lovi"
        verbose_name_plural = "Maosh to'lovlari"
        ordering = ['-paid_at']
        unique_together = ['staff', 'period']

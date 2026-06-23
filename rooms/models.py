from django.db import models


class Cabinet(models.Model):
    """Kabinet = doktor QABUL qiladigan xona. Palatadan butunlay ALOHIDA."""
    number = models.CharField(max_length=10, unique=True, verbose_name="Kabinet raqami")
    floor = models.PositiveIntegerField(verbose_name="Qavat")
    description = models.CharField(max_length=200, blank=True, verbose_name="Izoh")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Kabinet {self.number} ({self.floor}-qavat)"

    class Meta:
        verbose_name = "Kabinet (qabul xonasi)"
        verbose_name_plural = "Kabinetlar (qabul xonalari)"
        ordering = ['number']


class Ward(models.Model):
    """Palata = bemor YOTADIGAN joy (kasalxona bo'limi). Kabinetdan butunlay ALOHIDA."""
    WARD_TYPE = [
        ('general', 'Umumiy palata'),
        ('vip', 'VIP palata'),
        ('icu', 'Reanimatsiya'),
        ('surgery', 'Jarrohlikdan keyingi'),
        ('pediatric', 'Bolalar palatasi'),
        ('maternity', "Tug'uruqxona"),
    ]
    name = models.CharField(max_length=100, verbose_name="Palata nomi")
    number = models.CharField(max_length=10, unique=True, verbose_name="Palata raqami")
    ward_type = models.CharField(max_length=20, choices=WARD_TYPE, verbose_name="Turi")
    floor = models.PositiveIntegerField(verbose_name="Qavat")
    total_beds = models.PositiveIntegerField(verbose_name="Jami o'rinlar")
    price_per_day = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Kunlik narx")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Palata {self.number} — {self.name}"

    @property
    def occupied_beds(self):
        return self.admissions.filter(status='active').count()

    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds

    class Meta:
        verbose_name = "Palata (yotish bo'limi)"
        verbose_name_plural = "Palatalar (yotish bo'limi)"
        ordering = ['number']


class PatientAdmission(models.Model):
    STATUS = [('active', 'Yotmoqda'), ('discharged', 'Chiqarilgan')]
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='admissions')
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='admissions')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True)
    bed_number = models.CharField(max_length=10, blank=True, verbose_name="O'rin raqami")
    admitted_at = models.DateTimeField(auto_now_add=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    diagnosis = models.TextField(verbose_name="Tashxis")

    def __str__(self):
        return f"{self.patient} — {self.ward}"

    @property
    def days_admitted(self):
        from django.utils import timezone
        end = self.discharged_at or timezone.now()
        return (end - self.admitted_at).days + 1

    class Meta:
        verbose_name = "Bemor yotishi"
        verbose_name_plural = "Bemor yotishlari"
